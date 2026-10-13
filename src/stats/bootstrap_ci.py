from collections import defaultdict, Counter
from pathlib import Path
import csv
import numpy as np


def bootstrap_ci(hits_obs, total_obs, n_boot=2000, alpha=0.05):
    p_obs = hits_obs / total_obs if total_obs else 0.0
    rng = np.random.default_rng(42)
    p_boot = []
    for _ in range(n_boot):
        # simulate
        h = rng.binomial(total_obs, p_obs)
        p_boot.append(h / total_obs if total_obs else 0.0)
    p_boot = np.array(p_boot)
    lo = np.percentile(p_boot, 100*alpha/2)
    hi = np.percentile(p_boot, 100*(1-alpha/2))
    return p_obs, lo, hi


def main():
    base = Path(__file__).resolve().parents[2]
    proc = base / "data" / "processed" / "federal.csv"
    with open(proc, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r['bilhete']!='000000']
    # simple split
    by_conc = defaultdict(list)
    for x in rows: by_conc[int(x['concurso'])].append(x)
    concs = sorted(by_conc)
    split = int(len(concs)*0.8)
    test = concs[split:]
    # naive top10 on train
    train_rows = [r for r in rows if int(r['concurso']) < test[0]]
    c = Counter(r['bilhete'] for r in train_rows)
    preds = set(t for t,_ in c.most_common(10))
    hits = sum(1 for r in rows if int(r['concurso']) in set(test) and r['bilhete'] in preds)
    total = sum(1 for r in rows if int(r['concurso']) in set(test))
    p, lo, hi = bootstrap_ci(hits, total)
    print(f"freq-top10 (test): hits={hits}/{total} p={p:.4%} CI95=[{lo:.4%},{hi:.4%}]")


if __name__ == "__main__":
    main()
