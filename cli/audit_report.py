#!/usr/bin/env python3
from collections import defaultdict, Counter
from pathlib import Path
import csv


def load_clean(path):
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        return [x for x in r if x["bilhete"] != "000000"]


def predict_top(rows, for_conc, top_k=10, alpha=0.3):
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    last_seen = {}
    count_total = Counter()
    for conc in concs:
        if conc >= for_conc:
            break
        for x in by_conc[conc]:
            t = x["bilhete"]
            last_seen[t] = conc
            count_total[t] += 1
    if not count_total:
        maxf = 1
    else:
        maxf = max(count_total.values())
    cands = []
    for t, lc in last_seen.items():
        gap = (for_conc - 1) - lc
        rec = 1.0 / (gap + 1.0)
        freq = count_total[t]
        score = alpha * (freq / maxf) + (1 - alpha) * rec
        cands.append((t, score, freq, gap))
    cands.sort(key=lambda x: x[1], reverse=True)
    return cands[:top_k]


def main():
    base = Path(__file__).resolve().parents[1]
    proc = base / "data" / "processed" / "federal.csv"
    out = base / "reports" / "predicoes_vs_reais.csv"
    rows = load_clean(proc)
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    split = int(len(concs) * 0.8)
    test_concs = concs[split:]
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["concurso", "premio_pos", "bilhete_real", "acertou", "predito_rank", "predito_bilhete", "predito_score", "predito_freq", "predito_gap"])
        for tc in test_concs:
            top = predict_top(rows, tc, top_k=10)
            top_map = {t: (i+1, score, freq, gap) for i,(t,score,freq,gap) in enumerate(top)}
            for x in by_conc[tc]:
                breal = x["bilhete"]
                pos = x["posicao"]
                if breal in top_map:
                    rank, score, freq, gap = top_map[breal]
                    w.writerow([tc, pos, breal, "SIM", rank, breal, f"{score:.4f}", freq, gap])
                else:
                    w.writerow([tc, pos, breal, "NAO", "", "", "", "", ""])
    print(f"Relatório gerado: {out}")


if __name__ == "__main__":
    main()
