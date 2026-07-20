"""
Funcionalidades Avancadas - Inspirado em projetos profissionais
Backtest, Kelly Criterion, Ensemble Scorer, Wheeling, Auto-Tune
"""
import numpy as np
from collections import Counter
from itertools import combinations
import math
import json
from base_analyzer import AnalisadorBase


# Instancia reutilizada para acessar o nucleo estatistico compartilhado
# (elimina a recomputacao inline de frequencia feita antes em duplicata)
_analisador = AnalisadorBase()


class FuncionalidadesAvancadas:
    """
    Funcionalidades avancadas inspiradas em projetos profissionais de loteria
    """
    
    # ==========================================
    # 1. BACKTEST WALK-FORWARD
    # ==========================================
    
    @staticmethod
    def backtest_walk_forward(resultados: list, config: dict, janelas: int = 50, jogos_por_concurso: int = 3) -> dict:
        """
        Backtest walk-forward: treina com dados anteriores e testa no proximo
        Compara IA vs aleatorio
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        
        if len(resultados) < janelas + 10:
            return {"erro": "Dados insuficientes para backtest"}
        
        stats_ia = Counter()
        stats_random = Counter()
        
        start = max(10, len(resultados) - janelas)
        
        for i in range(start, len(resultados)):
            # Treinar com dados anteriores
            dados_treino = resultados[:i]
            target = set(int(d) for d in resultados[i].get("listaDezenas", []))
            
            # Gerar jogos IA
            jogos_ia = []
            for _ in range(jogos_por_concurso):
                jogo = _gerar_jogo_ia(dados_treino, config)
                jogos_ia.append(set(jogo))
            
            # Gerar jogos aleatorios
            jogos_random = []
            for _ in range(jogos_por_concurso):
                jogo = sorted(np.random.choice(range(minimo, maximo + 1), qtd_escolher, replace=False).tolist())
                jogos_random.append(set(jogo))
            
            # Contar acertos
            melhor_ia = max(len(j & target) for j in jogos_ia)
            melhor_random = max(len(j & target) for j in jogos_random)
            
            stats_ia[melhor_ia] += 1
            stats_random[melhor_random] += 1
        
        # Calcular vantagem
        total_ia = sum(k * v for k, v in stats_ia.items())
        total_random = sum(k * v for k, v in stats_random.items())
        
        return {
            "algoritmo": "Backtest Walk-Forward",
            "janelas_testadas": janelas,
            "jogos_por_concurso": jogos_por_concurso,
            "resultados_ia": dict(stats_ia),
            "resultados_random": dict(stats_random),
            "acertos_totais_ia": total_ia,
            "acertos_totais_random": total_random,
            "vantagem_percentual": round((total_ia - total_random) / max(total_random, 1) * 100, 2)
        }
    
    # ==========================================
    # 2. KELLY CRITERION
    # ==========================================
    
    @staticmethod
    def kelly_criterion(custo_aposta: float, premio_possivel: float, probabilidade: float) -> dict:
        """
        Kelly Criterion para gerenciamento de risco
        Calcula fracao otima do bankroll para apostar
        """
        if probabilidade <= 0 or probabilidade >= 1:
            return {"erro": "Probabilidade invalida"}
        
        # Odds fracionais
        odds = premio_possivel / custo_aposta
        
        # Kelly: f* = (bp - q) / b
        # b = odds - 1, p = probabilidade, q = 1 - p
        b = odds - 1
        p = probabilidade
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        
        # Limitar a 25% maximo (conservador)
        kelly_safe = min(0.25, max(0, kelly_fraction))
        
        # Recomendacoes
        if kelly_fraction <= 0:
            recomendacao = "NAO APOSTAR - EV negativo"
            risco = "muito alto"
        elif kelly_fraction < 0.05:
            recomendacao = "Aposta minima - 1-5% do bankroll"
            risco = "medio"
        elif kelly_fraction < 0.15:
            recomendacao = "Aposta moderada - 5-15% do bankroll"
            risco = "moderado"
        else:
            recomendacao = "Aposta agressiva - 15-25% do bankroll"
            risco = "alto"
        
        return {
            "algoritmo": "Kelly Criterion",
            "kelly_fraction": round(kelly_fraction * 100, 4),
            "kelly_safe": round(kelly_safe * 100, 4),
            "recomendacao": recomendacao,
            "risco": risco,
            "ev_por_aposta": round((probabilidade * premio_possivel - custo_aposta), 2),
            "roi_esperado": round((probabilidade * premio_possivel / custo_aposta - 1) * 100, 2)
        }
    
    # ==========================================
    # 3. ENSEMBLE SCORER AVANCADO
    # ==========================================
    
    @staticmethod
    def ensemble_scorer_avancado(numeros: list, resultados: list, config: dict) -> dict:
        """
        Ensemble que combina: Frequencia + Perfil + Entropia + Pares + Fourier
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        # Analise de frequencia (reutiliza o nucleo base)
        stats_freq = _analisador.calcular_frequencia_absoluta(resultados, config)
        freq_abs = stats_freq["frequencia"]
        total = stats_freq["total_numeros_sorteados"]

        # Score de frequencia
        freq_scores = []
        for n in numeros:
            freq = freq_abs.get(n, {}).get("relativa", 0) / 100 if total > 0 else 0
            freq_scores.append(freq)
        freq_score = np.mean(freq_scores) * 100 if freq_scores else 50
        
        # Score de perfil (soma, pares, consecutivos)
        soma = sum(numeros)
        media_soma = (minimo + maximo) / 2 * len(numeros)
        desvio_soma = abs(soma - media_soma) / (maximo - minimo) if (maximo - minimo) > 0 else 0
        profile_score = max(0, 100 - desvio_soma * 50)
        
        # Score de pares
        pares_count = 0
        for i, n1 in enumerate(numeros):
            for n2 in numeros[i+1:]:
                par = tuple(sorted([n1, n2]))
                # Buscar no historico
                for r in resultados:
                    dezenas = sorted([int(d) for d in r.get("listaDezenas", [])])
                    if n1 in dezenas and n2 in dezenas:
                        pares_count += 1
                        break
        pair_score = min(100, pares_count / len(numeros) * 20 + 30)
        
        # Score de entropia
        bins = [0, 0, 0, 0]
        for n in numeros:
            idx = min(3, int((n - minimo) / (maximo - minimo + 1) * 4))
            bins[idx] += 1
        entropia = -sum((b / len(numeros)) * math.log2(b / len(numeros)) if b > 0 else 0 for b in bins)
        entropy_score = entropia / 2 * 100
        
        # Score de diversidade
        unicos = len(set(numeros))
        diversity_score = unicos / len(numeros) * 100
        
        # Penalidade por padroes populares
        penalty = 0
        sorted_nums = sorted(numeros)
        if all(sorted_nums[i] == sorted_nums[i-1] + 1 for i in range(1, len(sorted_nums))):
            penalty += 20  # Todos consecutivos
        if all(n <= 31 for n in numeros) and maximo > 31:
            penalty += 10  # Todos datas
        if all(n % 2 == numeros[0] % 2 for n in numeros):
            penalty += 15  # Todos pares ou todos impares
        
        # Ensemble final
        final_score = (
            freq_score * 0.30 +
            profile_score * 0.20 +
            pair_score * 0.15 +
            entropy_score * 0.15 +
            diversity_score * 0.10 -
            penalty * 0.10
        )
        
        final_score = max(1, min(99, final_score))
        
        return {
            "algoritmo": "Ensemble Scorer Avancado",
            "scores": {
                "frequencia": round(freq_score, 2),
                "perfil": round(profile_score, 2),
                "pares": round(pair_score, 2),
                "entropia": round(entropy_score, 2),
                "diversidade": round(diversity_score, 2),
                "penalidade": round(penalty, 2)
            },
            "score_final": round(final_score, 2),
            "classificacao": "Elite" if final_score >= 80 else "Forte" if final_score >= 65 else "Moderado"
        }
    
    # ==========================================
    # 4. FECHAMENTO/WHEELING OTIMIZADO
    # ==========================================
    
    @staticmethod
    def wheeling_otimizado(base_numeros: list, qtd_jogos: int, config: dict) -> dict:
        """
        Wheeling otimizado com selecao inteligente
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        
        if len(base_numeros) < qtd_escolher:
            return {"erro": "Base de numeros insuficiente"}
        
        # Gerar todas as combinacoes possiveis da base
        todas_combinacoes = list(combinations(sorted(base_numeros), qtd_escolher))
        
        # Se temos menos combinacoes que jogos, usar todas
        if len(todas_combinacoes) <= qtd_jogos:
            jogos = [list(c) for c in todas_combinacoes]
        else:
            # Selecionar jogos mais diversificados
            jogos = []
            vistas = set()
            
            # Estrategia: maximizar diversidade
            for _ in range(qtd_jogos):
                melhor_jogo = None
                melhor_diversidade = -1
                
                # Amostrar candidatos
                for _ in range(min(100, len(todas_combinacoes))):
                    idx = np.random.randint(0, len(todas_combinacoes))
                    candidato = tuple(sorted(todas_combinacoes[idx]))
                    
                    if candidato in vistas:
                        continue
                    
                    # Calcular diversidade
                    diversidade = 0
                    for jogo_anterior in jogos:
                        # Distancia de Hamming
                        diff = len(set(candidato) - set(jogo_anterior))
                        diversidade += diff
                    
                    if diversidade > melhor_diversidade:
                        melhor_diversidade = diversidade
                        melhor_jogo = candidato
                
                if melhor_jogo:
                    jogos.append(list(melhor_jogo))
                    vistas.add(melhor_jogo)
        
        # Calcular cobertura
        todos_numeros_cobertos = set()
        for jogo in jogos:
            todos_numeros_cobertos.update(jogo)
        
        cobertura = len(todos_numeros_cobertos) / len(base_numeros) * 100
        
        return {
            "algoritmo": "Wheeling Otimizado",
            "base_numeros": sorted(base_numeros),
            "qtd_base": len(base_numeros),
            "qtd_jogos": len(jogos),
            "jogos": jogos,
            "cobertura_percentual": round(cobertura, 2),
            "numeros_cobertos": sorted(todos_numeros_cobertos)
        }
    
    # ==========================================
    # 5. AUTO-TUNE DE HIPERPARAMETROS
    # ==========================================
    
    @staticmethod
    def auto_tune(resultados: list, config: dict) -> dict:
        """
        Auto-tune: encontra os melhores parametros para geracao de numeros
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        
        if len(resultados) < 30:
            return {"erro": "Dados insuficientes para auto-tune"}
        
        # Grid de parametros para testar
        configs_teste = [
            {"peso_freq": 0.3, "peso_trend": 0.3, "peso_atrasado": 0.2, "peso_aleatorio": 0.2},
            {"peso_freq": 0.4, "peso_trend": 0.2, "peso_atrasado": 0.3, "peso_aleatorio": 0.1},
            {"peso_freq": 0.2, "peso_trend": 0.4, "peso_atrasado": 0.2, "peso_aleatorio": 0.2},
            {"peso_freq": 0.5, "peso_trend": 0.1, "peso_atrasado": 0.3, "peso_aleatorio": 0.1},
            {"peso_freq": 0.25, "peso_trend": 0.25, "peso_atrasado": 0.25, "peso_aleatorio": 0.25},
        ]
        
        # Treinar com 70% dos dados, testar com 30%
        split = int(len(resultados) * 0.7)
        dados_treino = resultados[:split]
        dados_teste = resultados[split:]
        
        melhor_config = None
        melhor_score = -1
        
        for cfg in configs_teste:
            acertos = 0
            for r in dados_teste:
                # Gerar jogo com esta configuracao
                jogo = _gerar_jogo_com_config(dados_treino, config, cfg)
                target = set(int(d) for d in r.get("listaDezenas", []))
                acertos += len(set(jogo) & target)
            
            score = acertos / len(dados_teste) if dados_teste else 0
            
            if score > melhor_score:
                melhor_score = score
                melhor_config = cfg
        
        return {
            "algoritmo": "Auto-Tune",
            "configs_testadas": len(configs_teste),
            "melhor_config": melhor_config,
            "score_treino": round(melhor_score, 4),
            "recomendacao": "Use esta configuracao para gerar numeros"
        }
    
    # ==========================================
    # 6. IMPORTACAO DE HISTORICO CSV
    # ==========================================
    
    @staticmethod
    def importar_csv(conteudo: str, config: dict) -> dict:
        """
        Importa historico de loteria de CSV
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        
        resultados = []
        erros = 0
        
        linhas = conteudo.strip().split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            
            # Tentar extrair numeros
            import re
            numeros = [int(x) for x in re.findall(r'\d+', linha)]
            
            # Filtrar numeros validos
            numeros_validos = [n for n in numeros if minimo <= n <= maximo]
            
            if len(numeros_validos) >= qtd_escolher:
                # Pegar apenas os primeiros qtd_escolher numeros
                numeros_finais = sorted(list(set(numeros_validos)))[:qtd_escolher]
                if len(numeros_finais) == qtd_escolher:
                    resultados.append({"listaDezenas": [str(n) for n in numeros_finais]})
                else:
                    erros += 1
            else:
                erros += 1
        
        return {
            "total_linhas": len(linhas),
            "resultados_importados": len(resultados),
            "erros": erros,
            "resultados": resultados
        }
    
    # ==========================================
    # 7. TESTES ESTATISTICOS
    # ==========================================
    
    @staticmethod
    def teste_chi_quadrado(observed: dict, expected: dict) -> dict:
        """
        Teste Chi-Quadrado de uniformidade
        """
        chi2 = 0
        gl = 0  # graus de liberdade
        
        for k in set(list(observed.keys()) + list(expected.keys())):
            o = observed.get(k, 0)
            e = expected.get(k, 1)
            if e > 0:
                chi2 += (o - e) ** 2 / e
                gl += 1
        
        # p-valor aproximado
        p_valor = math.exp(-chi2 / 2) if chi2 > 0 else 1
        
        return {
            "chi2": round(chi2, 4),
            "graus_liberdade": gl,
            "p_valor": round(p_valor, 4),
            "significativo": p_valor < 0.05,
            "interpretacao": "Distribuicao NAO e uniforme (p<0.05)" if p_valor < 0.05 else "Distribuicao pode ser uniforme"
        }
    
    @staticmethod
    def teste_ks(dados1: list, dados2: list) -> dict:
        """
        Teste Kolmogorov-Smirnov para comparar distribuicoes
        """
        sorted1 = sorted(dados1)
        sorted2 = sorted(dados2)
        
        all_vals = sorted(set(sorted1 + sorted2))
        
        max_d = 0
        cdf1 = 0
        cdf2 = 0
        
        for v in all_vals:
            cdf1 += sum(1 for x in sorted1 if x <= v) / len(sorted1) if sorted1 else 0
            cdf2 += sum(1 for x in sorted2 if x <= v) / len(sorted2) if sorted2 else 0
            max_d = max(max_d, abs(cdf1 - cdf2))
        
        return {
            "estatistica_D": round(max_d, 4),
            "interpretacao": "Distribuicoes sao diferentes" if max_d > 0.2 else "Distribuicoes sao similares"
        }
    
    # ==========================================
    # 8. GERACAO INTELIGENTE DE JOGOS
    # ==========================================
    
    @staticmethod
    def gerar_jogos_inteligentes(resultados: list, config: dict, quantidade: int = 10) -> list:
        """
        Gera jogos usando todas as tecnicas avancadas
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        
        # Pesos baseados em analise (reutiliza o nucleo base)
        stats_freq = _analisador.calcular_frequencia_absoluta(resultados, config)
        freq_abs = stats_freq["frequencia"]
        total = stats_freq["total_numeros_sorteados"]

        pesos = {}
        for num in range(minimo, maximo + 1):
            freq = freq_abs.get(num, {}).get("relativa", 0) / 100 if total > 0 else 0
            pesos[num] = freq + 0.1  # Suavizacao
        
        # Normalizar pesos
        soma_pesos = sum(pesos.values())
        pesos = {k: v / soma_pesos for k, v in pesos.items()}
        
        jogos = []
        
        for i in range(quantidade):
            # Estrategia ciclica
            estrategia = i % 5
            
            numeros = []
            
            if estrategia == 0:  # Frequencia pura
                nums_sorted = sorted(pesos.items(), key=lambda x: x[1], reverse=True)
                numeros = [n for n, _ in nums_sorted[:qtd_escolher]]
            
            elif estrategia == 1:  # Balanceado
                numeros = list(np.random.choice(
                    list(pesos.keys()), 
                    qtd_escolher, 
                    replace=False, 
                    p=list(pesos.values())
                ))
            
            elif estrategia == 2:  # Diversificado
                # Dividir em faixas
                faixa = (maximo - minimo) // 3
                numeros = []
                for f in range(3):
                    inicio = minimo + f * faixa
                    fim = minimo + (f + 1) * faixa
                    candidatos = [n for n in range(inicio, fim + 1) if n in pesos]
                    if candidatos:
                        numeros.extend(list(np.random.choice(
                            candidatos, 
                            min(qtd_escolher // 3 + 1, len(candidatos)), 
                            replace=False
                        )))
                numeros = sorted(numeros[:qtd_escolher])
            
            elif estrategia == 3:  # Par/Impar balanceado
                pares = [n for n in range(minimo, maximo + 1) if n % 2 == 0]
                impares = [n for n in range(minimo, maximo + 1) if n % 2 != 0]
                n_pares = qtd_escolher // 2
                n_impares = qtd_escolher - n_pares
                numeros = list(np.random.choice(pares, min(n_pares, len(pares)), replace=False))
                numeros.extend(list(np.random.choice(impares, min(n_impares, len(impares)), replace=False)))
                numeros = sorted(numeros[:qtd_escolher])
            
            else:  # Aleatorio com pesos
                numeros = list(np.random.choice(
                    list(pesos.keys()), 
                    qtd_escolher, 
                    replace=False, 
                    p=list(pesos.values())
                ))
            
            # Preencher se necessario
            while len(numeros) < qtd_escolher:
                num = np.random.randint(minimo, maximo + 1)
                if num not in numeros:
                    numeros.append(num)
            
            numeros = sorted(numeros[:qtd_escolher])
            
            # Calcular score
            score_info = FuncionalidadesAvancadas.ensemble_scorer_avancado(
                numeros, resultados, config
            )
            
            jogos.append({
                "numeros": numeros,
                "estrategia": ["frequencia", "balanceado", "diversificado", "par_impar", "ponderado"][estrategia],
                "score": score_info["score_final"],
                "classificacao": score_info["classificacao"]
            })
        
        # Ordenar por score
        jogos.sort(key=lambda x: x["score"], reverse=True)
        
        return jogos


# Funcoes auxiliares
def _gerar_jogo_ia(resultados: list, config: dict) -> list:
    """Gera um jogo usando IA"""
    minimo = config["min_num"]
    maximo = config["max_num"]
    qtd_escolher = config["pick_count"]
    
    stats_freq = _analisador.calcular_frequencia_absoluta(resultados, config)
    freq_abs = stats_freq["frequencia"]
    total = stats_freq["total_numeros_sorteados"]
    faixa = (maximo - minimo + 1)

    # Pesos baseados em frequencia (reutiliza o nucleo base)
    pesos = []
    nums = []
    for num in range(minimo, maximo + 1):
        freq = freq_abs.get(num, {}).get("relativa", 0) / 100 if total > 0 else 1 / faixa
        pesos.append(freq + 0.01)
        nums.append(num)
    
    soma = sum(pesos)
    pesos = [p / soma for p in pesos]
    
    return sorted(np.random.choice(nums, qtd_escolher, replace=False, p=pesos).tolist())


def _gerar_jogo_com_config(resultados: list, config: dict, cfg: dict) -> list:
    """Gera jogo com configuracao especifica"""
    minimo = config["min_num"]
    maximo = config["max_num"]
    qtd_escolher = config["pick_count"]
    
    stats_freq = _analisador.calcular_frequencia_absoluta(resultados, config)
    atrasados = Counter()
    
    # Numeros quentes (top 10 por frequencia absoluta)
    quentes = [n for n, _ in stats_freq["mais_frequentes"][:10]]
    
    # Numeros frios (nao aparecem ha tempo)
    for num in range(minimo, maximo + 1):
        for i, r in enumerate(resultados):
            if num in [int(d) for d in r.get("listaDezenas", [])]:
                atrasados[num] = i
                break
    
    frios = sorted(atrasados.items(), key=lambda x: x[1])[:10]
    frios = [n for n, _ in frios]
    
    # Gerar com pesos
    numeros = []
    
    # Quentes
    n_quentes = int(qtd_escolher * cfg["peso_freq"])
    if quentes and n_quentes > 0:
        numeros.extend(list(np.random.choice(quentes, min(n_quentes, len(quentes)), replace=False)))
    
    # Frios
    n_frios = int(qtd_escolher * cfg["peso_atrasado"])
    if frios and n_frios > 0:
        candidatos_frios = [n for n in frios if n not in numeros]
        if candidatos_frios:
            numeros.extend(list(np.random.choice(candidatos_frios, min(n_frios, len(candidatos_frios)), replace=False)))
    
    # Aleatorios
    n_aleatorios = qtd_escolher - len(numeros)
    if n_aleatorios > 0:
        todos = list(range(minimo, maximo + 1))
        candidatos = [n for n in todos if n not in numeros]
        if candidatos:
            numeros.extend(list(np.random.choice(candidatos, min(n_aleatorios, len(candidatos)), replace=False)))
    
    return sorted(numeros[:qtd_escolher])


# Instancia global
funcionalidades = FuncionalidadesAvancadas()
