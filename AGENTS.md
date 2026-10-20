# Analyst instructions — DDLS Week 5

## Goal
Analyze `data/pbmc3k.h5ad` to identify clusters 0–7 and give Dr. Ravi Menon an evidence-based keep-or-set-aside recommendation for cluster 6. Treat `ddls-week5-interview.md` as the raw interview source and `data/ABOUT_THIS_FILE.txt` as the dataset guide.

## Dataset contract
- 2,700 human PBMC cells; precomputed cluster labels are `ad.obs["leiden"]` (numeric strings 0–7).
- `ad.X`: log-normalized expression; use for expression plots/marker review.
- `ad.layers["counts"]`: raw UMI counts.
- `ad.var_names`: gene symbols.
- `ad.obs`: `n_genes`, `total_counts`, `pct_mito` quality fields.
- `ad.obsm["X_umap"]`: precomputed visualization coordinates. Do not recompute clusters or UMAP.
- The provided summary says cluster 6 has 13 cells, ~350 genes/cell, and 1.6% mitochondrial reads. Independently verify these against the file.

## Analysis requirements
1. Inspect the AnnData structure, metadata, cluster sizes, missingness, and quality distributions; report any limitations and do not assume facility filtering or doublet status is known.
2. Rank marker genes per cluster and inspect cluster 6 expression, prioritizing platelet markers (e.g. `PPBP`, `PF4`, `GP9`, `ITGA2B`) alongside competing leukocyte lineage markers. State the evidence, including per-cell consistency where feasible; distinguish RNA expression from inferred cell identity.
3. Compare cluster 6 quality metrics with other clusters. Low gene counts alone are not sufficient to label cells as junk; consider that platelets are naturally small/anucleate and RNA-poor.
4. Check for evidence of mixed-lineage/doublet-like expression and identify what cannot be concluded without raw facility QC, doublet calls, or sample provenance.
5. Deliver a concise, actionable recommendation for the figure (keep, remove, or set aside pending validation), with a short co-author-ready rationale and caveats. Avoid claiming certainty unsupported by the data.

## Reproducibility
Use the supplied file and existing cluster/map annotations. Include commands or a script/notebook for key summaries and marker evidence so the result can be reproduced. Do not alter source data.
