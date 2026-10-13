import csv
from collections import defaultdict, Counter
from pathlib import Path


def analyze():
    base = Path(__file__).resolve().parents[2]
    proc = base / "data" / "processed" / "federal.csv"
    with open(proc, encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = [x for x in r if x["bilhete"] != "000000"]
    # soma
    sums = [int(r["num"]) for r in rows]
    print(f"média num bilhete: {sum(sums)/len(sums):.1f}")
    print(f"min={min(sums)}, max={max(sums)}")
    # ranges by first digits groups
    # 000000-099999 all start 0
    # analyze by value ranges
    ranges = Counter()
    for s in sums:
        # ranges of 10000
        r = (s // 10000) * 10000
        ranges[f"{r:06d}-{r+9999:06d}"] += 1
    print("\ntop 5 faixas:")
    for k,v in ranges.most_common(5):
        print(f"{k}: {v}")


if __name__ == "__main__":
    analyze()
