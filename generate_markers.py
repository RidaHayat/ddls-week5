import json
import math
import warnings

import scanpy as sc

N = 50
ad = sc.read_h5ad("data/pbmc3k.h5ad")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    sc.tl.rank_genes_groups(ad, groupby="leiden", method="wilcoxon", use_raw=False, n_genes=N)
r = ad.uns["rank_genes_groups"]


def clean(x):
    x = float(x)
    return x if math.isfinite(x) else None


out = {}
for c in sorted(ad.obs["leiden"].astype(str).unique(), key=int):
    out[c] = [
        {
            "gene": str(r["names"][c][i]),
            "score": clean(r["scores"][c][i]),
            "p_value": clean(r["pvals"][c][i]),
            "adjusted_p_value": clean(r["pvals_adj"][c][i]),
            "log_fold_change": clean(r["logfoldchanges"][c][i]),
        }
        for i in range(N)
    ]

with open("data/markers.json", "w") as f:
    json.dump(out, f)
print("Saved data/markers.json for clusters:", list(out))