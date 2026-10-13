from collections import defaultdict, Counter
from pathlib import Path
import csv
import math


def load_clean(path: Path):
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        return [x for x in r if x["bilhete"] != "000000"]


class IntelligentPredictor:
    def __init__(self, rows):
        self.rows = rows
        self.by_conc = defaultdict(list)
        for x in rows:
            self.by_conc[int(x["concurso"])].append(x)
        self.concs = sorted(self.by_conc.keys())
        # build state
        self.last_seen = {}  # ticket -> last conc
        self.count_total = Counter()
        for x in rows:
            self.count_total[x["bilhete"]] += 1
    
    def train_up_to(self, max_conc):
        # recompute state up to max_conc
        self.last_seen = {}
        self.count_total = Counter()
        for conc in self.concs:
            if conc > max_conc:
                break
            for x in self.by_conc[conc]:
                t = x["bilhete"]
                self.last_seen[t] = conc
                self.count_total[t] += 1
    
    def predict(self, for_conc, top_k=10, alpha=0.5):
        # score: freq*alpha + recency*(1-alpha). recency = 1/(gap+1) normalized
        self.train_up_to(for_conc - 1) if for_conc > min(self.concs) else None
        scores = {}
        # consider all tickets seen before? but many. focus on those seen recently or all? 
        # for federal tickets are many; use all seen before with scoring
        for t, last_c in self.last_seen.items():
            gap = (for_conc - 1) - last_c if for_conc > last_c else 0
            rec = 1.0 / (gap + 1.0)
            freq = self.count_total.get(t, 0)
            # normalize freq roughly
            score = alpha * (freq / max(1, max(self.count_total.values()))) + (1-alpha) * rec
            scores[t] = score
        # also consider tickets never seen? rare to hit, skip for scoring focus
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]


def backtest_intel():
    base = Path(__file__).resolve().parents[2]
    proc = base / "data" / "processed" / "federal.csv"
    rows = load_clean(proc)
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    split = int(len(concs)*0.8)
    test_concs = concs[split:]
    pred = IntelligentPredictor(rows)
    hits = 0; total = 0
    for tc in test_concs[:30]:  # sample for speed
        res = set(x["bilhete"] for x in by_conc[tc])
        top = pred.predict(tc, top_k=10)
        preds = set([t for t,s in top])
        for r in res:
            total += 1
            if r in preds:
                hits += 1
    print(f"intelligent (recency+freq, top10, sampled): hits={hits}/{total} ({hits/total:.4%})")


if __name__ == "__main__":
    backtest_intel()
