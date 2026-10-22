# Seminar 5 — slide content (PowerPoint-ready)

## Slide 1 — Read the cells, then make the call
**PBMC Single-Cell Navigator | Cluster 6 decision**  
Should 13 low-complexity cells be removed from the figure?  
*Recommendation: set aside pending validation.*

## Slide 2 — The data owner's concern
> “I’m concerned about cluster 6—just 13 cells, with about 350 genes detected per cell—and my instinct is that they’re dead cells or empty droplets. I’m about to bin them as junk; can you confirm it’s safe to delete them from the figure?”

Dr. Ravi Menon also did not know facility filtering or doublet status.  
Source: supplied interview transcript.

## Slide 3 — Live navigator (live demonstration)
- Existing Leiden labels and precomputed UMAP; no reclustering/re-embedding
- Color map by **PPBP** → `n_genes` → `pct_mito`
- Choose cluster 6 and open the marker/QC summary
- UMAP is a map, not an identity test

Live: https://ddls-week5-pbmc-navigator.onrender.com/

## Slide 4 — A coherent platelet-associated RNA signal
**Cluster 6 raw-count detections (n=13)**
- `PF4`: 13/13
- `PPBP`: 13/13
- `GP9`: 12/13
- `ITGA2B`: 11/13
- `GNG11`, `NRGN`: 13/13 in recorded panel

RNA evidence supports an associated signature; it does not prove intact platelet identity.

## Slide 5 — Quality: low complexity, but not enough to call junk
| Cluster 6 metric | Median | Range |
|---|---:|---:|
| Detected genes | 350 | 212–2,455 |
| Total counts | 917 | 568–8,931 |
| Mitochondrial % | 1.57% | 0.68–3.22% |

Twelve are low complexity. One high-complexity cell has platelet and leukocyte-associated detections (including `CD74`, `LST1`, `FCGR3A`, `LYZ`, `PTPRC`, `S100A9`): doublet-like signal, not a doublet call.

## Slide 6 — Decision: set aside pending validation
- Do **not** automatically remove as junk based on genes/cell.
- Retain as a flagged, platelet-associated cluster outside the main figure until checked.
- Platelets are naturally anucleate and RNA-poor; low gene count alone is not diagnostic.

## Slide 7 — Honest limitation; what could change the call?
**Not available:** sample provenance, facility filtering/empty-droplet handling, facility doublet calls.  
**Next:** request those records; review the high-complexity cell and validate marker pattern.  
Contamination/artifact evidence could support removal; validation could support inclusion with an explicit label.

## Slide 8 — Reproduce it from GitHub
https://github.com/RidaHayat/ddls-week5

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# ensure data/pbmc3k.h5ad exists, or set PBMC_DATA
uvicorn app:app --host 127.0.0.1 --port 8001
```

`python analyze_pbmc.py --data data/pbmc3k.h5ad --top-n 10`  
Uses supplied clusters/map; no recomputation.

## Slide 9 — Questions
**What evidence would change your mind?**  
Filtering/provenance • doublet review • sample-level validation • the high-complexity cell

### Speaker notes
Use the timed speaking script in `seminar5_script.md` for narration, detailed caveats, and the Render backup plan. Keep the live app on screen for Slide 3 rather than substituting a screenshot.
