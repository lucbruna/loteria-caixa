import csv
from collections import defaultdict
from pathlib import Path
import json


def analyze_gap():
    base = Path(__file__).resolve().parents[2]
    proc = base / "data" / "processed" / "federal.csv"
    with open(proc, encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows_all = list(r)
    rows = [x for x in rows_all if x["bilhete"] != "000000"]
    # last seen per ticket
    last_seen = {}
    gaps = []
    # process in order
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    # track
    for conc in concs:
        # record gaps for tickets that appeared before? compute gap as conc - last_seen
        seen_now = set()
        for x in by_conc[conc]:
            t = x["bilhete"]
            seen_now.add(t)
            if t in last_seen:
                gap = conc - last_seen[t]
                gaps.append(gap)
            last_seen[t] = conc
    # distribution
    from collections import Counter
    c = Counter(gaps)
    print(f"total ocorrências com gap conhecido: {len(gaps)}")
    print("gap freq (top 15):")
    for g, cnt in c.most_common(15):
        print(f"{g}: {cnt}")
    print(f"média gap: {sum(gaps)/len(gaps):.1f}")


if __name__ == "__main__":
    analyze_gap()
