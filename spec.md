# Analysis specification: PBMC cluster 6 assessment

## Decision
Determine whether cluster 6 (13 cells) should be retained as a biologically meaningful population, excluded as low-quality/artefactual, or set aside from the figure pending validation. The decision must be supportable to a non-computational immunologist and co-author.

## Inputs
- `data/pbmc3k.h5ad`
- `data/ABOUT_THIS_FILE.txt`
- `ddls-week5-interview.md`

## Questions to answer
1. What are clusters 0–7 most plausibly representing based on cluster marker genes?
2. Does cluster 6 show coherent platelet-associated expression (including `PPBP`, `PF4`, `GP9`, `ITGA2B` where present), and how consistently across its 13 cells?
3. Does it also show substantial markers of other blood-cell lineages that could indicate doublets or contamination?
4. Are its low gene count and other QC measurements consistent with the proposed identity, and how does it compare with other clusters?
5. What do the observed data support, what remains unknown, and what is the practical figure recommendation?

## Required methods and outputs
- Load the file with Scanpy/AnnData, verify dimensions, layers, available `obs` fields, cluster sizes, missing values, and reported cluster 6 metrics.
- Rank per-cluster marker genes (e.g. Scanpy `rank_genes_groups`) using the existing cluster labels; inspect top markers and relevant canonical lineage markers.
- Summarize cluster 6 expression using normalized expression and, if useful, raw counts/detection fractions. Include comparisons to other clusters and per-cell evidence rather than relying only on cluster averages.
- Compare `n_genes`, `total_counts`, and `pct_mito` across clusters. Do not equate low complexity by itself with empty droplets or dead cells.
- Use the existing UMAP only as visualization, not as independent biological proof.
- Provide a brief conclusion with recommendation (keep / remove / set aside), evidence, uncertainty, and validation steps (facility QC/filtering history, doublet assessment, and sample provenance).

## Interpretation safeguards
- Cluster labels are numeric and are not cell identities.
- Marker association supports an annotation but does not prove cell identity or exclude technical artefacts.
- Platelets are naturally small, anucleate, and RNA-poor; low detected genes may be compatible with platelet-associated material/cells. Avoid overclaiming intact platelet identity from a PBMC scRNA-seq matrix.
- Facility filtering, empty-droplet handling, missingness, and doublet calls are not documented in the interview; report only what the supplied file can establish.
- Do not modify the input `.h5ad` or recompute clustering/UMAP.

## Final deliverable
A concise analysis report, including a co-author-ready keep-or-set-aside rationale, key marker/QC findings, limitations, and reproducible code or commands.
