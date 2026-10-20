# PBMC Single-Cell Navigator — DDLS Week 5

A small FastAPI and Plotly web app for interactively exploring the supplied PBMC single-cell RNA-seq dataset. It uses the dataset's existing Leiden cluster labels and precomputed UMAP coordinates; it does **not** recompute the clustering or embedding.

## The owner's question and recommendation

Dr. Ravi Menon was concerned that Cluster 6, a small group with low gene counts, might be dead cells or empty droplets and asked whether it was safe to remove it from a figure. The existing analysis instead finds a consistent **platelet-associated RNA signature**: raw-count detection includes `PF4` and `PPBP` in all 13 cells, `GP9` in 12/13, and `ITGA2B` in 11/13. Cluster 6 has median `n_genes` 350 (range 212–2,455), median `total_counts` 917 (568–8,931), and median `pct_mito` 1.57% (0.68–3.22%). These observations do not prove that the cells are intact platelets or rule out technical artifacts. **Recommendation: set Cluster 6 aside from the main figure pending validation rather than automatically discard it as junk.** Confirm sample provenance, facility filtering and empty-droplet handling, and doublet assessments before deciding its final treatment.

## Features

- Interactive view of the supplied UMAP coordinates, with color by existing cluster, arbitrary gene expression, or supported QC metric.
- Gene coloring uses normalized expression in `ad.X`.
- Quality coloring is restricted in the interface to `n_genes`, `total_counts`, and `pct_mito`.
- Cluster picker and **Run cluster summary** control show ranked marker genes and cluster-level QC summaries.
- Loading/status feedback and clear invalid-gene or invalid-cluster errors; when a map request fails, the previous valid map remains, with a caption that says it was not updated.
- Responsive Tailwind layout; Tailwind and Plotly.js are loaded from CDNs, so a browser connection is needed for those assets.

## Dataset

`data/pbmc3k.h5ad` is a processed AnnData object containing **2,700 cells × 13,714 genes**. The dataset notes describe human peripheral blood mononuclear cells (PBMCs). The file already contains eight Leiden clusters and UMAP coordinates.

| AnnData field | Meaning in this project |
|---|---|
| `ad.X` | Log-normalized expression matrix used for gene coloring and marker ranking. |
| `ad.layers["counts"]` | Raw UMI counts, used for Cluster 6 marker detection. |
| `ad.obs["leiden"]` | Existing numeric-string cluster labels `0` through `7`; labels are not cell-type annotations. |
| `ad.obs["n_genes"]`, `ad.obs["total_counts"]`, `ad.obs["pct_mito"]` | Per-cell quality metadata. All three are present; the recorded analysis found no missing values in these fields. |
| `ad.obsm["X_umap"]` | Existing two-dimensional coordinates used by the navigator. |

No clustering or UMAP is recomputed by the app or analysis script, and the source data is not modified.

## Repository structure

| Path | Purpose |
|---|---|
| `app.py` | FastAPI app, lazy-on-first-request AnnData loading, plotting data and API endpoints. |
| `templates/index.html` | Responsive navigator interface and client-side JavaScript. |
| `static/` | Static asset directory (currently contains a `.keep` placeholder). |
| `analyze_pbmc.py` | Reproducible cluster marker, QC, and Cluster 6 raw-count marker summaries. |
| `data/ABOUT_THIS_FILE.txt` | Supplied dataset guide and field descriptions. |
| `ddls-week5-interview.md` | Available interview transcript with the data owner. |
| `AGENTS.md`, `spec.md` | Analysis brief and specification used to guide the investigation. |
| `requirements.txt` | Python runtime dependencies. |

The supplied `data/pbmc3k.h5ad` dataset is not included in this repository; obtain it through the course-provided source and place it at that path (or set `PBMC_DATA` to its location). Generated environment directories, caches, logs, and credentials should not be committed. The `.gitignore` excludes these common local files and the dataset.

## Requirements and installation

