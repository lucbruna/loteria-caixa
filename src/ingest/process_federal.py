import json
from pathlib import Path
import csv


def load_federal(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def process_to_rows(data: dict):
    rows = []
    # concursos em ordem numérica
    for conc_str in sorted(data.keys(), key=lambda k: int(k)):
        conc = int(conc_str)
        tickets = data[conc_str]  # 5 tickets: 1º-5º
        for pos, t in enumerate(tickets, start=1):
            # extrair dígitos (6 dígitos)
            t_clean = str(t).zfill(6)
            d1 = int(t_clean[0])
            d2 = int(t_clean[1])
            d3 = int(t_clean[2])
            d4 = int(t_clean[3])
            d5 = int(t_clean[4])
            d6 = int(t_clean[5])
            num = int(t_clean)  # número do bilhete
            rows.append({
                "concurso": conc,
                "posicao": pos,  # 1-5
                "bilhete": t_clean,
                "num": num,
                "d1": d1, "d2": d2, "d3": d3, "d4": d4, "d5": d5, "d6": d6,
            })
    return rows


def save_csv(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        w.writeheader()
        for r in rows:
            w.writerow(r)


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[2]
    raw = base / "data" / "raw" / "federal.json"
    proc = base / "data" / "processed" / "federal.csv"
    data = load_federal(raw)
    rows = process_to_rows(data)
    save_csv(rows, proc)
    print(f"salvos {len(rows)} registros em {proc}")
