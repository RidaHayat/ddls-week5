from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock
from typing import Any, Optional

import numpy as np
import scanpy as sc
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from plotly import express as px
from plotly.utils import PlotlyJSONEncoder

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = Path(os.getenv("PBMC_DATA", BASE_DIR / "data" / "pbmc3k.h5ad"))

app = FastAPI(title="PBMC Single-Cell Navigator", version="1.0.0")
_data_lock = Lock()
_AD = None


def get_data():
    """Read the source file once per process and reuse its AnnData object."""
    global _AD
    if _AD is None:
        with _data_lock:
            if _AD is None:
                if not DATA_PATH.is_file():
                    raise RuntimeError(f"Dataset not found: {DATA_PATH}")
                ad = sc.read_h5ad(DATA_PATH)
                required = {"leiden"}
                missing = required.difference(ad.obs.columns)
                if missing or "X_umap" not in ad.obsm:
                    raise RuntimeError("Dataset is missing required cluster labels or precomputed UMAP")
                _AD = ad
    return _AD


def _json_value(value: Any):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.generic):
        return value.item()
    return value


def _result_group_values(result: dict[str, Any], field: str, cluster: str):
    """Read one group's values from Scanpy's structured recarray result."""
    values = result.get(field)
    if values is None:
        return None
    # Scanpy stores each field as a structured array with group names as dtype fields.
    # Handle mapping-style results too for compatibility with serialized/older outputs.
    if getattr(getattr(values, "dtype", None), "names", None):
        if cluster not in values.dtype.names:
            return None
        return values[cluster]
    if isinstance(values, dict):
        return values.get(cluster)
    return None


def _markers_are_compatible(result: Any, groups: set[str], n_genes: int) -> bool:
    """Check that stored marker results cover every actual group and gene."""
    if not isinstance(result, dict):
        return False
    for field in ("names", "scores", "pvals", "pvals_adj", "logfoldchanges"):
        values = result.get(field)
        fields = getattr(getattr(values, "dtype", None), "names", None)
        if fields:
            if not groups.issubset(fields) or len(values) != n_genes:
                return False
        elif isinstance(values, dict):
            if not groups.issubset(values) or any(len(values[g]) != n_genes for g in groups):
                return False
        else:
            return False
    return True


def _plot_data(color: str):
    ad = get_data()
    coords = np.asarray(ad.obsm["X_umap"])
    if coords.ndim != 2 or coords.shape[1] < 2:
        raise HTTPException(500, "Precomputed UMAP coordinates are not valid 2-D coordinates")
    frame = {"UMAP 1": coords[:, 0], "UMAP 2": coords[:, 1], "cluster": ad.obs["leiden"].astype(str).to_numpy()}
    if color == "cluster":
        frame["color"] = frame["cluster"]
        color_kind = "categorical"
    elif color in ad.obs.columns:
        vals = ad.obs[color]
        if not np.issubdtype(vals.dtype, np.number):
            raise HTTPException(400, f"'{color}' is not a numeric quality metric")
        frame["color"] = np.asarray(vals, dtype=float)
        color_kind = "continuous"
    else:
        gene_idx = ad.var_names.get_indexer([color])
        if gene_idx[0] < 0:
            raise HTTPException(404, f"Unknown gene or color field: {color}")
        expr = ad[:, gene_idx[0]].X
        if hasattr(expr, "toarray"):
            expr = expr.toarray()
        frame["color"] = np.asarray(expr).ravel().astype(float)
        color_kind = "continuous"
    return frame, color_kind


def _figure(color: str):
    frame, kind = _plot_data(color)
    fig = px.scatter(
        frame, x="UMAP 1", y="UMAP 2", color="color",
        hover_data={"cluster": True, "UMAP 1": False, "UMAP 2": False},
        color_continuous_scale="Viridis" if kind == "continuous" else None,
        category_orders={"color": sorted(set(frame["color"]))} if kind == "categorical" else None,
        labels={"color": color}, render_mode="webgl",
    )
    fig.update_traces(marker={"size": 7, "opacity": 0.85})
    fig.update_layout(template="plotly_white", margin={"l": 12, "r": 12, "t": 24, "b": 12}, legend_title_text=color)
    return fig


@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")


@app.get("/api/umap")
def umap(color: str = Query("cluster", min_length=1, max_length=100)):
    """Serve precomputed UMAP coordinates plus the Plotly figure for requested color."""
    ad = get_data()
    frame, kind = _plot_data(color)
    return {
        "color": color,
        "color_label": "cluster" if color == "cluster" else color,
        "color_kind": kind,
        "points": [
            {"x": float(frame["UMAP 1"][i]), "y": float(frame["UMAP 2"][i]), "cluster": str(frame["cluster"][i]), "value": _json_value(frame["color"][i])}
            for i in range(ad.n_obs)
        ],
        "figure": json.loads(json.dumps(_figure(color).to_plotly_json(), cls=PlotlyJSONEncoder)),
    }


