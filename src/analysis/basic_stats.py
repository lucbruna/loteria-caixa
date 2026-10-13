import csv
from collections import defaultdict, Counter
from pathlib import Path
import json


def load_csv(path: Path):
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r)


def analyze():
    base = Path(__file__).resolve().parents[2]
    proc = base / "data" / "processed" / "federal.csv"
    rows = load_csv(proc)
    # group by concurso
    by_conc = defaultdict(list)
    for x in rows:
        by_conc[int(x["concurso"])].append(x)
    concs = sorted(by_conc.keys())
    print(f"concursos: {len(concs)}, primeiros={concs[0]}, ultimos={concs[-1]}")
    # frequency of last 2 digits of ticket? or look at bilhete as number
    # analyze distribution of numbers
    all_tix = [r["bilhete"] for r in rows]
    c = Counter(all_tix)
    # most frequent
    print("\n--- top 10 bilhetes mais frequentes (histórico) ---")
    for t, cnt in c.most_common(10):
        print(f"{t}: {cnt}")
    # by last digit
    c_last = Counter(r["d6"] for r in rows)
    print("\n--- distribuição por último dígito ---")
    for d in "0","1","2","3","4","5","6","7","8","9":
        print(f"{d}: {c_last.get(d,0)}")
    # by first digit
    c_first = Counter(r["d1"] for r in rows)
    print("\n--- distribuição por 1º dígito ---")
    for d in "0","1","2","3","4","5","6","7","8","9":
        print(f"{d}: {c_first.get(d,0)}")


if __name__ == "__main__":
    analyze()
