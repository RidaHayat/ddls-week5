# DDLS 2026 — Week 5 interview transcript

**Lab:** Interview a Single-Cell Data Owner
**Data owner:** Dr. Ravi Menon — Immunologist cleaning up a PBMC single-cell dataset before a figure
**Student:** Rida Hayat <rida.hayat@studenti.univr.it>
**Exported:** 2026-10-20T20:05:34+00:00

> This is the record of your interview with the data owner. Hand it to your analyst agent as the raw source for `AGENTS.md` and `spec.md`.

---

**You**:

Hi! I'd like to understand your single-cell RNA-seq dataset and the biological question you're trying to answer before I start analysing it.  Could you explain what decision you need to make about the cluster you're concerned about, and why it matters for your research?

**Dr. Ravi Menon**:

I’m Ravi, an immunologist, and this is my first PBMC single-cell dataset back from the facility: **2,700 blood cells** grouped into clusters 0–7. I’m concerned about cluster 6—just **13 cells**, with about **350 genes detected per cell**—and my instinct is that they’re dead cells or empty droplets. I’m about to bin them as junk; can you confirm it’s safe to delete them from the figure?

**You**:

Thanks, Ravi. Before we investigate cluster 6, could you tell me a little more about the dataset structure? What file format is it in, what do the rows and columns represent, and which metadata fields are available for each cell? I'd also like to know what the cluster labels and quality metrics represent.

**Dr. Ravi Menon**:

I’m afraid I don’t know the file format or how the rows and columns are arranged—the facility sent me one processed file and a map. The summary I can see lists each cell’s numbered cluster, cells per cluster, genes detected per cell, and percent mitochondrial; I can’t tell you how those last measurements were calculated or what other cell-level fields are included. The labels are just 0–7, not cell identities. Are you asking about the file itself, or what’s in cluster 6?

**You**:

I’m asking about both, but let’s start with the file itself so I can understand what information is available for the analysis. Since you have the processed file and the cell map, could you share the original file or tell me how I can access it through the portal? I can inspect its structure and identify the available cell-level fields before investigating cluster 6.

**Dr. Ravi Menon**:

I can’t share it from here—I don’t have the facility portal details in front of me, just the summary and map. The original file should be in the facility’s delivery, but I’d need to check my email for the link. Do you want me to look for that, or should we work from the summary for now?

**You**:

I’ve confirmed that the file contains 2,700 cells, cluster labels, gene counts, total counts, mitochondrial percentages, normalized expression, and raw counts. Before I assess cluster 6, what would a convincing answer look like to you? Would you prefer a recommendation supported by marker genes and quality metrics, and what evidence would make you confident that keeping or removing these cells is justified?

**Dr. Ravi Menon**:

A clear keep-or-set-aside recommendation for the figure, with a short reason I can pass to my co-author, would be useful—especially if it uses what the cells actually express, not just their size. Huh, I hadn’t looked at what they’re expressing; I saw the gene count and assumed. Are some real blood cells naturally small and RNA-poor? I wouldn’t know which.

**You**:

That’s helpful. Before I interpret the markers, do you know whether the facility filtered out low-quality cells or empty droplets before delivering the dataset? Have you noticed any missing values, suspected doublets, or other quality issues, and is there anything about these measurements you trust least?

**Dr. Ravi Menon**:

I don’t know what filtering the facility did, and I haven’t checked for missing values or other problems in the file. All I can say from the summary is that cluster 6 has 13 cells, about 350 genes per cell, and 1.6% mitochondrial reads; I can’t tell you which measurements to trust least. What do the genes those cells are expressing look like?

**You**:

The platelet-associated markers give us a possible explanation for cluster 6, but I’d like to be careful before making a final recommendation. Have you or the facility checked whether these cells express markers from other immune-cell types as well, which could suggest platelet–immune-cell doublets or contamination? And has anyone previously investigated or annotated this cluster?

**Dr. Ravi Menon**:

I haven’t checked whether they also show signs of other blood-cell types, and I don’t know whether the facility investigated them; the labels I received are just numbers. Huh—I hadn’t looked at what they’re actually expressing; I just saw the low gene count and assumed. Are some real blood cells naturally small and RNA-poor? I wouldn’t know which.

**You**:

Let me check that I’ve understood correctly: you need a keep-or-set-aside recommendation for cluster 6, supported by gene expression and quality metrics, that you can explain to your co-author. The dataset contains 2,700 PBMCs with clusters 0–7, but the facility’s filtering steps and possible doublets haven’t been verified. Your initial assumption was that the low gene count meant these cells were junk, although their marker genes haven’t been investigated. What have I missed?

**Dr. Ravi Menon**:

That’s about it. I haven’t seen which genes stand out or checked for signs of other blood-cell types, and I don’t know the facility’s filtering steps or any previous annotation. I was going by the gene count; what do the platelet-associated genes actually look like alongside the other cell signals?
