from collections import defaultdict, Counter
from pathlib import Path
import csv


def load_clean(path):
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        return [x for x in r if x["bilhete"] != "000000"]


def rolling_eval(rows, window=2000, step=500, top_k=10, alpha=0.3):
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    hits = 0; total = 0
    # sliding
    for start in range(0, len(concs)-window-step, step):
        train_concs = set(concs[start:start+window])
        test_concs = set(concs[start+window:start+window+step])
        if not test_concs:
            break
        # build state
        last_seen = {}
        count_total = Counter()
        for c in sorted(train_concs):
            for x in by_conc[c]:
                last_seen[x["bilhete"]] = c
                count_total[x["bilhete"]] += 1
        if not count_total:
            maxf = 1
        else:
            maxf = max(count_total.values())
        # test
        for tc in test_concs:
            # predict
            cands = []
            for t, lc in last_seen.items():
                gap = (tc-1) - lc
                rec = 1.0/(gap+1.0)
                freq = count_total[t]
                score = alpha*(freq/maxf) + (1-alpha)*rec
                cands.append((t,score))
            cands.sort(key=lambda x:x[1], reverse=True)
            preds = set(t for t,s in cands[:top_k])
            for x in by_conc[tc]:
                total += 1
                if x["bilhete"] in preds:
                    hits += 1
    return hits, total, hits/total if total else 0


def main():
    base = Path(__file__).resolve().parents[2]
    proc = base / "data" / "processed" / "federal.csv"
    rows = load_clean(proc)
    h,t,p = rolling_eval(rows)
    print(f"rolling(window=2000,step=500,top10): hits={h}/{t} ({p:.4%})")


if __name__ == "__main__":
    main()
