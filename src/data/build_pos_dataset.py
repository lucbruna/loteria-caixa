from collections import defaultdict, Counter
from pathlib import Path
import csv


def main():
    base = Path(__file__).resolve().parents[2]
    with open(base/'data/processed/federal.csv') as f:
        rows = [r for r in csv.DictReader(f) if r['bilhete']!='000000']
    by_conc = defaultdict(list)
    for x in rows: by_conc[int(x['concurso'])].append(x)
    concs = sorted(by_conc)
    # build last_seen global
    last = {}
    out = []
    for i, c in enumerate(concs):
        # predict next? build features up to c-1
        if i < 2: 
            # record
            for x in by_conc[c]: last[x['bilhete']]=c
            continue
        next_c = concs[i+1] if i+1 < len(concs) else None
        # features for tickets seen
        for t, lc in last.items():
            gap = c - lc
            out.append({'concurso':c,'bilhete':t,'gap':gap,'target_next': 0})
        # update
        for x in by_conc[c]: last[x['bilhete']]=c
    print('rows approx', len(out))


if __name__=='__main__':
    main()
