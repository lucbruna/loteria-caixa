from collections import defaultdict
from pathlib import Path
import csv


def main():
    base = Path(__file__).resolve().parents[2]
    with open(base/'data/processed/federal.csv') as f:
        rows = [r for r in csv.DictReader(f) if r['bilhete']!='000000']
    by = defaultdict(list)
    for x in rows: by[int(x['concurso'])].append(x)
    concs = sorted(by)[:3000]  # sample
    last = {}
    cnt = 0
    for i,c in enumerate(concs[:-1]):
        next_c = concs[i+1]
        next_set = set(x['bilhete'] for x in by[next_c])
        for t,lc in list(last.items())[:500]:  # limit
            gap = c-lc
            target = 1 if t in next_set else 0
            cnt += 1
        for x in by[c]: last[x['bilhete']]=c
    print('ok', cnt)


if __name__=='__main__':
    main()
