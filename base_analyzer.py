"""
Motor de Analise e IA Avancada para Loterias
Calculos matematicos e probabilisticos baseados no historico completo.

Este modulo define a classe base ``AnalisadorBase`` com todo o nucleo
estatistico compartilhado (frequencia, probabilidades, intervalos,
tendencias, sequencias, distribuicao, paridade, scoring e sugestoes).

Os analyzers especializados (``AnalisadorLoteriasAvancado``,
``AnalisadorUltraAvancado``, ``AnalisadorGlobal``) herdam desta base para
evitar duplicacao de logica e manter uma unica fonte de verdade.
"""
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime, timedelta
import json
import os
import math
from config import AI_CONFIG, RESULTS_DIR, LOTTERIES


class AnalisadorBase:
    def __init__(self):
        self.cache_frequencia = {}
        self.cache_padroes = {}

    # ========================================
    # ANALISES MATEMATICAS BASICAS
    # ========================================

    def calcular_frequencia_absoluta(self, resultados: list, config: dict) -> dict:
        """Calcula frequencia absoluta e relativa de cada numero"""
        todos_numeros = []
        for resultado in resultados:
            dezenas = resultado.get("listaDezenas", [])
            todos_numeros.extend([int(d) for d in dezenas])

        contador = Counter(todos_numeros)
        total_sorteios = len(resultados)
        total_numeros_sorteados = len(todos_numeros)

        minimo = config["min_num"]
        maximo = config["max_num"]
        faixa = maximo - minimo + 1

        frequencia = {}
        for num in range(minimo, maximo + 1):
            vezes = contador.get(num, 0)
            frequencia[num] = {
                "absoluta": vezes,
                "relativa": round((vezes / total_numeros_sorteados) * 100, 4) if total_numeros_sorteados > 0 else 0,
                "esperada": round(total_numeros_sorteados / faixa, 4),
                "desvio": round(vezes - (total_numeros_sorteados / faixa), 4),
                "desvio_relativo": round(((vezes - (total_numeros_sorteados / faixa)) / (total_numeros_sorteados / faixa)) * 100, 2) if total_numeros_sorteados > 0 else 0
            }

        return {
            "frequencia": frequencia,
            "total_sorteios": total_sorteios,
            "total_numeros_sorteados": total_numeros_sorteados,
            "mais_frequentes": sorted(frequencia.items(), key=lambda x: x[1]["absoluta"], reverse=True)[:15],
            "menos_frequentes": sorted(frequencia.items(), key=lambda x: x[1]["absoluta"])[:15],
            "acima_esperado": [(n, info) for n, info in frequencia.items() if info["absoluta"] > info["esperada"]],
            "abaixo_esperado": [(n, info) for n, info in frequencia.items() if info["absoluta"] < info["esperada"]]
        }

    def calcular_estatisticas_descritivas(self, resultados: list, config: dict) -> dict:
        """Calcula media, mediana, moda, variancia, desvio padrao"""
        somas = []
        medias_por_sorteio = []

        for resultado in resultados:
            dezenas = [int(d) for d in resultado.get("listaDezenas", [])]
            somas.append(sum(dezenas))
            medias_por_sorteio.append(np.mean(dezenas))

        somas_array = np.array(somas)
        medias_array = np.array(medias_por_sorteio)

        return {
            "soma": {
                "media": round(float(np.mean(somas_array)), 4),
                "mediana": round(float(np.median(somas_array)), 4),
                "moda": int(Counter(somas).most_common(1)[0][0]) if somas else 0,
                "variancia": round(float(np.var(somas_array, ddof=1)), 4),
                "desvio_padrao": round(float(np.std(somas_array, ddof=1)), 4),
                "coeficiente_variacao": round(float((np.std(somas_array, ddof=1) / np.mean(somas_array)) * 100), 2) if np.mean(somas_array) > 0 else 0,
                "minimo": int(np.min(somas_array)),
                "maximo": int(np.max(somas_array)),
                "amplitude": int(np.max(somas_array) - np.min(somas_array)),
                "assimetria": round(float(self._calcular_assimetria(somas_array)), 4),
                "curtose": round(float(self._calcular_curtose(somas_array)), 4)
            },
            "media_por_numero": {
                "media": round(float(np.mean(medias_array)), 4),
                "desvio_padrao": round(float(np.std(medias_array, ddof=1)), 4)
            }
        }

    def _calcular_assimetria(self, dados: np.ndarray) -> float:
        """Calcula assimetria (skewness) de Fisher"""
        n = len(dados)
        if n < 3:
            return 0
        media = np.mean(dados)
        dp = np.std(dados, ddof=1)
        if dp == 0:
            return 0
        return float((n / ((n-1) * (n-2))) * np.sum(((dados - media) / dp) ** 3))

    def _calcular_curtose(self, dados: np.ndarray) -> float:
        """Calcula curtose excessiva"""
        n = len(dados)
        if n < 4:
            return 0
        media = np.mean(dados)
        dp = np.std(dados, ddof=1)
        if dp == 0:
            return 0
        return float(((n * (n+1)) / ((n-1) * (n-2) * (n-3))) * np.sum(((dados - media) / dp) ** 4) - (3 * (n-1)**2) / ((n-2) * (n-3)))

    # ========================================
    # ANALISES PROBABILISTICAS
    # ========================================

    def calcular_probabilidades(self, resultados: list, config: dict) -> dict:
        """Calcula probabilidades empiricas de cada numero"""
        todos_numeros = []
        for resultado in resultados:
            dezenas = [int(d) for d in resultado.get("listaDezenas", [])]
            todos_numeros.extend(dezenas)

        contador = Counter(todos_numeros)
        total = len(todos_numeros)

        minimo = config["min_num"]
        maximo = config["max_num"]
        faixa = maximo - minimo + 1
        qtd_escolher = config["pick_count"]

        # Probabilidade teorica uniforme
        prob_teorica = 1 / faixa

        probabilidades = {}
        for num in range(minimo, maximo + 1):
            vezes = contador.get(num, 0)
            prob_empirica = vezes / total if total > 0 else 0

            # Probabilidade de NAO ser sorteado em K jogos
            prob_nao_sorteado_1 = (1 - prob_empirica)
            prob_nao_sorteado_5 = prob_nao_sorteado_1 ** 5
            prob_nao_sorteado_10 = prob_nao_sorteado_1 ** 10

            # Chi-quadrado para teste de uniformidade
            chi2 = ((vezes - (total * prob_teorica)) ** 2) / (total * prob_teorica)

            probabilidades[num] = {
                "empirica": round(prob_empirica * 100, 4),
                "teorica": round(prob_teorica * 100, 4),
                "odds": round(1 / prob_empirica, 2) if prob_empirica > 0 else float('inf'),
                "prob_nao_sorteado_5jogos": round(prob_nao_sorteado_5 * 100, 2),
                "prob_nao_sorteado_10jogos": round(prob_nao_sorteado_10 * 100, 2),
                "chi2": round(chi2, 4),
                "desvio_padrao_teorica": round(math.sqrt(total * prob_teorica * (1 - prob_teorica)), 4)
            }

        return probabilidades

    def calcular_probabilidade_conjunta(self, resultados: list, config: dict) -> dict:
        """Calcula probabilidades de combinacoes de numeros"""
        contador_pares = Counter()
        contador_trios = Counter()

        for resultado in resultados:
            dezenas = sorted([int(d) for d in resultado.get("listaDezenas", [])])
            for par in combinations(dezenas, 2):
                contador_pares[par] += 1
            if len(dezenas) >= 3:
                for trio in combinations(dezenas[:10], 3):  # Top 10 para limitar
                    contador_trios[trio] += 1

        total_sorteios = len(resultados)

        return {
            "pares": {
                "top_20": [(list(p), c, round(c/total_sorteios*100, 2)) for p, c in contador_pares.most_common(20)],
                "total_pares_unicos": len(contador_pares)
            },
            "trios": {
                "top_10": [(list(t), c, round(c/total_sorteios*100, 2)) for t, c in contador_trios.most_common(10)],
                "total_trios_unicos": len(contador_trios)
            }
        }

    # ========================================
    # ANALISES TEMPORAIS
    # ========================================

    def analisar_intervalos(self, resultados: list, config: dict) -> dict:
        """Analisa intervalos entre aparicoes com estatisticas completas"""
        ultimo_visto = {}
        intervalos = defaultdict(list)

        for i, resultado in enumerate(resultados):
            dezenas = [int(d) for d in resultado.get("listaDezenas", [])]
            for num in dezenas:
                if num in ultimo_visto:
                    gap = i - ultimo_visto[num]
                    intervalos[num].append(gap)
                ultimo_visto[num] = i

        ultimo_indice = len(resultados) - 1

        info_intervalos = {}
        for num, lista_gaps in intervalos.items():
            gaps_array = np.array(lista_gaps) if lista_gaps else np.array([0])

            info_intervalos[num] = {
                "media": round(float(np.mean(gaps_array)), 2),
                "mediana": round(float(np.median(gaps_array)), 2),
                "desvio_padrao": round(float(np.std(gaps_array, ddof=1)), 2) if len(gaps_array) > 1 else 0,
                "minimo": int(np.min(gaps_array)),
                "maximo": int(np.max(gaps_array)),
                "atual": ultimo_indice - ultimo_visto.get(num, ultimo_indice),
                "vezes_apareceu": len(lista_gaps) + 1,
                "probabilidade_proximo": round(1 - (1 - 1/(config["max_num"] - config["min_num"] + 1)) ** (config["pick_count"]), 4)
            }

            # Calcular se esta "atrasado"
            media = info_intervalos[num]["media"]
            atual = info_intervalos[num]["atual"]
            if media > 0:
                info_intervalos[num]["atrasado"] = atual > media * 1.3
                info_intervalos[num]["nivel_atraso"] = round(atual / media, 2) if media > 0 else 0
            else:
                info_intervalos[num]["atrasado"] = False
                info_intervalos[num]["nivel_atraso"] = 0

        return info_intervalos

    def analisar_tendencias(self, resultados: list, config: dict, janelas: list = [5, 10, 20, 50]) -> dict:
        """Analisa tendencias em multiplas janelas temporais"""
        todas_tendencias = {}

        for janela in janelas:
            if len(resultados) < janela * 2:
                continue

            recentes = resultados[:janela]
            anteriores = resultados[janela:janela*2]

            freq_recente = Counter()
            freq_antiga = Counter()

            for r in recentes:
                for d in r.get("listaDezenas", []):
                    freq_recente[int(d)] += 1

            for r in anteriores:
                for d in r.get("listaDezenas", []):
                    freq_antiga[int(d)] += 1

            em_alta = []
            em_baixa = []
            estaveis = []

            todos = set(list(freq_recente.keys()) + list(freq_antiga.keys()))
            for num in todos:
                r = freq_recente.get(num, 0) / janela
                o = freq_antiga.get(num, 0) / janela

                if o > 0:
                    variacao = ((r - o) / o) * 100
                else:
                    variacao = 100 if r > 0 else 0

                if variacao > 20:
                    em_alta.append({"numero": num, "variacao": round(variacao, 2)})
                elif variacao < -20:
                    em_baixa.append({"numero": num, "variacao": round(variacao, 2)})
                else:
                    estaveis.append(num)

            todas_tendencias[f"janela_{janela}"] = {
                "em_alta": sorted(em_alta, key=lambda x: x["variacao"], reverse=True)[:10],
                "em_baixa": sorted(em_baixa, key=lambda x: x["variacao"])[:10],
                "estaveis": estaveis[:10]
            }

        return todas_tendencias

    def analisar_sequencias(self, resultados: list, config: dict) -> dict:
        """Analisa padroes de sequencia e consecutivos"""
        consecutivos = Counter()
        pares_consecutivos = Counter()
        saltos = []

        for resultado in resultados:
            dezenas = sorted([int(d) for d in resultado.get("listaDezenas", [])])

            # Contar consecutivos
            consec = 0
            for i in range(1, len(dezenas)):
                if dezenas[i] == dezenas[i-1] + 1:
                    consec += 1
                else:
                    if consec > 0:
                        consecutivos[consec] += 1
                    consec = 0
            if consec > 0:
                consecutivos[consec] += 1

            # Analisar saltos entre numeros
            for i in range(1, len(dezenas)):
                salto = dezenas[i] - dezenas[i-1]
                saltos.append(salto)

        saltos_array = np.array(saltos) if saltos else np.array([0])

        return {
            "consecutivos": dict(consecutivos),
            "probabilidade_consecutivo": round(sum(consecutivos.values()) / len(resultados) * 100, 2) if resultados else 0,
            "saltos": {
                "media": round(float(np.mean(saltos_array)), 2),
                "mediana": round(float(np.median(saltos_array)), 2),
                "desvio_padrao": round(float(np.std(saltos_array, ddof=1)), 2) if len(saltos_array) > 1 else 0,
                "minimo": int(np.min(saltos_array)),
                "maximo": int(np.max(saltos_array)),
                "distribuicao": dict(Counter(saltos).most_common(10))
            }
        }

    def analisar_distribuicao(self, resultados: list, config: dict) -> dict:
        """Analisa distribuicao dos numeros por faixas"""
        minimo = config["min_num"]
        maximo = config["max_num"]
        faixa_total = maximo - minimo + 1

        # Dividir em 4 quartis
        tamanho_quartil = faixa_total // 4
        quartis = {
            "Q1": (minimo, minimo + tamanho_quartil - 1),
            "Q2": (minimo + tamanho_quartil, minimo + 2 * tamanho_quartil - 1),
            "Q3": (minimo + 2 * tamanho_quartil, minimo + 3 * tamanho_quartil - 1),
            "Q4": (minimo + 3 * tamanho_quartil, maximo)
        }

        contagem_quartis = defaultdict(int)
        distribuicoes_completas = []

        for resultado in resultados:
            dezenas = [int(d) for d in resultado.get("listaDezenas", [])]
            dist_sorteio = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}

            for num in dezenas:
                for q, (inf, sup) in quartis.items():
                    if inf <= num <= sup:
                        contagem_quartis[q] += 1
                        dist_sorteio[q] += 1

            distribuicoes_completas.append(dist_sorteio)

        # Frequencia de cada distribuicao
        freq_distribuicoes = Counter(json.dumps(d, sort_keys=True) for d in distribuicoes_completas)

        total_numeros = sum(contagem_quartis.values())

        return {
            "quartis": {q: {"inicio": inf, "fim": sup} for q, (inf, sup) in quartis.items()},
            "contagem_absoluta": dict(contagem_quartis),
            "contagem_relativa": {q: round(c/total_numeros*100, 2) for q, c in contagem_quartis.items()} if total_numeros > 0 else {},
            "distribuicoes_mais_comuns": [(json.loads(d), f, round(f/len(resultados)*100, 2)) for d, f in freq_distribuicoes.most_common(5)]
        }

    def analisar_paridade(self, resultados: list, config: dict) -> dict:
        """Analisa distribuicao de numeros pares e impares"""
        padroes_paridade = []

        for resultado in resultados:
            dezenas = [int(d) for d in resultado.get("listaDezenas", [])]
            pares = sum(1 for d in dezenas if d % 2 == 0)
            impares = len(dezenas) - pares
            padroes_paridade.append({"pares": pares, "impares": impares})

        contagem_padroes = Counter(json.dumps(p, sort_keys=True) for p in padroes_paridade)

        return {
            "padroes_mais_comuns": [(json.loads(p), f, round(f/len(resultados)*100, 2)) for p, f in contagem_padroes.most_common(5)],
            "media_pares": round(np.mean([p["pares"] for p in padroes_paridade]), 2),
            "media_impares": round(np.mean([p["impares"] for p in padroes_paridade]), 2)
        }

    # ========================================
    # ALGORITMOS DE SELECAO AVANCADOS
    # ========================================

    def calcular_pontuacao_numero(self, num: int, stats: dict, config: dict) -> dict:
        """Calcula pontuacao composta para um numero baseado em multiplas metricas"""
        pontuacao = 0
        fatores = []

        freq = stats["frequencia"]["frequencia"].get(num, {})
        intervalos = stats.get("intervalos", {}).get(num, {})
        tendencias = stats.get("tendencias", {})

        # Fator 1: Frequencia (0-25 pontos)
        if freq:
            media_geral = stats["frequencia"]["total_numeros_sorteados"] / (config["max_num"] - config["min_num"] + 1)
            if freq["absoluta"] > media_geral:
                pontos = min(25, (freq["absoluta"] / media_geral) * 15)
                pontuacao += pontos
                fatores.append(f"Acima da media (+{pontos:.1f})")

        # Fator 2: Atraso (0-25 pontos)
        if intervalos and intervalos.get("atrasado"):
            nivel = intervalos.get("nivel_atraso", 0)
            pontos = min(25, nivel * 10)
            pontuacao += pontos
            fatores.append(f"Atrasado nivel {nivel} (+{pontos:.1f})")

        # Fator 3: Tendencia (0-25 pontos)
        for janela, dados in tendencias.items():
            em_alta = [item["numero"] for item in dados.get("em_alta", [])]
            if num in em_alta:
                pontos = 25 / len(tendencias)
                pontuacao += pontos
                fatores.append(f"Em alta {janela} (+{pontos:.1f})")
                break

        # Fator 4: Probabilidade (0-25 pontos)
        prob = stats.get("probabilidades", {}).get(num, {})
        if prob:
            odds = prob.get("odds", 0)
            if odds > 0 and odds < 100:
                pontos = min(25, (1/odds) * 500)
                pontuacao += pontos
                fatores.append(f"Odds {odds}:1 (+{pontos:.1f})")

        return {
            "pontuacao_total": round(pontuacao, 2),
            "fatores": fatores,
            "classificacao": "alta" if pontuacao >= 60 else "media" if pontuacao >= 40 else "baixa"
        }

    def gerar_sugestoes_avancadas(self, resultados: list, config: dict, quantidade: int = 1) -> list:
        """Gera sugestoes com analise avancada multi-criterio"""
        stats_completas = self._calcular_estatisticas_completas(resultados, config)

        # Calcular pontuacao para todos os numeros
        pontuacoes = {}
        minimo = config["min_num"]
        maximo = config["max_num"]

        for num in range(minimo, maximo + 1):
            pontuacoes[num] = self.calcular_pontuacao_numero(num, stats_completas, config)

        # Ordenar por pontuacao
        numeros_ordenados = sorted(pontuacoes.items(), key=lambda x: x[1]["pontuacao_total"], reverse=True)

        # Separar por tiers
        tier_s = [n for n, p in numeros_ordenados if p["classificacao"] == "alta"][:15]
        tier_a = [n for n, p in numeros_ordenados if p["classificacao"] == "media"][:15]
        tier_b = [n for n, p in numeros_ordenados if p["classificacao"] == "baixa"][:10]

        sugestoes = []

        for i in range(quantidade):
            # Estrategias variadas
            estrategia = np.random.choice(["elite", "balanceada", "diversificada", "conservadora", "ousada"])

            numeros = []

            if estrategia == "elite":
                # 70% tier S, 30% tier A
                qtd_s = int(config["pick_count"] * 0.7)
                qtd_a = config["pick_count"] - qtd_s
                numeros = list(np.random.choice(tier_s[:15], min(qtd_s, len(tier_s)), replace=False))
                numeros.extend(list(np.random.choice(tier_a[:15], min(qtd_a, len(tier_a)), replace=False)))

            elif estrategia == "balanceada":
                # 40% S, 40% A, 20% B
                qtd_s = int(config["pick_count"] * 0.4)
                qtd_a = int(config["pick_count"] * 0.4)
                qtd_b = config["pick_count"] - qtd_s - qtd_a
                numeros = list(np.random.choice(tier_s[:15], min(qtd_s, len(tier_s)), replace=False))
                numeros.extend(list(np.random.choice(tier_a[:15], min(qtd_a, len(tier_a)), replace=False)))
                if qtd_b > 0 and tier_b:
                    numeros.extend(list(np.random.choice(tier_b, min(qtd_b, len(tier_b)), replace=False)))

            elif estrategia == "diversificada":
                # Mix completo
                numeros = list(np.random.choice(tier_s[:10], min(3, len(tier_s)), replace=False))
                numeros.extend(list(np.random.choice(tier_a[:10], min(3, len(tier_a)), replace=False)))
                if tier_b:
                    numeros.extend(list(np.random.choice(tier_b, min(2, len(tier_b)), replace=False)))

            elif estrategia == "conservadora":
                # Focada em numeros quentes historicamente
                quentes = [n for n, _ in stats_completas["frequencia"]["mais_frequentes"][:15]]
                numeros = list(np.random.choice(quentes, min(config["pick_count"], len(quentes)), replace=False))

            elif estrategia == "ousada":
                # Focada em numeros atrasados e em alta
                candidatos = list(set(tier_s[:10] + [n for n, p in numeros_ordenados if pontuacoes[n]["pontuacao_total"] > 40]))
                numeros = list(np.random.choice(candidatos[:20], min(config["pick_count"], min(20, len(candidatos))), replace=False))

            # Preencher se necessario
            while len(numeros) < config["pick_count"]:
                num = np.random.randint(minimo, maximo + 1)
                if num not in numeros:
                    numeros.append(num)

            numeros = sorted([int(x) for x in numeros[:config["pick_count"]]])

            # Calcular metricas da combinacao
            metricas = self._calcular_metricas_combinacao(numeros, stats_completas, config)

            sugestoes.append({
                "numeros": numeros,
                "pontuacao_geral": metricas["pontuacao"],
                "estrategia": estrategia.strip(),
                "confianca": metricas["confianca"],
                "metricas": metricas,
                "motivos": metricas["motivos"]
            })

        # Ordenar por pontuacao
        sugestoes.sort(key=lambda x: x["pontuacao_geral"], reverse=True)

        return sugestoes

    def _calcular_estatisticas_completas(self, resultados: list, config: dict) -> dict:
        """Calcula todas as estatisticas de uma vez"""
        return {
            "frequencia": self.calcular_frequencia_absoluta(resultados, config),
            "probabilidades": self.calcular_probabilidades(resultados, config),
            "intervalos": self.analisar_intervalos(resultados, config),
            "tendencias": self.analisar_tendencias(resultados, config),
            "sequencias": self.analisar_sequencias(resultados, config),
            "distribuicao": self.analisar_distribuicao(resultados, config),
            "paridade": self.analisar_paridade(resultados, config),
            "descritivas": self.calcular_estatisticas_descritivas(resultados, config),
            "conjunta": self.calcular_probabilidade_conjunta(resultados, config)
        }

    def _calcular_metricas_combinacao(self, numeros: list, stats: dict, config: dict) -> dict:
        """Calcula metricas detalhadas para uma combinacao"""
        pontuacao = 0
        motivos = []

        # 1. Analise de frequencia (0-20 pontos)
        nums_quentes = [n for n, _ in stats["frequencia"]["mais_frequentes"][:10]]
        qtd_quentes = sum(1 for n in numeros if n in nums_quentes)
        pontos_freq = min(20, qtd_quentes * 4)
        pontuacao += pontos_freq
        if qtd_quentes >= 3:
            motivos.append(f"{qtd_quentes} numeros entre os mais frequentes")

        # 2. Analise de tendencia (0-20 pontos)
        em_alta_total = []
        for janela, dados in stats.get("tendencias", {}).items():
            em_alta_total.extend([item["numero"] for item in dados.get("em_alta", [])])
        qtd_tendencia = sum(1 for n in numeros if n in em_alta_total)
        pontos_tend = min(20, qtd_tendencia * 5)
        pontuacao += pontos_tend
        if qtd_tendencia >= 2:
            motivos.append(f"{qtd_tendencia} numeros em tendencia de alta")

        # 3. Analise de atraso (0-20 pontos)
        atrasados = [n for n, info in stats.get("intervalos", {}).items() if info.get("atrasado")]
        qtd_atrasados = sum(1 for n in numeros if n in atrasados)
        pontos_atraso = min(20, qtd_atrasados * 5)
        pontuacao += pontos_atraso
        if qtd_atrasados >= 2:
            motivos.append(f"{qtd_atrasados} numeros atrasados acima da media")

        # 4. Analise de pares (0-15 pontos)
        pares_top = stats.get("conjunta", {}).get("pares", {}).get("top_20", [])
        pares_encontrados = 0
        for i, n1 in enumerate(numeros):
            for n2 in numeros[i+1:]:
                for p, _, _ in pares_top:
                    if sorted([n1, n2]) == sorted(p):
                        pares_encontrados += 1
        pontos_pares = min(15, pares_encontrados * 3)
        pontuacao += pontos_pares
        if pares_encontrados >= 2:
            motivos.append(f"{pares_encontrados} pares frequentes encontrados")

        # 5. Analise de distribuicao (0-15 pontos)
        dist = self._calcular_distribuicao_numeros(numeros, config)
        pontos_dist = 0
        if 30 <= dist["percentual_primeiro_terco"] <= 40:
            pontos_dist += 5
        if 30 <= dist["percentual_segundo_terco"] <= 40:
            pontos_dist += 5
        if 20 <= dist["percentual_terceiro_terco"] <= 40:
            pontos_dist += 5
        pontuacao += pontos_dist

        if pontos_dist >= 10:
            motivos.append("Distribuicao equilibrada nas faixas")

        # 6. Analise de paridade (0-10 pontos)
        pares = sum(1 for n in numeros if n % 2 == 0)
        impares = len(numeros) - pares
        if abs(pares - impares) <= 2:
            pontuacao += 10
            motivos.append(f"Balanceamento par/impar ({pares}P/{impares}I)")

        # 7. Analise de soma (0-10 pontos)
        soma = sum(numeros)
        media_soma = stats["descritivas"]["soma"]["media"]
        dp_soma = stats["descritivas"]["soma"]["desvio_padrao"]
        if dp_soma > 0:
            z_score = abs(soma - media_soma) / dp_soma
            if z_score < 1:
                pontuacao += 10
                motivos.append("Soma dentro do desvio padrao esperado")
            elif z_score < 1.5:
                pontuacao += 5

        # 8. Analise de probabilidade (0-10 pontos)
        prob_numeros = [stats["probabilidades"].get(n, {}).get("empirica", 0) for n in numeros]
        prob_media = np.mean(prob_numeros) if prob_numeros else 0
        if prob_media > 3:
            pontuacao += 10
            motivos.append("Probabilidade empirica acima da media")

        # Calcular confianca
        confianca = min(95, max(10, pontuacao))

        if not motivos:
            motivos.append("Combinacao gerada por analise estatistica")

        return {
            "pontuacao": round(pontuacao, 2),
            "confianca": round(confianca, 1),
            "motivos": motivos[:5],
            "distribuicao": dist
        }

    def _calcular_confianca(self, numeros: list, freq_stats: dict, pares_stats: dict, intervalos: dict) -> float:
        """Calcula pontuacao de confianca para uma combinacao (usado por /api/combinacoes)"""
        pontuacao = 0

        nums_quentes = [n for n, _ in freq_stats.get("mais_frequentes", [])[:10]]
        qtd_quentes = sum(1 for n in numeros if n in nums_quentes)
        pontuacao += min(20, qtd_quentes * 4)

        pares_top = (pares_stats or {}).get("top_20", [])
        pares_encontrados = 0
        for i, n1 in enumerate(numeros):
            for n2 in numeros[i + 1:]:
                for p, _, _ in pares_top:
                    if sorted([n1, n2]) == sorted(p):
                        pares_encontrados += 1
        pontuacao += min(15, pares_encontrados * 3)

        atrasados = [n for n, info in (intervalos or {}).items() if info.get("atrasado")]
        qtd_atrasados = sum(1 for n in numeros if n in atrasados)
        pontuacao += min(20, qtd_atrasados * 5)

        return round(min(95, max(10, pontuacao)), 1)

    def _gerar_motivos(self, numeros: list, freq_stats: dict, tendencias: dict, intervalos: dict) -> list:
        """Gera lista de motivos para uma combinacao (usado por /api/combinacoes)"""
        motivos = []

        nums_quentes = [n for n, _ in freq_stats.get("mais_frequentes", [])[:10]]
        qtd_quentes = sum(1 for n in numeros if n in nums_quentes)
        if qtd_quentes >= 3:
            motivos.append(f"{qtd_quentes} numeros entre os mais frequentes")

        em_alta_total = []
        for janela, dados in (tendencias or {}).items():
            em_alta_total.extend(item["numero"] for item in dados.get("em_alta", []))
        qtd_tendencia = sum(1 for n in numeros if n in em_alta_total)
        if qtd_tendencia >= 2:
            motivos.append(f"{qtd_tendencia} numeros em tendencia de alta")

        atrasados = [n for n, info in (intervalos or {}).items() if info.get("atrasado")]
        qtd_atrasados = sum(1 for n in numeros if n in atrasados)
        if qtd_atrasados >= 2:
            motivos.append(f"{qtd_atrasados} numeros atrasados acima da media")

        if not motivos:
            motivos.append("Combinacao gerada por analise estatistica")

        return motivos

    def _calcular_distribuicao_numeros(self, numeros: list, config: dict) -> dict:
        """Calcula distribuicao dos numeros por tercos"""
        minimo = config["min_num"]
        maximo = config["max_num"]
        faixa = maximo - minimo + 1
        terco = faixa / 3

        primeiro_terco = sum(1 for n in numeros if n < minimo + terco)
        segundo_terco = sum(1 for n in numeros if minimo + terco <= n < minimo + 2*terco)
        terceiro_terco = len(numeros) - primeiro_terco - segundo_terco

        total = len(numeros)

        return {
            "primeiro_terco": primeiro_terco,
            "segundo_terco": segundo_terco,
            "terceiro_terco": terceiro_terco,
            "percentual_primeiro_terco": round(primeiro_terco/total*100, 1) if total > 0 else 0,
            "percentual_segundo_terco": round(segundo_terco/total*100, 1) if total > 0 else 0,
            "percentual_terceiro_terco": round(terceiro_terco/total*100, 1) if total > 0 else 0
        }

    # ========================================
    # METODOS DE COMPATIBILIDADE
    # ========================================

    def obter_resumo_estatisticas(self, resultados: list, config: dict) -> dict:
        """Retorna resumo completo de estatisticas"""
        return self._calcular_estatisticas_completas(resultados, config)

    def gerar_sugestao_ia(self, resultados: list, config: dict, quantidade: int = 1) -> list:
        """Metodo principal de geracao de sugestoes"""
        return self.gerar_sugestoes_avancadas(resultados, config, quantidade)
