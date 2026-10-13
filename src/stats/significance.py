from collections import defaultdict, Counter
from pathlib import Path
import csv
import numpy as np


def load_clean():
    base = Path(__file__).resolve().parents[2]
    with open(base/'data/processed/federal.csv', encoding='utf-8') as f:
        return [x for x in csv.DictReader(f) if x['bilhete']!='000000']


def main():
    rows = load_clean()
    by = defaultdict(list)
    for x in rows: by[int(x['concurso'])].append(x)
    concs = sorted(by)
    split = int(len(concs)*0.8)
    test = set(concs[split:])
    train = [r for r in rows if int(r['concurso']) < concs[split]]
    test_rows = [r for r in rows if int(r['concurso']) in test]
    c = Counter(r['bilhete'] for r in train)
    preds = set(t for t,_ in c.most_common(10))
    hits_obs = sum(1 for r in test_rows if r['bilhete'] in preds)
    total = len(test_rows)
    # permutation
    rng = np.random.default_rng(42)
    hits_perm = []
    # get pool
    pool = [r['bilhete'] for r in test_rows]
    for _ in range(1000):
        rng.shuffle(pool)
        # fake preds? compare hits if we picked random 10? simpler: permute labels
        # or count random matches naive
        pass
    print(f"hits_obs={hits_obs}/{total}")


if __name__ == '__main__':
    main()
