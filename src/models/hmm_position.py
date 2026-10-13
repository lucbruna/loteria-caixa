from pathlib import Path
import csv
import numpy as np
from hmmlearn import hmm


def seq_by_pos(rows, pos):
    by = {}
    for x in rows:
        if int(x['posicao'])==pos:
            by[int(x['concurso'])]=int(x['bilhete'])
    concs = sorted(by)
    return [by[c] for c in concs]


def main():
    base = Path(__file__).resolve().parents[2]
    with open(base/'data/processed/federal.csv') as f:
        rows = [r for r in csv.DictReader(f) if r['bilhete']!='000000']
    X = seq_by_pos(rows,1)[:2000]
    if len(X)>10:
        Xs = np.array(X).reshape(-1,1)
        model = hmm.GaussianHMM(n_components=3, n_iter=10, random_state=42)
        try:
            model.fit(Xs)
            print('HMM ok', model.n_components)
        except Exception as e:
            print('err',e)
    else:
        print('skip')


if __name__ == '__main__':
    main()
