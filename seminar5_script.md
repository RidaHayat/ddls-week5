# Seminar 5 — Show Your Navigator, Defend the Call

**7-minute demo + 3-minute Q&A | Live app:** https://ddls-week5-pbmc-navigator.onrender.com/  
**Repository:** https://github.com/RidaHayat/ddls-week5

> Quotes below are from `ddls-week5-interview.md`; no separate original interview audio/recording was supplied. Cluster 6 is a transcript-backed project question, not an unverified alternate quote.

## Timed speaking script

### 0:00–0:40 — Title and decision
“Today I’m showing a PBMC navigator and defending one practical decision: should we delete cluster 6 from the figure because it has few detected genes? The short answer is no—not on that evidence alone. I recommend setting it aside pending validation.”

### 0:40–1:25 — Owner’s question
Dr. Ravi Menon said: **“I’m concerned about cluster 6—just 13 cells, with about 350 genes detected per cell—and my instinct is that they’re dead cells or empty droplets. I’m about to bin them as junk; can you confirm it’s safe to delete them from the figure?”**
“He also said he did not know the facility’s filtering steps or whether possible doublets had been checked. That uncertainty is part of the decision.”

### 1:25–2:45 — Live navigator walkthrough (do not use screenshots instead)
Open the live URL. Explain that the map uses the provided UMAP and cluster labels; it does not recompute either. Color by cluster first, then choose **PPBP** (or search a gene) for normalized expression, followed by `n_genes` and `pct_mito` to show quality coloring. Select cluster 6 and run its summary. Point out that map position is visualization, not cell identity. If the public app is unavailable, follow the backup plan and switch to local app.

### 2:45–4:10 — Marker evidence
“The labels 0–7 are numeric groups, not annotations. The analysis ranks genes from normalized `ad.X`; raw-count detection in `layers['counts']` gives an independent view of whether selected transcripts are detected in individual cells.”
“For cluster 6, `PF4` and `PPBP` were detected in 13/13 cells, `GP9` in 12/13, and `ITGA2B` in 11/13. `GNG11` and `NRGN` were also detected in all 13 in the recorded marker panel. That coordinated platelet-associated RNA signal is stronger evidence than the small gene count alone. RNA detection supports a platelet-associated expression signature; it does not by itself prove intact platelet identity.”

### 4:10–5:10 — Quality and mixed-lineage concern
“Cluster 6 median QC values are 350 genes, 917 total counts, and 1.57% mitochondrial reads; ranges are 212–2,455 genes, 568–8,931 counts, and 0.68–3.22% mitochondrial. Twelve cells are low complexity, while one cell (`ACGAACTGGCTATG-1`) is much higher complexity and has platelet as well as leukocyte-associated detections including `CD74`, `LST1`, `FCGR3A`, `LYZ`, `PTPRC`, and `S100A9`. That is a mixed-lineage/doublet-like flag, not proof of a doublet. Platelets are naturally anucleate and RNA-poor, so low genes alone do not prove junk.”

### 5:10–6:00 — Call and limitation
“My call is **set aside from the main figure pending validation**, not remove as junk and not present as definitively identified intact platelets. The strongest limitation is absent facility/sample provenance and QC context: we do not know empty-droplet filtering, facility doublet calls, or sample handling. Those could change whether this is a legitimate platelet-associated population, contamination, or a technical artifact.”

### 6:00–7:00 — Reproducibility
“A stranger can clone the GitHub repository, read the README, install requirements, provide `data/pbmc3k.h5ad` (or set `PBMC_DATA`), then run `uvicorn app:app --host 127.0.0.1 --port 8001`. `analyze_pbmc.py` reproduces cluster/QC and marker summaries without recomputing the UMAP or clusters. The dataset is tracked with Git LFS in the repository, but deployment data availability depends on the Render configuration.”

## Q&A (3 minutes)

- **Are they definitely platelets?** No. The evidence supports a platelet-associated RNA signature (PF4/PPBP 13/13; GP9 12/13; ITGA2B 11/13), not definitive intact-cell identity.
- **Why not remove for low gene counts?** Low complexity is not sufficient alone; platelets are naturally small/anucleate and RNA-poor. The coherent marker evidence argues against treating every cell as empty debris without validation.
- **Could they be doublets?** One cell has unusually high counts/genes and mixed platelet/leukocyte-associated detections. It is doublet-like, but no facility doublet calls or raw QC are available to establish this.
- **What would change your call?** Facility filtering/provenance and doublet calls; sample-level evidence; inspection/validation of the high-complexity cell; evidence that the marker signal reflects contamination or empty droplets.
- **Does UMAP proximity identify the cell type?** No. UMAP is a visualization; interpretation comes from expression and QC, not map position alone.

## Backup if Render fails
1. Be transparent: public Render was observed to return HTTP 500 for the marker endpoint before the local fix; no deployment dashboard access. Do not claim it is repaired until redeployed and rechecked.
2. Locally, from repo root with dataset available: `source .venv/bin/activate && uvicorn app:app --host 127.0.0.1 --port 8001`; show `http://127.0.0.1:8001` and `/api/markers/1?top_n=10`.
3. If local app cannot start, narrate the exact interaction path using the script and explain the confirmed API tests; do not substitute static screenshots for the requested live demo.
4. Keep a terminal command ready: `curl -sS 'https://ddls-week5-pbmc-navigator.onrender.com/api/markers/1?top_n=10'` (after redeploy, expect HTTP 200 JSON with marker objects, e.g. cluster 1 starts `LYZ`, `S100A9`, `S100A8`).
