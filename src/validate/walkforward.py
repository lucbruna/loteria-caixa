from collections import defaultdict, Counter
from pathlib import Path
import csv


def walkforward_expanding(rows, train_size=1000, step=200, top_k=10):
    by = defaultdict(list)
    for x in rows: by[int(x['concurso'])].append(x)
    concs = sorted(by)
    hits = 0; total = 0
    for i in range(train_size, len(concs)-step, step):
        train_concs = set(concs[:i])
        test_concs = set(concs[i:i+step])
        c = Counter(r['bilhete'] for r in rows if int(r['concurso']) in train_concs)
        preds = set(t for t,_ in c.most_common(top_k))
        for tc in test_concs:
            for x in by[tc]:
                total += 1
                if x['bilhete'] in preds: hits += 1
    return hits,total,hits/total if total else 0


def main():
    base = Path(__file__).resolve().parents[2]
    with open(base/'data/processed/federal.csv') as f:
        rows = [r for r in csv.DictReader(f) if r['bilhete']!='000000']
    h,t,p = walkforward_expanding(rows)
    print(f"WF expanding: {h}/{t} ({p:.4%})")


if __name__ == '__main__':
    main()
