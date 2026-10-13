from collections import defaultdict, Counter
from pathlib import Path
import csv


def load_clean(path: Path):
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        return [x for x in r if x["bilhete"] != "000000"]


def backtest_fast():
    base = Path(__file__).resolve().parents[2]
    proc = base / "data" / "processed" / "federal.csv"
    rows = load_clean(proc)
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    split = int(len(concs)*0.8)
    test_concs = set(concs[split:])
    # maintain state
    last_seen = {}
    count_total = Counter()
    hits = 0; total = 0
    # process in order up to before test, then test
    for conc in concs:
        if conc in test_concs:
            # predict before updating with results? predict for conc using state up to conc-1
            # score
            if count_total:
                maxf = max(count_total.values())
            else:
                maxf = 1
            # get top 10 by score alpha=0.3 (favor recency a bit more)
            cands = []
            for t, lc in list(last_seen.items()):
                gap = (conc - 1) - lc
                rec = 1.0 / (gap + 1.0)
                freq = count_total[t]
                score = 0.3*(freq/maxf) + 0.7*rec
                cands.append((t, score))
            cands.sort(key=lambda x: x[1], reverse=True)
            preds = set(t for t,s in cands[:10])
            # check hits
            for x in by_conc[conc]:
                total += 1
                if x["bilhete"] in preds:
                    hits += 1
        # update state with this conc's results
        for x in by_conc[conc]:
            t = x["bilhete"]
            last_seen[t] = conc
            count_total[t] += 1
    print(f"intelligent_fast top10: hits={hits}/{total} ({hits/total:.4%})")


if __name__ == "__main__":
    backtest_fast()
