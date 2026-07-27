import json
import os
import uuid
from datetime import datetime
from typing import Any
from config import DATA_DIR

PREDICOES_FILE = os.path.join(DATA_DIR, "predicoes.json")
STATS_FILE = os.path.join(DATA_DIR, "stats_predicoes.json")


def _load() -> dict:
    if not os.path.exists(PREDICOES_FILE):
        return {}
    try:
        with open(PREDICOES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict):
    os.makedirs(os.path.dirname(PREDICOES_FILE), exist_ok=True)
    with open(PREDICOES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def salvar_predicoes(
    lottery: str, source: str, combinacoes: list[dict], config: dict
) -> list[str]:
    data = _load()
    if lottery not in data:
        data[lottery] = {"predicoes": [], "stats": {}}
    ids = []
    for comb in combinacoes:
        pid = str(uuid.uuid4())[:8]
        ids.append(pid)
        data[lottery]["predicoes"].append({
            "id": pid,
            "data": datetime.now().isoformat(),
            "fonte": source,
            "numeros": comb.get("numeros", comb.get("combinacao", [])),
            "confianca": comb.get("confianca", comb.get("score", 0)),
            "estrategia": comb.get("estrategia", ""),
            "concurso_verificado": None,
            "acertos": None,
            "numeros_acertados": [],
            "verificado": False,
            "atualizado_em": None,
        })
    _save(data)
    return ids


def obter_predicoes(lottery: str | None = None) -> dict:
    data = _load()
    if lottery:
        return data.get(lottery, {"predicoes": [], "stats": {}})
    return data


def obter_estatisticas(lottery: str | None = None) -> dict:
    data = _load()
    stats = {}
    loterias = [lottery] if lottery else list(data.keys())
    for chave in loterias:
        preds = data.get(chave, {}).get("predicoes", [])
        total = len(preds)
        verificadas = [p for p in preds if p.get("verificado")]
        if not total:
            stats[chave] = {"total": 0, "verificadas": 0, "media_acertos": 0, "por_verificar": 0}
            continue
        acertos_list = [p["acertos"] for p in verificadas if p["acertos"] is not None]
        media = sum(acertos_list) / len(acertos_list) if acertos_list else 0
        dist = {}
        for p in verificadas:
            a = p.get("acertos", 0)
            dist[str(a)] = dist.get(str(a), 0) + 1
        stats[chave] = {
            "total": total,
            "verificadas": len(verificadas),
            "por_verificar": total - len(verificadas),
            "media_acertos": round(media, 2),
            "max_acertos": max(acertos_list) if acertos_list else 0,
            "distribuicao": dist,
            "ultima_verificacao": max(
                (p["atualizado_em"] for p in verificadas if p.get("atualizado_em")),
                default=None,
            ),
        }
    return stats


def verificar_todas_predicoes(api_client) -> dict:
    from config import LOTTERIES
    data = _load()
    resultados_verificacao = {}
    for lottery_key in list(data.keys()):
        if lottery_key not in LOTTERIES:
            continue
        config = LOTTERIES[lottery_key]
        preds = data[lottery_key].get("predicoes", [])
        nao_verificadas = [p for p in preds if not p.get("verificado")]
        if not nao_verificadas:
            continue
        ultimo = api_client.get_latest_result(lottery_key)
        if not ultimo:
            continue
        concurso_num = ultimo.get("numero")
        dezenas = set(int(d) for d in ultimo.get("listaDezenas", []))
        for p in nao_verificadas:
            nums_set = set(p.get("numeros", []))
            acertos = len(nums_set & dezenas)
            p["acertos"] = acertos
            p["numeros_acertados"] = sorted(nums_set & dezenas)
            p["concurso_verificado"] = concurso_num
            p["verificado"] = True
            p["atualizado_em"] = datetime.now().isoformat()
        resultados_verificacao[lottery_key] = {
            "concurso": concurso_num,
            "dezenas_sorteadas": sorted(dezenas),
            "total_verificadas": len(nao_verificadas),
        }
    _save(data)
    return {
        "status": "ok",
        "loterias_verificadas": len(resultados_verificacao),
        "detalhes": resultados_verificacao,
    }


def limpar_predicoes(lottery: str | None = None):
    data = _load()
    if lottery:
        data.pop(lottery, None)
    else:
        data.clear()
    _save(data)