@app.get("/api/expression/{gene}")
def gene_expression(gene: str):
    ad = get_data()
    idx = ad.var_names.get_indexer([gene])
    if idx[0] < 0:
        raise HTTPException(404, f"Unknown gene: {gene}")
    matrix = ad[:, idx[0]].X
    if hasattr(matrix, "toarray"):
        matrix = matrix.toarray()
    values = np.asarray(matrix).ravel()
    return {"gene": gene, "n_cells": int(ad.n_obs), "n_expressing": int(np.count_nonzero(values > 0)), "points": [
        {"cell": str(ad.obs_names[i]), "cluster": str(ad.obs["leiden"].iloc[i]), "expression": float(values[i]), "x": float(ad.obsm["X_umap"][i, 0]), "y": float(ad.obsm["X_umap"][i, 1])}
        for i in range(ad.n_obs)
    ]}


@app.get("/api/markers/{cluster}")
def cluster_markers(cluster: str, top_n: int = Query(10, ge=1, le=50)):
    if not cluster.isdigit():
        raise HTTPException(404, f"Unknown cluster: {cluster}")
    ad = get_data()
    labels = ad.obs["leiden"].astype(str)
    if cluster not in set(labels):
        raise HTTPException(404, f"Unknown cluster: {cluster}")
    key = "navigator_rank_genes_groups"
    if key not in ad.uns:
        with _data_lock:
            if key not in ad.uns:
                sc.tl.rank_genes_groups(ad, groupby="leiden", method="wilcoxon", use_raw=False, key_added=key)
    try:
        df = sc.get.rank_genes_groups_df(ad, group=cluster, key=key).head(top_n)
    except Exception as exc:
        raise HTTPException(500, f"Could not read marker results for group '{cluster}': {exc}")
    genes = [
        {
            "gene": str(row["names"]),
            "score": _json_value(row.get("scores")),
            "p_value": _json_value(row.get("pvals")),
            "adjusted_p_value": _json_value(row.get("pvals_adj")),
            "log_fold_change": _json_value(row.get("logfoldchanges")),
        }
        for row in df.to_dict("records")
    ]
    return {"cluster": cluster, "n_cells": int((labels == cluster).sum()), "top_n": top_n, "markers": genes}


@app.get("/api/quality")
def quality(cluster: Optional[str] = None):
    if cluster is not None and not cluster.isdigit():
        raise HTTPException(404, f"Unknown cluster: {cluster}")
    ad = get_data()
    labels = ad.obs["leiden"].astype(str)
    if cluster is not None and cluster not in set(labels):
        raise HTTPException(404, f"Unknown cluster: {cluster}")
    metrics = [name for name in ("n_genes", "total_counts", "pct_mito") if name in ad.obs.columns]
    if not metrics:
        raise HTTPException(500, "No supported quality metrics found in dataset")
    groups = [cluster] if cluster else sorted(labels.unique(), key=lambda item: int(item) if item.isdigit() else item)
    summaries = []
    for group in groups:
        mask = labels.to_numpy() == group
        row = {"cluster": group, "n_cells": int(mask.sum()), "metrics": {}}
        for metric in metrics:
            vals = np.asarray(ad.obs.loc[mask, metric], dtype=float)
            vals = vals[np.isfinite(vals)]
            row["metrics"][metric] = {
                "n_valid": int(vals.size), "missing": int(mask.sum() - vals.size),
                "mean": _json_value(np.mean(vals)) if vals.size else None,
                "median": _json_value(np.median(vals)) if vals.size else None,
                "min": _json_value(np.min(vals)) if vals.size else None,
                "max": _json_value(np.max(vals)) if vals.size else None,
            }
        summaries.append(row)
    return {"metrics": metrics, "summaries": summaries}


@app.get("/api/genes")
def genes(q: str = Query("", max_length=100), limit: int = Query(20, ge=1, le=100)):
    ad = get_data()
    query = q.strip().upper()
    found = [str(gene) for gene in ad.var_names if query in str(gene).upper()]
    return {"genes": found[:limit], "total_matches": len(found)}


@app.get("/api/clusters")
def clusters():
    ad = get_data()
    counts = ad.obs["leiden"].astype(str).value_counts().sort_index(key=lambda ix: ix.map(lambda x: int(x) if x.isdigit() else x))
    return {"clusters": [{"cluster": str(key), "n_cells": int(value)} for key, value in counts.items()]}


@app.get("/api/plot/{color}")
def plot(color: str):
    return json.loads(json.dumps(_figure(color).to_plotly_json(), cls=PlotlyJSONEncoder))


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
