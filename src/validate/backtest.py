import csv
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime
import json


def load_csv(path: Path):
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
    # clean anomalies
    rows = [x for x in rows if x["bilhete"] != "000000"]
    return rows


def backtest_naive_freq(train_rows, test_rows, top_k=5):
    # top K most frequent in train
    c = Counter(r["bilhete"] for r in train_rows)
    preds = set([t for t,cnt in c.most_common(top_k)])
    # count hits: how many test prizes are in preds?
    hits = 0
    total = len(test_rows)
    for r in test_rows:
        if r["bilhete"] in preds:
            hits += 1
    return hits, total, hits/total if total else 0


def backtest():
    base = Path(__file__).resolve().parents[2]
    proc = base / "data" / "processed" / "federal.csv"
    rows = load_csv(proc)
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    # time split: 80% train, 20% test
    split = int(len(concs) * 0.8)
    train_concs = set(concs[:split])
    test_concs = set(concs[split:])
    train_rows = [r for r in rows if int(r["concurso"]) in train_concs]
    test_rows = [r for r in rows if int(r["concurso"]) in test_concs]
    print(f"split: train_concs={len(train_concs)} (conc {min(train_concs)}-{max(train_concs)}), test_concs={len(test_concs)} ({min(test_concs)}-{max(test_concs)})")
    h,t,p = backtest_naive_freq(train_rows, test_rows, top_k=5)
    print(f"freq-top5: hits={h}/{t} ({p:.4%})")
    h,t,p = backtest_naive_freq(train_rows, test_rows, top_k=10)
    print(f"freq-top10: hits={h}/{t} ({p:.4%})")
    h,t,p = backtest_naive_freq(train_rows, test_rows, top_k=20)
    print(f"freq-top20: hits={h}/{t} ({p:.4%})")


if __name__ == "__main__":
    backtest()
