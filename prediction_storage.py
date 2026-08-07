import json
import os
import threading
import uuid
from datetime import datetime

from config import DATA_DIR

PREDICOES_FILE = os.path.join(DATA_DIR, "predicoes.json")
_predicoes_lock = threading.Lock()


def _load() -> dict:
    if not os.path.exists(PREDICOES_FILE):
        return {}
    try:
        with open(PREDICOES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict):
    os.makedirs(os.path.dirname(PREDICOES_FILE), exist_ok=True)
    with open(PREDICOES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def obter_dados_predicoes() -> dict:
    with _predicoes_lock:
        return _load()


def salvar_dados_predicoes(data: dict):
    with _predicoes_lock:
        _save(data)


def _ultimo_concurso(api_client, lottery: str) -> int | None:
    ultimo = api_client.get_latest_result(lottery)
    return ultimo.get("numero") if ultimo else None


def salvar_predicoes(
    lottery: str, source: str, combinacoes: list[dict], config: dict
) -> list[str]:
    data = _load()
    if lottery not in data:
        data[lottery] = {"predicoes": [], "stats": {}}
    ids = []
    from api_client import api_client
    concurso_atual = _ultimo_concurso(api_client, lottery)
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
            "concurso_criacao": concurso_atual,
            "verificacoes": [],
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
        total_verificacoes = sum(len(p.get("verificacoes", [])) for p in preds)
        preds_com_verif = [p for p in preds if p.get("verificacoes")]
        if not total:
            stats[chave] = {
                "total": 0,
                "verificadas": 0,
                "total_verificacoes": 0,
                "media_acertos": 0,
                "por_verificar": total
            }
            continue
        todos_acertos = []
        dist = {}
        concurso_max = 0
        for p in preds_com_verif:
            for v in p["verificacoes"]:
                a = v.get("acertos", 0)
                todos_acertos.append(a)
                dist[str(a)] = dist.get(str(a), 0) + 1
                if v.get("concurso", 0) > concurso_max:
                    concurso_max = v["concurso"]
        media = sum(todos_acertos) / len(todos_acertos) if todos_acertos else 0
        stats[chave] = {
            "total": total,
            "verificadas": len(preds_com_verif),
            "total_verificacoes": total_verificacoes,
            "por_verificar": total - len(preds_com_verif),
            "media_acertos": round(media, 2),
            "max_acertos": max(todos_acertos) if todos_acertos else 0,
            "distribuicao": dist,
            "ultimo_concurso_verificado": concurso_max or None,
        }
    return stats


def verificar_todas_predicoes(api_client) -> dict:
    from config import LOTTERIES
    data = _load()
    resultados_verificacao = {}

    for lottery_key in list(data.keys()):
        if lottery_key not in LOTTERIES:
            continue
        preds = data[lottery_key].get("predicoes", [])
        if not preds:
            continue

        # Descobrir qual o maior concurso ja verificado para esta loteria
        max_concurso_verif = 0
        for p in preds:
            for v in p.get("verificacoes", []):
                if v.get("concurso", 0) > max_concurso_verif:
                    max_concurso_verif = v["concurso"]

        ultimo = api_client.get_latest_result(lottery_key)
        if not ultimo:
            continue
        ultimo_num = ultimo.get("numero", 0)

        # Se o ultimo sorteio ja foi verificado, nao ha nada novo
        if ultimo_num <= max_concurso_verif:
            continue

        # Buscar TODOS os concursos novos desde o ultimo verificado
        novos_concursos = list(range(max_concurso_verif + 1, ultimo_num + 1))
        if not novos_concursos:
            continue

        concursos_dados = api_client._fetch_concursos_paralelo(lottery_key, novos_concursos)
        concursos_map = {}
        for c in concursos_dados:
            n = c.get("numero")
            if n:
                concursos_map[n] = set(int(d) for d in c.get("listaDezenas", []))

        total_verificadas = 0
        for p in preds:
            nums_set = set(p.get("numeros", []))
            concursos_criacao = p.get("concurso_criacao") or 0
            for num_concurso in novos_concursos:
                if num_concurso <= concursos_criacao:
                    continue
                dezenas = concursos_map.get(num_concurso)
                if dezenas is None:
                    continue
                acertos = len(nums_set & dezenas)
                ja_existe = any(v.get("concurso") == num_concurso for v in p.get("verificacoes", []))
                if not ja_existe:
                    numeros_errados = sorted(nums_set - dezenas)
                    p.setdefault("verificacoes", []).append({
                        "concurso": num_concurso,
                        "acertos": acertos,
                        "numeros_sorteados": sorted(dezenas),
                        "numeros_acertados": sorted(nums_set & dezenas),
                        "numeros_errados": numeros_errados,
                        "data_verificacao": datetime.now().isoformat(),
                    })
                    total_verificadas += 1

        if total_verificadas > 0:
            resultados_verificacao[lottery_key] = {
                "ultimo_concurso": ultimo_num,
                "novos_concursos": len(novos_concursos),
                "total_verificacoes": total_verificadas,
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
