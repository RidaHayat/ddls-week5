#!/usr/bin/env python3
"""Reproducible QC and marker summaries for the supplied PBMC AnnData."""
from pathlib import Path
import argparse
import warnings

import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse


def matrix_column(matrix, index):
    col = matrix[:, index]
    return np.asarray(col.toarray() if sparse.issparse(col) else col).ravel()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/pbmc3k.h5ad")
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()
    ad = sc.read_h5ad(args.data)
    print(f"Shape: {ad.n_obs} cells x {ad.n_vars} genes")
    print(f"Layers: {list(ad.layers.keys())}; obsm: {list(ad.obsm.keys())}")
    print(f"obs columns: {list(ad.obs.columns)}")
    print("Missing values by obs field:")
    print(ad.obs.isna().sum().to_string())
    labels = ad.obs["leiden"].astype(str)
    print("\nCluster sizes:")
    print(labels.value_counts().sort_index(key=lambda ix: ix.astype(int)).to_string())
    qc_cols = [c for c in ["n_genes", "total_counts", "pct_mito"] if c in ad.obs]
    print("\nQC median [min, max] by cluster:")
    grouped = ad.obs.assign(cluster=labels).groupby("cluster", observed=True)[qc_cols]
    print(grouped.agg(["median", "min", "max"]).round(2).to_string())

    print("\nPer-cluster top ranked genes (Wilcoxon; existing clusters, normalized X):")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sc.tl.rank_genes_groups(ad, groupby="leiden", method="wilcoxon", use_raw=False, n_genes=args.top_n)
    result = ad.uns["rank_genes_groups"]
    for cluster in sorted(labels.unique(), key=int):
        print(f"{cluster}: " + ", ".join(map(str, result["names"][cluster][:args.top_n])))

    print("\nCluster 6 selected marker detection (positive raw UMI; n/13 and detected-cell counts):")
    marker_sets = {
        "platelet": ["PPBP", "PF4", "GP9", "ITGA2B", "NRGN", "GNG11", "TUBB1"],
        "T/NK": ["CD3D", "CD3E", "TRAC", "NKG7", "GNLY"],
        "B": ["MS4A1", "CD79A", "CD74"],
        "monocyte": ["LYZ", "S100A8", "S100A9", "FCGR3A", "LST1"],
        "erythroid": ["HBB", "HBA1"],
        "pan-leukocyte": ["PTPRC"],
    }
    cluster_mask = labels.to_numpy() == "6"
    cluster_indices = np.flatnonzero(cluster_mask)
    for lineage, genes in marker_sets.items():
        pieces = []
        for gene in genes:
            loc = ad.var_names.get_indexer([gene])[0]
            if loc < 0:
                continue
            counts = matrix_column(ad.layers["counts"], loc)[cluster_indices]
            positive = int((counts > 0).sum())
            pieces.append(f"{gene} {positive}/{len(cluster_indices)} (UMI sum {counts.sum():.0f})")
        print(f"{lineage}: " + ("; ".join(pieces) if pieces else "not in feature matrix"))

    print("\nCluster 6 per-cell raw count marker panel (positive genes):")
    panel = sorted({g for genes in marker_sets.values() for g in genes if g in ad.var_names})
    for cell_i in cluster_indices:
        cell = str(ad.obs_names[cell_i])
        positives = []
        for gene in panel:
            gi = ad.var_names.get_loc(gene)
            value = matrix_column(ad.layers["counts"][cell_i:cell_i+1], gi)[0]
            if value > 0:
                positives.append(f"{gene}:{int(value)}")
        qc = ", ".join(f"{col}={ad.obs.iloc[cell_i][col]}" for col in qc_cols)
        print(f"{cell} ({qc}) | " + (", ".join(positives) if positives else "none from panel"))

    print("\nCluster 6 normalized mean expression by cluster for lineage panel:")
    genes = [g for values in marker_sets.values() for g in values if g in ad.var_names]
    for gene in genes:
        gi = ad.var_names.get_loc(gene)
        x = ad.X[:, gi]
        x = np.asarray(x.toarray() if sparse.issparse(x) else x).ravel()
        means = pd.Series(x).groupby(labels.to_numpy()).mean()
        print(f"{gene}: c6={means.get('6', np.nan):.3f}; others max={means.drop('6').max():.3f}")


if __name__ == "__main__":
    main()