Python 3.9 or newer is recommended. Dependencies declared in `requirements.txt` are FastAPI, Uvicorn (with standard extras), Scanpy, Plotly, and NumPy; Scanpy brings its scientific Python dependencies. No Node/npm build step is needed.

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1` instead of the `source` command.

## Run the app

The project has been run locally using port **8001** (port 8000 may already be occupied):

```bash
source .venv/bin/activate
uvicorn app:app --host 127.0.0.1 --port 8001
```

Open <http://127.0.0.1:8001>. FastAPI's interactive API docs are at <http://127.0.0.1:8001/docs>. To use another dataset path, set `PBMC_DATA` to its `.h5ad` path before starting Uvicorn. The default is `data/pbmc3k.h5ad`.

## How to use the navigator

1. Select **Cluster** to color cells by their existing Leiden assignment.
2. Select **Gene expression**, enter a gene symbol (for example, `PPBP`), and press **Run**. Any gene in `ad.var_names` can be requested; unknown genes return a visible error.
3. Select **Quality metric** and choose one of the three available metrics: `n_genes`, `total_counts`, or `pct_mito`. The map updates on selection.
4. Choose a cluster with the cluster picker. **Run cluster summary** fetches its top Wilcoxon-ranked genes and QC summary. Selecting a new cluster also refreshes the displayed summary.
5. If a request fails, read the status message. For a failed map update, the last successful plot is retained and its caption explicitly says `Map not updated`; it should not be interpreted as the requested new coloring.

The API includes `/api/umap`, `/api/expression/{gene}`, `/api/markers/{cluster}`, `/api/quality`, `/api/clusters`, and `/api/genes`.

## Preliminary cluster annotations

These are cautious interpretations of the recorded Wilcoxon marker-ranking output and supporting marker inspection. They are not labels provided by the dataset, and several identities remain broad or uncertain.

| Cluster | Preliminary interpretation | Supporting ranked markers |
|---|---|---|
| 0 | T-cell-enriched; ranked list is ribosomal-dominated | `RPS12`, `LDHB`, `RPS25`, `RPS27`, `CD3D` |
| 1 | Classical/inflammatory monocyte-like | `LYZ`, `S100A9`, `S100A8`, `TYROBP`, `FCN1` |
| 2 | Cytotoxic T/NK-like | `NKG7`, `GZMA`, `CCL5`, `PRF1`, `GZMM` |
| 3 | B-cell-like | `CD79A`, `MS4A1`, `CD74`, `HLA-DRA`, `CD79B` |
| 4 | FCGR3A-positive monocyte-like | `LST1`, `FCGR3A`, `FCER1G`, `AIF1`, `COTL1` |
| 5 | HLA-II-high antigen-presenting/dendritic-like | `HLA-DPA1`, `HLA-DRA`, `CD74`, `FCER1A` |
| 6 | Platelet-associated transcript signal; precise identity unresolved | `GNG11`, `SDPR`, `PF4`, `PPBP`, `NRGN`; raw-count support also includes `GP9`, `ITGA2B` |
| 7 | Small cluster; identity uncertain, with cytoskeletal and cell-cycle-associated genes | `ACTG1`, `CFL1`, `KIAA0101`, `STMN1` |

## Cluster 6 evidence, caveats, and next steps

The strongest evidence is the coherent platelet-associated signal across this small cluster: raw counts detect `PF4` and `PPBP` in 13/13 cells, `GP9` in 12/13, and `ITGA2B` in 11/13. The app/analysis also found `GNG11` and `NRGN` in all 13 cells. Cluster 6's median QC values are 350 detected genes, 917 total counts, and 1.57% mitochondrial reads; ranges are 212–2,455 genes, 568–8,931 total counts, and 0.68–3.22% mitochondrial reads. Twelve cells are relatively low-complexity. One cell (`ACGAACTGGCTATG-1`) has 2,455 genes and 8,931 counts, with platelet markers and leukocyte-associated detections including `CD74`, `LST1`, `FCGR3A`, `LYZ`, `PTPRC`, and `S100A9`. This is compatible with a mixed-lineage/doublet-like signal, but does not establish a doublet. Sparse leukocyte-marker detections elsewhere are not, by themselves, evidence of a coherent second lineage.

The matrix supports a platelet-associated RNA annotation, not a claim that these are intact platelets. Platelets are naturally anucleate and RNA-poor, so low gene counts alone do not establish that observations are empty droplets or junk. The available files do not document sample provenance, facility filtering, empty-droplet handling, or facility doublet calls. Resolve those with the data owner/facility, inspect the high-complexity cell, and validate the platelet-associated group before deciding whether it belongs in the main figure.

## Reproducible analysis

With the environment installed, run:

```bash
source .venv/bin/activate
python analyze_pbmc.py --data data/pbmc3k.h5ad --top-n 10
```

This reads the existing AnnData data, summarizes metadata, missingness, cluster sizes and QC, ranks markers using the existing Leiden labels, and prints Cluster 6 raw-count marker detection. It does not recalculate the UMAP or clusters.

## Testing and limitations

Recorded checks include FastAPI TestClient checks for the home page, cluster/QC endpoints, cluster/gene/quality UMAP coloring, expression, marker ranking, gene lookup, and invalid gene/cluster responses; successful and expected 404 outcomes were observed. Cluster marker/QC summaries agreed on cell counts for clusters 4 (163) and 6 (13). Python compilation and inline JavaScript syntax parsing with Node were performed. The latest quality-metric dropdown and failed-request feedback code were checked for the three allowed options and expected error-caption logic. **Browser rendering, visual responsiveness, and manual interaction have not been verified.** The user should open the app in a browser and check all metric modes, cluster summary interactions, a valid gene, and invalid-gene feedback; also inspect a narrow/mobile viewport. These results describe the checks recorded during development and are not a claim of a fresh end-to-end run during publication preparation.

## DDLS requirements and hand-in

The Week 5 lab handout says **no separate written report is required**. The required deliverables are the working single-cell navigator and a GitHub repository with a clear README explaining what the app does, how to run it, and the answer to the owner's question. The README or app should identify the question cluster, its markers, and the cell type they point to. Submit the GitHub repository URL in the course portal along with the interview and Pi analysis transcripts. A report or GitHub Pages project page is optional. The live app tunnel is also optional and temporary.

The interview transcript is included as `ddls-week5-interview.md`. `ddls-week5-pi-transcript.md` is the available edited Markdown export of the Pi conversation; it is not the full original session transcript. The course allows an analysis transcript as readable Markdown/text or raw Pi `.jsonl`. If submitting a transcript through the course portal, review the original session log for private information and use the format requested by the course; do not add raw session logs to this repository.

**Course reference:** [DDLS Computer Lab 5 — Interview a Single-Cell Data Owner, Build a Navigator, Read the Cells](https://ddls.aicell.io/course/ddls-2026/module-5/lab/).
