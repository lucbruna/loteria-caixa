import csv
from collections import defaultdict, Counter
from pathlib import Path


def analyze():
    base = Path(__file__).resolve().parents[2]
    proc = base / "data" / "processed" / "federal.csv"
    with open(proc, encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = [x for x in r if x["bilhete"] != "000000"]
    by_pos = defaultdict(list)
    for x in rows:
        by_pos[int(x["posicao"])].append(x)
    for pos in range(1,6):
        last = Counter(r["d6"] for r in by_pos[pos])
        print(f"\n=== POSIÇÃO {pos} ===")
        print("último dígito:")
        for d in "0","1","2","3","4","5","6","7","8","9":
            print(f"{d}:{last.get(d,0):4d}", end="  ")
        print()


if __name__ == "__main__":
    analyze()
