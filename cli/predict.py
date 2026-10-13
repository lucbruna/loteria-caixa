#!/usr/bin/env python3
from collections import defaultdict, Counter
from pathlib import Path
import csv
import sys


def load_clean(path):
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        return [x for x in r if x["bilhete"] != "000000"]


def predict_for_conc(rows, for_conc, top_k=10, alpha=0.3):
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    last_seen = {}
    count_total = Counter()
    for conc in concs:
        if conc >= for_conc:
            break
        for x in by_conc[conc]:
            t = x["bilhete"]
            last_seen[t] = conc
            count_total[t] += 1
    if not count_total:
        maxf = 1
    else:
        maxf = max(count_total.values())
    cands = []
    for t, lc in last_seen.items():
        gap = (for_conc - 1) - lc
        rec = 1.0 / (gap + 1.0)
        freq = count_total[t]
        score = alpha * (freq / maxf) + (1 - alpha) * rec
        cands.append((t, score, freq, gap))
    cands.sort(key=lambda x: x[1], reverse=True)
    return cands[:top_k]


def main():
    base = Path(__file__).resolve().parents[1]
    proc = base / "data" / "processed" / "federal.csv"
    rows = load_clean(proc)
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    last = concs[-1]
    target = last + 1
    print(f"Último concurso: {last}")
    print(f"Predições para concurso: {target}")
    print("(baseadas em histórico até {last}, sem look-ahead)")
    print("-"*60)
    top = predict_for_conc(rows, target, top_k=15)
    for i, (t, score, freq, gap) in enumerate(top, 1):
        print(f"{i:2d}. {t} | score={score:.4f} | freq={freq} | gap={gap}")


if __name__ == "__main__":
    main()
