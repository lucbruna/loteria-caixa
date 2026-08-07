"""
Servidor Flask - API Backend Atualizado
"""
import json
import os
import threading
import uuid
from datetime import datetime

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

from analyzer import AnalisadorLoteriasAvancado as AnalisadorLoterias
from analyzer_global import AnalisadorGlobal
from analyzer_ultra import AnalisadorUltraAvancado
from api_client import api_client
from config import (
    BASE_DIR,
    CACHE_TTL_DATA,
    CACHE_TTL_ULTIMO,
    FLASK_DEBUG,
    FLASK_HOST,
    FLASK_PORT,
    HISTORICO_PADRAO,
    LOTTERIES,
)
from prediction_storage import (
    _load,
    _ultimo_concurso,
    obter_estatisticas,
    obter_predicoes,
    salvar_predicoes,
    verificar_todas_predicoes,
)

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
CORS(app)


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "img-src 'self' data:; "
        "connect-src 'self' https://servicebus2.caixa.gov.br"
    )
    return response


class NumpyJSONProvider(DefaultJSONProvider):
    """Serializa tipos numpy (int32/float32/ndarray) para JSON."""
    def default(self, o):
        import numpy as np
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


app.json = NumpyJSONProvider(app)

cache_memoria = {}
_dados_cache = {}
cache_lock = threading.Lock()

# Instancia unica do analisador (reutilizada entre requests)
analisador = AnalisadorLoterias()


def obter_dados(lottery: str, count: int = HISTORICO_PADRAO):
    """Busca resultados + estatisticas com cache em memoria (TTL 10 min)"""
    key = (lottery, count)
    with cache_lock:
        if key in _dados_cache:
            cached = _dados_cache[key]
            if (datetime.now() - cached["time"]).total_seconds() < CACHE_TTL_DATA:
                return cached["resultados"], cached["stats"]

    try:
        resultados = api_client.get_historical_results(lottery, count)
    except Exception:
        return None, None
    if not resultados:
        return None, None

    stats = analisador.obter_resumo_estatisticas(resultados, LOTTERIES[lottery])

    with cache_lock:
        _dados_cache[key] = {
            "resultados": resultados,
            "stats": stats,
            "time": datetime.now()
        }
    return resultados, stats


_result_cache = {}


def cachear_resultado(chave, ttl: int, fn):
    """Cacheia o resultado de uma computacao pesada (ex.: modelos Ultra/Global).

    `fn` e executada apenas quando nao ha cache valido. O lock protege o
    acesso concorrente ao cache em memoria.
    """
    with cache_lock:
        if chave in _result_cache:
            cached = _result_cache[chave]
            if (datetime.now() - cached["time"]).total_seconds() < ttl:
                return cached["data"]

    data = fn()

    with cache_lock:
        _result_cache[chave] = {"data": data, "time": datetime.now()}
    return data


def obter_ou_buscar(lottery: str):
    with cache_lock:
        if lottery in cache_memoria:
            cached = cache_memoria[lottery]
            if (datetime.now() - cached["time"]).total_seconds() < CACHE_TTL_ULTIMO:
                return cached["data"]

    try:
        data = api_client.get_latest_result(lottery)
    except Exception:
        return None
    if data:
        with cache_lock:
            cache_memoria[lottery] = {"data": data, "time": datetime.now()}
    return data


@app.route("/")
def index():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "index.html")


@app.route("/mobile")
def mobile():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "mobile.html")


@app.route("/detalhes/<lottery>")
def detalhes(lottery):
    if lottery not in LOTTERIES:
        return "Loteria nao encontrada", 404
    return send_from_directory(os.path.join(BASE_DIR, "static"), "detalhes.html")


@app.route("/static/<path:path>")
def servir_estatico(path):
    return send_from_directory(os.path.join(BASE_DIR, "static"), path)


@app.route("/api/todos-ultimos")
def obter_todos_ultimos():
    resultados = {}
    for lottery in LOTTERIES:
        data = obter_ou_buscar(lottery)
        if data:
            resultados[lottery] = data
    return jsonify(resultados)


