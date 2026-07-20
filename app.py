"""
Servidor Flask - API Backend Atualizado
"""
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import json
import threading
import numpy as np
from datetime import datetime
from api_client import api_client
from analyzer import AnalisadorLoteriasAvancado as AnalisadorLoterias
from analyzer_ultra import AnalisadorUltraAvancado
from analyzer_global import AnalisadorGlobal
from config import LOTTERIES, BASE_DIR, RESULTS_DIR, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from flask.json.provider import DefaultJSONProvider

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
CORS(app)


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


def obter_dados(lottery: str, count: int = 100):
    """Busca resultados + estatisticas com cache em memoria (TTL 10 min)"""
    key = (lottery, count)
    with cache_lock:
        if key in _dados_cache:
            cached = _dados_cache[key]
            if (datetime.now() - cached["time"]).seconds < 600:
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
            if (datetime.now() - cached["time"]).seconds < ttl:
                return cached["data"]

    data = fn()

    with cache_lock:
        _result_cache[chave] = {"data": data, "time": datetime.now()}
    return data


def obter_ou_buscar(lottery: str):
    with cache_lock:
        if lottery in cache_memoria:
            cached = cache_memoria[lottery]
            if (datetime.now() - cached["time"]).seconds < 300:
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
    
    return jsonify({
        "total_geradas": len(combinacoes),
        "configuracao": config,
        "combinacoes": combinacoes[:maximo]
    })


@app.route("/api/estatisticas/<lottery>")
def obter_estatisticas(lottery):
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

    return jsonify({
        "loteria": lottery,
        "configuracao": config,
        "resultado_ultra": resultado,
        "concursos_analisados": len(resultado.get("combinacoes", [])) if isinstance(resultado, dict) else 0
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

    return jsonify({
        "loteria": lottery,
        "configuracao": config,
        "resultado_global": resultado,
        "concursos_analisados": len(resultado.get("combinacoes", [])) if isinstance(resultado, dict) else 0
    })


@app.route("/api/loterias_mundiais")
def obter_loterias_mundiais():
    """Retorna todas as loterias mundiais"""
    from loterias_mundiais import LOTERIAS_MUNDIAIS, TECNICAS_ANALISE_MUNDIAL, ESTRATEGIAS_GLOBAIS
    
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
            "odds": f"1 em {round(1/prob_acerto) if prob_acerto > 0 else 'infinito':,}"
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
    custo = float(request.args.get('custo', 5))
    premio = float(request.args.get('premio', 5000000))
    probabilidade = float(request.args.get('probabilidade', 0.0000001))
    
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
        from tecnologias_adicionais import TecnologiasAdicionais
        from analyzer_ultra import AnalisadorUltraAvancado
        from analyzer_global import AnalisadorGlobal
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


if __name__ == "__main__":
    print("🚀 Iniciando Loteria Federal API...")
    print(f"📊 Acesse: http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
