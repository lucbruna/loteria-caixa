from collections import defaultdict, Counter
from pathlib import Path
import csv
import numpy as np


def brier_score(y_true, y_prob):
    y_true = np.array(y_true, dtype=float)
    y_prob = np.array(y_prob, dtype=float)
    return np.mean((y_prob - y_true)**2)


def main():
    base = Path(__file__).resolve().parents[2]
    with open(base/'data/processed/federal.csv') as f:
        rows = [r for r in csv.DictReader(f) if r['bilhete']!='000000']
    by = defaultdict(list)
    for x in rows: by[int(x['concurso'])].append(x)
    concs = sorted(by)
    split = int(len(concs)*0.8)
    test = concs[split:]
    train = [r for r in rows if int(r['concurso']) < test[0]]
    c = Counter(r['bilhete'] for r in train)
    preds = c.most_common(20)
    # score map
    total_c = sum(c.values())
    y_true, y_prob = [], []
    for tc in test[:50]:
        next_set = set(x['bilhete'] for x in by[tc])
        for t,freq in preds[:10]:
            y_prob.append(freq/max(1,total_c))
            y_true.append(1.0 if t in next_set else 0.0)
    print('Brier:', brier_score(y_true,y_prob))


if __name__=='__main__':
    main()