@app.route("/api/ultimo/<lottery>")
def obter_ultimo(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    data = obter_ou_buscar(lottery)
    if not data:
        return jsonify({"erro": "Erro ao buscar dados"}), 500

    return jsonify(data)


@app.route("/api/historico/<lottery>/<int:count>")
def obter_historico(lottery, count):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    resultados = api_client.get_historical_results(lottery, min(count, 200))
    return jsonify(resultados)


@app.route("/api/analise/<lottery>")
def obter_analise(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, stats = obter_dados(lottery, 100)

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    sugestoes = analisador.gerar_sugestao_ia(resultados, config, 10)
    salvar_predicoes(lottery, "IA", sugestoes, config)

    return jsonify({
        "loteria": lottery,
        "configuracao": config,
        "estatisticas": stats,
        "sugestoes": sugestoes,
        "concursos_analisados": len(resultados)
    })


@app.route("/api/sugerir/<lottery>/<int:count>")
def sugerir_numeros(lottery, count):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 100)

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    sugestoes = analisador.gerar_sugestao_ia(resultados, config, min(count, 100))
    salvar_predicoes(lottery, "IA", sugestoes, config)
    return jsonify(sugestoes)


@app.route("/api/combinacoes/<lottery>/<int:quantidade>")
def gerar_combinacoes(lottery, quantidade):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    maximo = min(quantidade, 20000)

    resultados, stats = obter_dados(lottery, 100)

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    # Gerar pool de numeros baseado em analise
    pool_quentes = [n for n, _ in stats["frequencia"]["mais_frequentes"][:15]]
    pool_em_alta = []
    for _janela, _dados in stats.get("tendencias", {}).items():
        pool_em_alta.extend(item["numero"] for item in _dados.get("em_alta", []))
    pool_em_alta = pool_em_alta[:10]
    pool_atrasados = []
    for num, info in stats.get("intervalos", {}).items():
        if info.get("atual", 0) > info.get("media", 0) * 1.3:
            pool_atrasados.append(num)
    pool_atrasados = pool_atrasados[:10]

    # Pool combinado com pesos
    pool_principal = list(set(pool_quentes + pool_em_alta + pool_atrasados))

    minimo = config["min_num"]
    maximo_num = config["max_num"]
    qtd_escolher = config["pick_count"]

    pool_total = maximo_num - minimo + 1
    if qtd_escolher > pool_total:
        qtd_escolher = pool_total
    maximo_possivel = 1
    for i in range(qtd_escolher):
        maximo_possivel = maximo_possivel * (pool_total - i) // (i + 1)
    maximo = min(maximo, maximo_possivel)

    combinacoes = []
    vistas = set()

    tentativas = 0
    while len(combinacoes) < maximo and tentativas < maximo * 3:
        tentativas += 1

        # Misturar estrategias
        estrategia = str(np.random.choice(["quente", "tendencia", "atrasado", "aleatorio", "misto"],
                                       p=[0.30, 0.25, 0.20, 0.10, 0.15]))

        if estrategia == "quente" and pool_quentes:
            base = [int(x) for x in np.random.choice(pool_quentes, min(qtd_escolher, len(pool_quentes)), replace=False)]
        elif estrategia == "tendencia" and pool_em_alta:
            base = [int(x) for x in np.random.choice(pool_em_alta, min(qtd_escolher, len(pool_em_alta)), replace=False)]
        elif estrategia == "atrasado" and pool_atrasados:
            base = [int(x) for x in np.random.choice(pool_atrasados, min(qtd_escolher, len(pool_atrasados)), replace=False)]
        elif estrategia == "misto" and pool_principal:
            base = [int(x) for x in np.random.choice(pool_principal, min(qtd_escolher, len(pool_principal)), replace=False)]
        else:
            base = []

        while len(base) < qtd_escolher:
            num = int(np.random.randint(minimo, maximo_num + 1))
            if num not in base:
                base.append(num)
            if len(base) == pool_total:
                break

        base = sorted([int(x) for x in base[:qtd_escolher]])
        chave = tuple(base)

        if chave not in vistas:
            vistas.add(chave)
            confianca = analisador._calcular_confianca(base, stats["frequencia"], stats["conjunta"]["pares"], stats.get("intervalos", {}))
            motivos = analisador._gerar_motivos(base, stats["frequencia"], stats.get("tendencias", {}), stats.get("intervalos", {}))

            combinacoes.append({
                "numeros": base,
                "confianca": round(confianca, 1),
                "estrategia": estrategia,
                "motivos": motivos
            })

    # Ordenar por confianca
    combinacoes.sort(key=lambda x: x["confianca"], reverse=True)
    salvar_predicoes(lottery, "Combinacoes", combinacoes[:maximo], config)

    return jsonify({
        "total_geradas": len(combinacoes),
        "configuracao": config,
        "combinacoes": combinacoes[:maximo]
    })


@app.route("/api/estatisticas/<lottery>")
def api_obter_estatisticas(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, stats = obter_dados(lottery, 100)

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    return jsonify(stats)


@app.route("/api/calculadora-apostas")
def calculadora_apostas():
    calculos = {}
    for chave, config in LOTTERIES.items():
        custo = config["cost_per_bet"]
        calculos[chave] = {
            "nome": config["name"],
            "custo_por_jogo": custo,
            "icone": config["icon"],
            "cor": config["color"],
            "combinacoes": {}
        }

        # Calcular custos para diferentes quantidades
        for qtd in range(config["pick_count"], min(config["pick_count"] + 10, 16)):
            from math import comb
            num_combinacoes = comb(config["max_num"] - config["min_num"] + 1, qtd) if qtd <= (config["max_num"] - config["min_num"] + 1) else 0
            custo_total = num_combinacoes * custo
            calculos[chave]["combinacoes"][qtd] = {
                "qtd_numeros": qtd,
                "total_combinacoes": num_combinacoes,
                "custo_total": round(custo_total, 2)
            }

    return jsonify(calculos)


@app.route("/api/detalhes/<lottery>")
def obter_detalhes(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    ultimo = obter_ou_buscar(lottery)
    resultados, stats = obter_dados(lottery, 100)

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    # Top 10 sugestoes
    sugestoes = analisador.gerar_sugestao_ia(resultados, config, 10)
    salvar_predicoes(lottery, "IA", sugestoes, config)

    return jsonify({
        "loteria": lottery,
        "configuracao": config,
        "ultimo_sorteio": ultimo,
        "estatisticas": stats,
        "sugestoes": sugestoes,
        "concursos_analisados": len(resultados)
    })


@app.route("/api/ultra/<lottery>/<int:quantidade>")
def analise_ultra(lottery, quantidade):
    """Analise ultra avancada com 9 algoritmos de Machine Learning"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    maximo = min(quantidade, 100)

    def _calc():
        resultados, _ = obter_dados(lottery, 150)
        if not resultados:
            return None
        return AnalisadorUltraAvancado().gerar_sugestoes_ultra(resultados, config, maximo)

    resultado = cachear_resultado(("ultra", lottery, maximo), 600, _calc)

    if resultado is None:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    combos = resultado.get("combinacoes", [])
    salvar_predicoes(lottery, "Ultra", combos, config)

    return jsonify({
        "loteria": lottery,
        "configuracao": config,
        "resultado_ultra": resultado,
        "concursos_analisados": len(combos) if isinstance(resultado, dict) else 0
    })


@app.route("/api/global/<lottery>/<int:quantidade>")
def analise_global(lottery, quantidade):
    """Analise global com tecnicas de todas as escolas mundiais"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    maximo = min(quantidade, 100)

    def _calc():
        resultados, _ = obter_dados(lottery, 150)
        if not resultados:
            return None
        return AnalisadorGlobal().gerar_sugestoes_globais(resultados, config, maximo)

    resultado = cachear_resultado(("global", lottery, maximo), 600, _calc)

    if resultado is None:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    combos = resultado.get("combinacoes", [])
    salvar_predicoes(lottery, "Global", combos, config)

    return jsonify({
        "loteria": lottery,
        "configuracao": config,
        "resultado_global": resultado,
        "concursos_analisados": len(combos) if isinstance(resultado, dict) else 0
    })


@app.route("/api/worldclass/<lottery>/<int:quantidade>")
def analise_worldclass(lottery, quantidade):
    """Analise World-Class: Regressao Logistica, ARIMA, Gradient Boosting, Distribuicao"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    maximo = min(quantidade, 50)

    def _calc():
        resultados, _ = obter_dados(lottery, 200)
        if not resultados or len(resultados) < 20:
            return None
        from analise_worldclass import AnaliseWorldClass
        analise = AnaliseWorldClass(config["min_num"], config["max_num"], config["pick_count"])
        resultados_int = [[int(d) for d in r.get("listaDezenas", [])] for r in resultados]
        return analise.ensemble_world_class(resultados_int, janela=10)

    resultado = cachear_resultado(("worldclass", lottery, maximo), 900, _calc)

    if resultado is None:
        return jsonify({"erro": "Dados insuficientes (minimo 20 concursos)"}), 404

    # Gerar combinacoes a partir das probabilidades finais
    probs = resultado.get("probabilidades_finais", {})
    if probs:
        probabilidades_ordenadas = sorted(probs.items(), key=lambda x: float(x[1]), reverse=True)
        numeros_top = [int(k) for k, _ in probabilidades_ordenadas[:config["pick_count"]]]
        numeros_top.sort()
        combos = [{
            "numeros": numeros_top,
            "confianca": 50,
            "estrategia": "worldclass_ensemble",
            "fonte": "WorldClass"
        }]
        salvar_predicoes(lottery, "WorldClass", combos, config)
    else:
        combos = []

    return jsonify({
        "loteria": lottery,
        "configuracao": config,
        "resultado_worldclass": resultado,
        "combinacoes_geradas": combos,
        "concursos_analisados": 200,
    })


@app.route("/api/loterias_mundiais")
def obter_loterias_mundiais():
    """Retorna todas as loterias mundiais"""
    from loterias_mundiais import ESTRATEGIAS_GLOBAIS, LOTERIAS_MUNDIAIS, TECNICAS_ANALISE_MUNDIAL

    return jsonify({
        "total_loterias": len(LOTERIAS_MUNDIAIS),
        "loterias": LOTERIAS_MUNDIAIS,
        "tecnicas": TECNICAS_ANALISE_MUNDIAL,
        "estrategias": ESTRATEGIAS_GLOBAIS
    })


@app.route("/api/tecnologias")
def obter_tecnologias():
    """Retorna todas as tecnologias globais de analise"""
    from tecnologias_globais import TecnologiasGlobais

    tech = TecnologiasGlobais()

    return jsonify({
        "formulas": {
            "combinatoria": "C(n,k) = n! / (k! * (n-k)!)",
            "probabilidade": "P(acertos) = C(T,M) * C(P-T, W-M) / C(P,W)",
            "odds_jackpot": "1 / C(P,W)"
        },
        "estrategias_comprovadas": [
            tech.estrategia_syndicate_profissional(),
            tech.estrategia_delta_system(),
            tech.estrategia_ottosen(),
            tech.estrategia_gail_howard(),
            tech.estrategia_lottery_expert()
        ],
        "estatisticas_loterias": tech.ESTATISTICAS_LOTERIAS
    })


@app.route("/api/calcular_odds/<int:p>/<int:w>/<int:m>")
def calcular_odds(p, w, m):
    """Calcula odds para qualquer configuracao de loteria"""
    from tecnologias_globais import TecnologiasGlobais

    tech = TecnologiasGlobais()

    odds = tech.calcular_odds_jackpot(p, w)
    prob_acerto = tech.calcular_probabilidade_combinatoria(p, w, w, m)

    return jsonify({
        "configuracao": {"p": p, "w": w, "m": m},
        "odds_jackpot": odds,
        "probabilidade_acertos": {
            "m_acertos": m,
            "probabilidade": round(prob_acerto, 8),
            "percentual": round(prob_acerto * 100, 6),
            "odds": f"1 em {round(1/prob_acerto):,}" if prob_acerto > 0 else "1 em infinito"
        }
    })


@app.route("/api/tecnologias_avancadas/<lottery>")
def obter_tecnologias_avancadas(lottery):
    """Retorna resultados de todas as tecnologias avancadas"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 100)

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    def _calc():
        from tecnologias_adicionais import TecnologiasAdicionais
        tech = TecnologiasAdicionais()
        return {
            "lstm": tech.lstm_simplificado(resultados, config),
            "q_learning": tech.q_learning_loteria(resultados, config),
            "fuzzy_logic": tech.fuzzy_logic_loteria(resultados, config),
            "chaos_theory": tech.chaos_theory_loteria(resultados, config),
            "wavelet": tech.wavelet_analysis(resultados, config),
            "kmeans": tech.kmeans_clustering(resultados, config),
            "pca": tech.pca_analysis(resultados, config),
            "bayesian": tech.bayesian_optimization(resultados, config),
            "stacking": tech.ensemble_stacking(resultados, config),
            "fractal": tech.fractal_analysis(resultados, config)
        }

    tecnologias = cachear_resultado(("tecnologias_avancadas", lottery), 600, _calc)

    if tecnologias is None:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    return jsonify({
        "loteria": lottery,
        "tecnologias": tecnologias,
        "concursos_analisados": len(resultados)
    })


@app.route("/api/backtest/<lottery>/<int:janelas>")
def backtest(lottery, janelas):
    """Backtest walk-forward da IA"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 200)

    if not resultados or len(resultados) < janelas + 10:
        return jsonify({"erro": "Dados insuficientes para backtest"}), 404

    from funcionalidades_avancadas import FuncionalidadesAvancadas
    func = FuncionalidadesAvancadas()
    resultado = func.backtest_walk_forward(resultados, config, janelas)

    return jsonify(resultado)


@app.route("/api/kelly")
def kelly():
    """Calcula Kelly Criterion"""
    try:
        custo = float(request.args.get('custo', 5))
        premio = float(request.args.get('premio', 5000000))
        probabilidade = float(request.args.get('probabilidade', 0.0000001))
    except (ValueError, TypeError):
        return jsonify({"erro": "Parametros invalidos"}), 400

    from funcionalidades_avancadas import FuncionalidadesAvancadas
    func = FuncionalidadesAvancadas()
    resultado = func.kelly_criterion(custo, premio, probabilidade)
    return jsonify(resultado)


@app.route("/api/wheeling/<lottery>/<int:qtd_jogos>")
def wheeling(lottery, qtd_jogos):
    """Gera fechamento/wheeling otimizado"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 100)

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    # Usar numeros mais frequentes como base
    from collections import Counter
    historico = Counter()
    for r in resultados:
        for d in r.get("listaDezenas", []):
            historico[int(d)] += 1

    base = [n for n, _ in historico.most_common(config["pick_count"] + 4)]

    from funcionalidades_avancadas import FuncionalidadesAvancadas
    func = FuncionalidadesAvancadas()
    resultado = func.wheeling_otimizado(base, qtd_jogos, config)

    return jsonify(resultado)


@app.route("/api/auto_tune/<lottery>")
def auto_tune(lottery):
    """Auto-tune de hiperparametros"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 50)  # Reduzido para velocidade

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    from funcionalidades_avancadas import FuncionalidadesAvancadas
    func = FuncionalidadesAvancadas()
    resultado = func.auto_tune(resultados, config)

    return jsonify(resultado)


@app.route("/api/gerar_jogos/<lottery>/<int:quantidade>")
def gerar_jogos_inteligentes(lottery, quantidade):
    """Gera jogos inteligentes com todas as tecnicas"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 100)

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    from funcionalidades_avancadas import FuncionalidadesAvancadas
    func = FuncionalidadesAvancadas()
    jogos = func.gerar_jogos_inteligentes(resultados, config, min(quantidade, 50))
    salvar_predicoes(lottery, "Inteligente", jogos, config)

    return jsonify({
        "loteria": lottery,
        "jogos_gerados": len(jogos),
        "jogos": jogos
    })


@app.route("/api/importar_csv", methods=['POST'])
def importar_csv():
    """Importa historico de CSV"""
    data = request.get_json()
    conteudo = data.get('conteudo', '')
    lottery = data.get('loteria', 'megasena')

    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]

    from funcionalidades_avancadas import FuncionalidadesAvancadas
    func = FuncionalidadesAvancadas()
    resultado = func.importar_csv(conteudo, config)

    return jsonify(resultado)


@app.route("/api/ensemble/<lottery>")
def ensemble_completo(lottery):
    """Ensemble completo com todas as analises"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 50)  # Reduzido para velocidade

    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    def _calc():
        from analyzer_global import AnalisadorGlobal
        from analyzer_ultra import AnalisadorUltraAvancado
        from funcionalidades_avancadas import FuncionalidadesAvancadas

        ultra = AnalisadorUltraAvancado()
        global_analyzer = AnalisadorGlobal()
        func = FuncionalidadesAvancadas()

        # Gerar jogos de cada metodo
        jogos_ia = ultra.gerar_sugestoes_ultra(resultados, config, 10)
        jogos_global = global_analyzer.gerar_sugestoes_globais(resultados, config, 10)
        jogos_func = func.gerar_jogos_inteligentes(resultados, config, 10)

        # Combinar e rankear
        todos_jogos = []

        for j in jogos_ia.get("combinacoes", []):
            score = func.ensemble_scorer_avancado(j["numeros"], resultados, config)
            todos_jogos.append({
                "numeros": j["numeros"],
                "fonte": "Ultra IA",
                "score": score["score_final"]
            })

        for j in jogos_global.get("combinacoes", []):
            score = func.ensemble_scorer_avancado(j["numeros"], resultados, config)
            todos_jogos.append({
                "numeros": j["numeros"],
                "fonte": "Global",
                "score": score["score_final"]
            })

        for j in jogos_func:
            todos_jogos.append({
                "numeros": j["numeros"],
                "fonte": "Inteligente",
                "score": j["score"]
            })

        # Ordenar por score
        todos_jogos.sort(key=lambda x: x["score"], reverse=True)

        return {
            "loteria": lottery,
            "total_jogos": len(todos_jogos),
            "top_20": todos_jogos[:20]
        }

    return jsonify(cachear_resultado(("ensemble", lottery), 600, _calc))


# ==========================================
# ENDPOINTS DE PREDICOES / RESULTADOS
# ==========================================


@app.route("/api/predicoes/todas")
def api_obter_todas_predicoes():
    return jsonify(obter_predicoes())


@app.route("/api/predicoes/<lottery>")
def api_obter_predicoes(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404
    return jsonify(obter_predicoes(lottery))


@app.route("/api/estatisticas-predicoes")
def api_estatisticas_predicoes():
    return jsonify(obter_estatisticas())


@app.route("/api/estatisticas-predicoes/<lottery>")
def api_estatisticas_predicoes_loteria(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404
    return jsonify(obter_estatisticas(lottery))


@app.route("/api/verificar-resultados", methods=["POST"])
def api_verificar_resultados():
    """Verifica todas as predicoes nao verificadas contra o ultimo sorteio"""
    resultado = verificar_todas_predicoes(api_client)
    return jsonify(resultado)


@app.route("/api/resultados-simulacao/<lottery>")
def api_resultados_simulacao(lottery):
    """Retorna resultados de simulacoes agrupados por tipo/fonte para uma loteria especifica"""
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    predicoes = obter_predicoes(lottery)
    preds = predicoes.get("predicoes", [])

    if not preds:
        return jsonify({
            "loteria": lottery,
            "configuracao": LOTTERIES[lottery],
            "total_preditos": 0,
            "total_verificados": 0,
            "por_tipo": {},
            "concursos_verificados": [],
        })

    max_concurso_verif = 0
    for p in preds:
        for v in p.get("verificacoes", []):
            if v.get("concurso", 0) > max_concurso_verif:
                max_concurso_verif = v["concurso"]

    ultimo = api_client.get_latest_result(lottery)
    ultimo_num = ultimo.get("numero", 0) if ultimo else 0

    concursos_com_resultado = []
    if max_concurso_verif > 0 and ultimo_num > max_concurso_verif:
        novos = list(range(max_concurso_verif + 1, ultimo_num + 1))
        concursos_dados = api_client._fetch_concursos_paralelo(lottery, novos)
        for c in concursos_dados:
            n = c.get("numero")
            if n:
                concursos_com_resultado.append({
                    "concurso": n,
                    "numeros_sorteados": sorted(int(d) for d in c.get("listaDezenas", [])),
                    "data": c.get("dataApuracao", ""),
                })
    concursos_com_resultado.sort(key=lambda x: x["concurso"])

    grupos = {}
    total_verificados = 0
    total_nao_verificados = 0

    for p in preds:
        fonte = p.get("fonte", "Desconhecida")
        if fonte not in grupos:
            grupos[fonte] = {
                "total": 0,
                "verificadas": 0,
                "jogos": [],
            }
        grupos[fonte]["total"] += 1

        verificacoes = p.get("verificacoes", [])
        if verificacoes:
            grupos[fonte]["verificadas"] += 1
            total_verificados += 1
        else:
            total_nao_verificados += 1

        grupos[fonte]["jogos"].append({
            "id": p.get("id", ""),
            "data": p.get("data", ""),
            "numeros": p.get("numeros", []),
            "confianca": p.get("confianca", 0),
            "estrategia": p.get("estrategia", ""),
            "concurso_criacao": p.get("concurso_criacao"),
            "verificacoes": verificacoes,
            "pendente": len(verificacoes) == 0,
        })

    return jsonify({
        "loteria": lottery,
        "configuracao": LOTTERIES[lottery],
        "ultimo_concurso": ultimo_num,
        "total_preditos": len(preds),
        "total_verificados": total_verificados,
        "total_pendentes": total_nao_verificados,
        "concursos_com_resultado": concursos_com_resultado,
        "por_tipo": grupos,
    })


@app.route("/api/resultados-simulacao")
def api_resultados_simulacao_geral():
    """Retorna resultados de simulacoes de todas as loterias agrupados por tipo/fonte"""
    from config import LOTTERIES
    data = _load()
    resultado_geral = {}

    for lottery_key in list(data.keys()):
        if lottery_key not in LOTTERIES:
            continue
        preds = data[lottery_key].get("predicoes", [])
        if not preds:
            continue

        max_concurso_verif = 0
        for p in preds:
            for v in p.get("verificacoes", []):
                if v.get("concurso", 0) > max_concurso_verif:
                    max_concurso_verif = v["concurso"]

        ultimo = api_client.get_latest_result(lottery_key)
        ultimo_num = ultimo.get("numero", 0) if ultimo else 0

        concursos_com_resultado = []
        if max_concurso_verif > 0 and ultimo_num > max_concurso_verif:
            novos = list(range(max_concurso_verif + 1, ultimo_num + 1))
            concursos_dados = api_client._fetch_concursos_paralelo(lottery_key, novos)
            for c in concursos_dados:
                n = c.get("numero")
                if n:
                    concursos_com_resultado.append({
                        "concurso": n,
                        "numeros_sorteados": sorted(int(d) for d in c.get("listaDezenas", [])),
                        "data": c.get("dataApuracao", ""),
                    })
        concursos_com_resultado.sort(key=lambda x: x["concurso"])

        grupos = {}
        total_verificados = 0
        total_nao_verificados = 0

        for p in preds:
            fonte = p.get("fonte", "Desconhecida")
            if fonte not in grupos:
                grupos[fonte] = {"total": 0, "verificadas": 0, "jogos": []}
            grupos[fonte]["total"] += 1

            verificacoes = p.get("verificacoes", [])
            if verificacoes:
                grupos[fonte]["verificadas"] += 1
                total_verificados += 1
            else:
                total_nao_verificados += 1

            grupos[fonte]["jogos"].append({
                "id": p.get("id", ""),
                "data": p.get("data", ""),
                "numeros": p.get("numeros", []),
                "confianca": p.get("confianca", 0),
                "estrategia": p.get("estrategia", ""),
                "concurso_criacao": p.get("concurso_criacao"),
                "verificacoes": verificacoes,
                "pendente": len(verificacoes) == 0,
            })

        resultado_geral[lottery_key] = {
            "configuracao": LOTTERIES[lottery_key],
            "ultimo_concurso": ultimo_num,
            "total_preditos": len(preds),
            "total_verificados": total_verificados,
            "total_pendentes": total_nao_verificados,
            "concursos_com_resultado": concursos_com_resultado,
            "por_tipo": grupos,
        }

    return jsonify(resultado_geral)


@app.route("/api/simular", methods=["POST"])
def api_criar_simulacao():
    """Cria uma nova simulacao de jogos"""
    data = request.get_json()
    lottery = data.get("loteria", "lotofacil")
    nome = data.get("nome", "") or "Simulacao " + lottery
    try:
        quantidade = int(data.get("quantidade", 10))
    except (TypeError, ValueError):
        quantidade = 10
    quantidade = max(1, min(quantidade, 5000))
    metodo = data.get("metodo", "IA")

    config = LOTTERIES.get(lottery)
    if not config:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    resultados, stats = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    sugestoes = []
    if metodo == "IA":
        sugestoes = analisador.gerar_sugestao_ia(resultados, config, quantidade)
        salvar_predicoes(lottery, "IA", sugestoes, config)
    elif metodo == "Ultra":
        ultra = AnalisadorUltraAvancado()
        combos = ultra.gerar_sugestoes_ultra(resultados, config, quantidade)
        sugestoes = combos.get("combinacoes", [])
        salvar_predicoes(lottery, "Ultra", sugestoes, config)
    elif metodo == "Global":
        global_analyzer = AnalisadorGlobal()
        combos = global_analyzer.gerar_sugestoes_globais(resultados, config, quantidade)
        sugestoes = combos.get("combinacoes", [])
        salvar_predicoes(lottery, "Global", sugestoes, config)
    elif metodo == "Combinacoes":
        combinacoes = gerar_combinacoes_ia(resultados, config, quantidade, stats)
        sugestoes = combinacoes.get("combinacoes", [])
        salvar_predicoes(lottery, "Combinacoes", sugestoes, config)
    elif metodo in ("lstm", "qlearning", "fuzzy", "chaos", "wavelet", "kmeans", "pca", "bayesian", "stacking", "fractal"):
        return jsonify({"erro": "Use a aba Analise Avancada para essas tecnologias", "metodo": metodo, "rota": "/api/tecnologia/" + lottery + "/" + metodo}), 400
    else:
        return jsonify({"erro": "Metodo nao reconhecido"}), 400

    # Gerar ID da simulacao
    simulacao_id = str(uuid.uuid4())[:8] if 'uuid' in dir() else nome.lower().replace(' ', '_')

    return jsonify({
        "status": "ok",
        "simulacao_id": simulacao_id,
        "nome": nome,
        "loteria": lottery,
        "metodo": metodo,
        "gerados": len(sugestoes),
        "concurso_criacao": None,
    })


def gerar_combinacoes_ia(resultados, config, quantidade, stats):
    """Gera combinacoes de IA para simulacao"""
    import numpy as np
    from collections import Counter
    minimo = config["min_num"]
    maximo_num = config["max_num"]
    qtd_escolher = config["pick_count"]

    historico = Counter()
    for r in resultados:
        for d in r.get("listaDezenas", []):
            historico[int(d)] += 1

    pool_quentes = [n for n, _ in historico.most_common(15)]
    pool_principal = list(set(pool_quentes))

    combinacoes = []
    vistas = set()
    tentativas = 0
    while len(combinacoes) < quantidade and tentativas < quantidade * 3:
        tentativas += 1
        base = []
        while len(base) < qtd_escolher:
            num = int(np.random.choice(pool_principal) if pool_principal else np.random.randint(minimo, maximo_num + 1))
            if num not in base:
                base.append(num)
        base = sorted([int(x) for x in base[:qtd_escolher]])
        chave = tuple(base)
        if chave not in vistas:
            vistas.add(chave)
            confianca = analisador._calcular_confianca(
                base, stats["frequencia"], stats["conjunta"]["pares"], stats.get("intervalos", {})
            )
            combinacoes.append({"numeros": base, "confianca": round(confianca, 1), "estrategia": "simulacao"})
        if not pool_principal:
            break

    return {"total_geradas": len(combinacoes), "combinacoes": combinacoes}


@app.route("/api/simulacoes")
def api_listar_simulacoes():
    """Lista todas as simulacoes com filtros"""
    from prediction_storage import _load
    data = _load()
    loteria_filter = request.args.get('loteria', '')
    metodo_filter = request.args.get('metodo', '')
    status_filter = request.args.get('status', '')

    todas_simulacoes = []
    for lottery_key in data:
        preds = data[lottery_key].get("predicoes", [])
        for p in preds:
            fonte = p.get("fonte", "Desconhecida")
            verificacoes = p.get("verificacoes", [])
            pendentes = len(verificacoes) == 0

            if loteria_filter and lottery_key != loteria_filter:
                continue
            if metodo_filter and fonte != metodo_filter:
                continue
            if status_filter == "pendente" and not pendentes:
                continue
            if status_filter == "verificado" and pendentes:
                continue

            todas_simulacoes.append({
                "id": p.get("id", ""),
                "nome": p.get("nome", f"Simulacao {fonte} #{p.get('concurso_criacao', '?')}"),
                "loteria": lottery_key,
                "metodo": fonte,
                "total": len(p.get("numeros", [])),
                "concurso_criacao": p.get("concurso_criacao"),
                "verificadas": len(verificacoes),
                "pendente": pendentes,
                "data": p.get("data", ""),
            })

    return jsonify(todas_simulacoes)


@app.route("/api/evolucao-acertos")
def api_evolucao_acertos():
    """Retorna dados para grafico de evolucao de acertos por tipo"""
    from prediction_storage import _load
    data = _load()
    resultado = {}

    for lottery_key in data:
        preds = data[lottery_key].get("predicoes", [])
        for p in preds:
            fonte = p.get("fonte", "Outro")
            if fonte not in resultado:
                resultado[fonte] = {}
            for v in p.get("verificacoes", []):
                concurso = v.get("concurso", 0)
                acertos = v.get("acertos", 0)
                if concurso not in resultado[fonte]:
                    resultado[fonte][concurso] = []
                resultado[fonte][concurso].append(acertos)

    # Agregar por concurso (media)
    evolucao = {}
    for fonte, concursos in resultado.items():
        evolucao[fonte] = []
        for concurso in sorted(concursos.keys()):
            acertos = concursos[concurso]
            media = sum(acertos) / len(acertos) if acertos else 0
            evolucao[fonte].append({"concurso": concurso, "media_acertos": round(media, 2), "total_jogos": len(acertos)})

    return jsonify(evolucao)


@app.route("/api/distribuicao-acertos")
def api_distribuicao_acertos():
    """Retorna distribuicao de acertos por tipo de simulacao"""
    from prediction_storage import _load
    data = _load()
    resultado = {}

    for lottery_key in data:
        preds = data[lottery_key].get("predicoes", [])
        for p in preds:
            fonte = p.get("fonte", "Outro")
            for v in p.get("verificacoes", []):
                acertos = v.get("acertos", 0)
                if fonte not in resultado:
                    resultado[fonte] = {}
                resultado[fonte][str(acertos)] = resultado[fonte].get(str(acertos), 0) + 1

    return jsonify(resultado)


@app.route("/api/performance-tipos")
def api_performance_tipos():
    """Retorna performance comparativa por tipo de simulacao"""
    from prediction_storage import _load
    data = _load()
    resultado = {}

    for lottery_key in data:
        preds = data[lottery_key].get("predicoes", [])
        for p in preds:
            fonte = p.get("fonte", "Outro")
            if fonte not in resultado:
                resultado[fonte] = {"total_acertos": 0, "total_verificadas": 0, "max_acertos": 0}
            for v in p.get("verificacoes", []):
                resultado[fonte]["total_acertos"] += v.get("acertos", 0)
                resultado[fonte]["total_verificadas"] += 1
                resultado[fonte]["max_acertos"] = max(resultado[fonte]["max_acertos"], v.get("acertos", 0))

    # Calcular media
    for fonte, stats in resultado.items():
        total_v = stats["total_verificadas"]
        stats["media_acertos"] = round(stats["total_acertos"] / total_v, 2) if total_v > 0 else 0

    return jsonify(resultado)


@app.route("/api/comparar-simulacoes/<id_a>/<id_b>")
def api_comparar_simulacoes(id_a, id_b):
    """Compara duas simulacoes lado a lado"""
    from prediction_storage import _load
    data = _load()

    sim_a = None
    sim_b = None
    for lottery_key in data:
        for p in data[lottery_key].get("predicoes", []):
            if p.get("id") == id_a:
                sim_a = p
            if p.get("id") == id_b:
                sim_b = p

    if not sim_a or not sim_b:
        return jsonify({"erro": "Simulacao nao encontrada"}), 404

    def calc_stats(sim):
        verificacoes = sim.get("verificacoes", [])
        verificadas = len(verificacoes)
        acertos = [v.get("acertos", 0) for v in verificacoes]
        return {
            "total": verificadas,
            "media_acertos": round(sum(acertos) / len(acertos), 2) if acertos else 0,
            "max_acertos": max(acertos) if acertos else 0,
        }

    def get_metodo(sim):
        return sim.get("fonte", "Desconhecido")

    def get_loteria(sim):
        for k in data:
            for p in data[k].get("predicoes", []):
                if p.get("id") == sim.get("id"):
                    return k
        return "?"

    return jsonify({
        "a_nome": "Simulacao " + id_a,
        "b_nome": "Simulacao " + id_b,
        "a_loteria": get_loteria(sim_a), "b_loteria": get_loteria(sim_b),
        "a_metodo": get_metodo(sim_a), "b_metodo": get_metodo(sim_b),
        "a_total": len(sim_a.get("numeros", [])), "b_total": len(sim_b.get("numeros", [])),
        "a_verificadas": calc_stats(sim_a)["total"], "b_verificadas": calc_stats(sim_b)["total"],
        "a_media": calc_stats(sim_a)["media_acertos"], "b_media": calc_stats(sim_b)["media_acertos"],
        "a_max": calc_stats(sim_a)["max_acertos"], "b_max": calc_stats(sim_b)["max_acertos"],
    })


@app.route("/api/exportar-simulacoes")
def api_exportar_simulacoes():
    """Exporta simulacoes em CSV ou JSON"""
    from prediction_storage import _load
    formato = request.args.get('formato', 'csv')
    escopo = request.args.get('escopo', 'todas')
    loteria_filter = request.args.get('loteria', '')

    data = _load()
    linhas = []
    if formato == 'csv':
        linhas.append("Nome,Loteria,Metodo,Jogos,Concurso,Status,Data")

    for lottery_key in data:
        if loteria_filter and lottery_key != loteria_filter:
            continue
        preds = data[lottery_key].get("predicoes", [])
        for p in preds:
            verificacoes = p.get("verificacoes", [])
            pendentes = len(verificacoes) == 0

            if escopo == "verificadas" and pendentes:
                continue
            if escopo == "pendentes" and not pendentes:
                continue

            nome = "Simulacao " + (p.get("fonte", ""))
            if formato == 'csv':
                status = "Pendente" if pendentes else "Verificado"
                linhas.append('"{}","{}","{}",{},{},{},"{}"'.format(
                    nome, lottery_key, p.get("fonte", ""),
                    len(verificacoes), p.get("concurso_criacao", "?"), status, p.get("data", "")
                ))
            else:
                linhas.append(json.dumps({
                    "nome": nome, "loteria": lottery_key, "metodo": p.get("fonte", ""),
                    "total": len(verificacoes), "concurso": p.get("concurso_criacao", "?"),
                    "pendente": pendentes, "data": p.get("data", ""),
                }, ensure_ascii=False))

    conteudo = "\n".join(linhas)
    extensao = "csv" if formato == 'csv' else "json"
    mime = "text/csv" if formato == 'csv' else "application/json"

    resp = app.response_class(
        response=conteudo,
        status=200,
        mimetype=mime,
        headers={"Content-Disposition": "attachment; filename=simulacoes.{}.{}".format(formato, extensao)}
    )
    return resp


@app.route("/simulacao")
def pagina_simulacao():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "simulacao.html")


@app.route("/backtest")
def pagina_backtest():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "backtest.html")


@app.route("/api/resultados")
def api_resultados():
    """Pagina de resultados de predicoes"""
    return send_from_directory(os.path.join(BASE_DIR, "static"), "resultados.html")




# ==========================================
# ROTAS DE TECNOLOGIAS AVANCADAS INDIVIDUAIS
# ==========================================

@app.route("/api/tecnologia/<lottery>/<tech>")
def tecnologia_individual(lottery, tech):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    tech_map = {
        "lstm": "lstm_simplificado",
        "qlearning": "q_learning_loteria",
        "fuzzy": "fuzzy_logic_loteria",
        "chaos": "chaos_theory_loteria",
        "wavelet": "wavelet_analysis",
        "kmeans": "kmeans_clustering",
        "pca": "pca_analysis",
        "bayesian": "bayesian_optimization",
        "stacking": "ensemble_stacking",
        "fractal": "fractal_analysis",
    }

    if tech not in tech_map:
        return jsonify({"erro": "Tecnologia nao encontrada", "disponiveis": list(tech_map.keys())}), 404

    def _calc():
        from tecnologias_adicionais import TecnologiasAdicionais
        t = TecnologiasAdicionais()
        method = getattr(t, tech_map[tech])
        return method(resultados, config)

    result = cachear_resultado(("tecnologia", lottery, tech), 600, _calc)
    if result is None:
        return jsonify({"erro": "Erro ao processar"}), 500
    return jsonify({"loteria": lottery, "tecnologia": tech, "resultado": result})


@app.route("/api/monte-carlo/<lottery>")
def monte_carlo_simulation(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    pool_numeros = list(range(config["min_num"], config["max_num"] + 1))
    qtd_sorteados = config["pick_count"]

    def _calc():
        from random import sample, seed
        from collections import Counter
        seed(42)

        numeros_historicos = set()
        for concurso in resultados[-20:]:
            for d in concurso.get("listaDezenas", []):
                numeros_historicos.add(int(d))

        jogos_aleatorio = []
        jogos_frequencia = []
        jogos_ia = []

        for _ in range(1000):
            jogos_aleatorio.append(sorted(sample(pool_numeros, qtd_sorteados)))

        freq = Counter()
        for concurso in resultados:
            for d in concurso.get("listaDezenas", []):
                freq[int(d)] += 1
        top_nums = [n for n, _ in freq.most_common(qtd_sorteados * 2)]
        for _ in range(1000):
            jogo = sorted(sample(top_nums, min(qtd_sorteados, len(top_nums))))
            while len(jogo) < qtd_sorteados:
                extra = [n for n in pool_numeros if n not in jogo]
                jogo.append(sample(extra, 1)[0])
            jogos_frequencia.append(sorted(jogo[:qtd_sorteados]))

        recent_nums = set()
        for concurso in resultados[-10:]:
            recent_nums.update(int(d) for d in concurso.get("listaDezenas", []))
        for _ in range(1000):
            base = list(recent_nums)[:min(qtd_sorteados, len(recent_nums))]
            if len(base) < qtd_sorteados:
                extras = sample([n for n in pool_numeros if n not in base], qtd_sorteados - len(base))
                jogos_ia.append(sorted(base + extras))
            else:
                jogos_ia.append(sorted(sample(base, qtd_sorteados)))

        def contar_acertos(jogos, resultados_ref):
            acertos = []
            for jogo in jogos:
                melhor = 0
                for concurso in resultados_ref[-20:]:
                    a = len(set(jogo) & set(int(d) for d in concurso.get("listaDezenas", [])))
                    melhor = max(melhor, a)
                acertos.append(melhor)
            return acertos

        historico = resultados[-20:]
        acertos_aleatorio = contar_acertos(jogos_aleatorio, historico)
        acertos_frequencia = contar_acertos(jogos_frequencia, historico)
        acertos_ia = contar_acertos(jogos_ia, historico)

        melhor = max([
            ("aleatorio", sum(acertos_aleatorio) / len(acertos_aleatorio)),
            ("frequencia", sum(acertos_frequencia) / len(acertos_frequencia)),
            ("ia", sum(acertos_ia) / len(acertos_ia))
        ], key=lambda x: x[1])

        return {
            "iteracoes": 3000,
            "ultimos_concursos_analisados": 20,
            "resultados": {
                "aleatorio": {"media_acertos": round(sum(acertos_aleatorio) / len(acertos_aleatorio), 2), "max_acertos": max(acertos_aleatorio)},
                "frequencia": {"media_acertos": round(sum(acertos_frequencia) / len(acertos_frequencia), 2), "max_acertos": max(acertos_frequencia)},
                "ia": {"media_acertos": round(sum(acertos_ia) / len(acertos_ia), 2), "max_acertos": max(acertos_ia)}
            },
            "melhor_estrategia": melhor[0]
        }

    result = cachear_resultado(("monte_carlo", lottery), 300, _calc)
    if result is None:
        return jsonify({"erro": "Erro ao processar"}), 500
    return jsonify({"loteria": lottery, "monte_carlo": result})


@app.route("/api/bias-detector/<lottery>")
def bias_detector(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404

    config = LOTTERIES[lottery]
    resultados, _ = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404

    total_numeros = config["max_num"] - config["min_num"] + 1
    qtd_sorteados = config["pick_count"]

    def _calc():
        from collections import Counter
        import math

        freq = Counter()
        for concurso in resultados:
            for d in concurso.get("listaDezenas", []):
                freq[int(d)] += 1

        total_sorteios = len(resultados)
        esperado_per_num = total_sorteios * qtd_sorteados / total_numeros

        chi2 = sum((f - esperado_per_num) ** 2 / esperado_per_num for f in freq.values())
        gl = total_numeros - 1

        observadas = sorted(freq.values())
        n = len(observadas)
        cdf_obs = [i / n for i in range(1, n + 1)]
        cdf_exp = [min(1.0, (f / esperado_per_num)) for f in observadas]
        ks_stat = max(abs(a - b) for a, b in zip(cdf_obs, cdf_exp)) if freq else 0

        media_freq = sum(freq.values()) / len(freq) if freq else 0
        desvio = math.sqrt(sum((f - media_freq) ** 2 for f in freq.values()) / len(freq)) if freq else 0

        quentes = sorted(freq.items(), key=lambda x: -x[1])[:10]
        frios = sorted(freq.items(), key=lambda x: x[1])[:10]

        total = sum(freq.values())
        entropy = -sum((c / total) * math.log2(c / total) for c in freq.values() if c > 0) if total > 0 else 0
        entropy_max = math.log2(total_numeros)
        entropy_norm = entropy / entropy_max if entropy_max > 0 else 0

        chisq_ratio = chi2 / gl if gl > 0 else 0

        return {
            "total_sorteios": total_sorteios,
            "numero_total_numeros": total_numeros,
            "chisquare": round(chi2, 2),
            "chisq_ratio": round(chisq_ratio, 3),
            "interpretacao": "Uniforme" if chisq_ratio < 2.0 else "Leve viés" if chisq_ratio < 4.0 else "Viés detectado",
            "graus_liberdade": gl,
            "ks_statistic": round(ks_stat, 4),
            "entropia": round(entropy, 3),
            "entropia_normalizada": round(entropy_norm, 3),
            "entropia_maxima": round(entropy_max, 3),
            "desvio_padrao_frequencia": round(desvio, 2),
            "media_frequencia": round(media_freq, 2),
            "top10_quentes": [{"numero": n, "frequencia": f} for n, f in quentes],
            "top10_frios": [{"numero": n, "frequencia": f} for n, f in frios],
            "distribuicao_uniforme": "Sim" if chisq_ratio < 2.0 else "Nao"
        }

    result = cachear_resultado(("bias", lottery), 600, _calc)
    if result is None:
        return jsonify({"erro": "Erro ao processar"}), 500
    return jsonify({"loteria": lottery, "bias_detector": result})


@app.route("/analise-avancada")
def pagina_analise_avancada():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "analise-avancada.html")


@app.route("/api/ml-complete/<lottery>")
def ml_complete(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404
    resultados, _ = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404
    config = LOTTERIES[lottery]

    def _calc():
        from tecnologias_ml import executar_analise_completa
        return executar_analise_completa(resultados, config)

    result = cachear_resultado(("ml_complete", lottery), 600, _calc)
    if result is None:
        return jsonify({"erro": "Erro ao processar"}), 500
    return jsonify({"loteria": lottery, "analise_ml": result})


@app.route("/api/ml/regression/<lottery>")
def ml_regression(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404
    resultados, _ = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404
    config = LOTTERIES[lottery]

    def _calc():
        from tecnologias_ml import RegressaoLogistica
        return RegressaoLogistica(C=1.0, penalty='l2').analisar(resultados, config)

    result = cachear_resultado(("ml_regression", lottery), 600, _calc)
    if result is None:
        return jsonify({"erro": "Erro ao processar"}), 500
    return jsonify({"loteria": lottery, "regressao_logistica": result})


@app.route("/api/ml/arima/<lottery>")
def ml_arima(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404
    resultados, _ = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404
    config = LOTTERIES[lottery]

    def _calc():
        from tecnologias_ml import ArimaReal
        return ArimaReal(ordem=(2, 1, 2)).analisar(resultados, config)

    result = cachear_resultado(("ml_arima", lottery), 600, _calc)
    if result is None:
        return jsonify({"erro": "Erro ao processar"}), 500
    return jsonify({"loteria": lottery, "arima": result})


@app.route("/api/ml/poisson/<lottery>")
def ml_poisson(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404
    resultados, _ = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404
    config = LOTTERIES[lottery]

    def _calc():
        from tecnologias_ml import DistribuicaoPoisson
        return DistribuicaoPoisson().analisar(resultados, config)

    result = cachear_resultado(("ml_poisson", lottery), 600, _calc)
    if result is None:
        return jsonify({"erro": "Erro ao processar"}), 500
    return jsonify({"loteria": lottery, "distribuicao_poisson": result})


@app.route("/api/ml/gradient/<lottery>")
def ml_gradient(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404
    resultados, _ = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404
    config = LOTTERIES[lottery]

    def _calc():
        from tecnologias_ml import XGBoostReal
        return XGBoostReal().analisar(resultados, config)

    result = cachear_resultado(("ml_gradient", lottery), 600, _calc)
    if result is None:
        return jsonify({"erro": "Erro ao processar"}), 500
    return jsonify({"loteria": lottery, "gradient_boosting": result})


@app.route("/api/ml/lightgbm/<lottery>")
def ml_lightgbm(lottery):
    if lottery not in LOTTERIES:
        return jsonify({"erro": "Loteria nao encontrada"}), 404
    resultados, _ = obter_dados(lottery, 100)
    if not resultados:
        return jsonify({"erro": "Sem dados disponiveis"}), 404
    config = LOTTERIES[lottery]

    def _calc():
        from tecnologias_ml import LightGBMReal
        return LightGBMReal().analisar(resultados, config)

    result = cachear_resultado(("ml_lightgbm", lottery), 600, _calc)
    if result is None:
        return jsonify({"erro": "Erro ao processar"}), 500
    return jsonify({"loteria": lottery, "lightgbm": result})


if __name__ == "__main__":
    # Verificar predicoes pendentes na inicializacao
    try:
        resultado = verificar_todas_predicoes(api_client)
        if resultado["loterias_verificadas"] > 0:
            print(f"✅ {resultado['loterias_verificadas']} loterias verificadas automaticamente")
    except Exception:
        pass

    print("🚀 Iniciando Loteria Federal API...")
    print(f"📊 Acesse: http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
