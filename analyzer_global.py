"""
Motor de Analise Global - Tecnicas Mundiais de Loterias
Implementa as melhores estrategias de todas as escolas de analise
"""
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations
import math
import json
from base_analyzer import AnalisadorBase


class AnalisadorGlobal(AnalisadorBase):
    """
    Analisador que implementa tecnicas de analise de loterias de todo o mundo
    Combina metodos europeus, americanos e asiaticos
    """
    
    def __init__(self):
        super().__init__()
        self.estrategias = {}
    
    # ==========================================
    # ESTRATEGIA EUROPEIA - Analise de Ciclos
    # ==========================================
    
    def analise_ciclos_longos(self, resultados: list, config: dict, janela_grande: int = 100) -> dict:
        """
        Analise de ciclos longos (100+ sorteios)
        Tecnicas europeias de deteccao de padroes
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        if len(resultados) < janela_grande:
            janela_grande = len(resultados)
        
        # Analisar em blocos de 10 sorteios
        blocos = []
        tamanho_bloco = 10
        
        for i in range(0, min(janela_grande, len(resultados)), tamanho_bloco):
            bloco = resultados[i:i+tamanho_bloco]
            freq_bloco = Counter()
            for r in bloco:
                for d in r.get("listaDezenas", []):
                    freq_bloco[int(d)] += 1
            blocos.append(dict(freq_bloco))
        
        # Detectar tendencia entre blocos
        tendencias = defaultdict(list)
        for num in range(minimo, maximo + 1):
            valores = [bloco.get(num, 0) for bloco in blocos]
            if len(valores) >= 2:
                # Calcular tendencia (inclinacao da reta)
                x = np.arange(len(valores))
                y = np.array(valores)
                if np.std(y) > 0:
                    inclinacao = np.polyfit(x, y, 1)[0]
                    tendencias[num] = {
                        "inclinacao": round(float(inclinacao), 4),
                        "tendencia": "subindo" if inclinacao > 0.1 else "descendo" if inclinacao < -0.1 else "estavel",
                        "media": round(float(np.mean(y)), 2),
                        "ultima": valores[-1] if valores else 0
                    }
        
        # Numeros em ciclo subindo (bons para proximo sorteio)
        numeros_ciclo_positivo = [n for n, t in tendencias.items() 
                                   if t["tendencia"] == "subindo" and t["inclinacao"] > 0.2]
        
        # Numeros em ciclo descendente
        numeros_ciclo_negativo = [n for n, t in tendencias.items() 
                                   if t["tendencia"] == "descendo" and t["inclinacao"] < -0.2]
        
        return {
            "metodo": "Analise de Ciclos Longos (Europa)",
            "total_blocos": len(blocos),
            "tendencias": tendencias,
            "numeros_ciclo_positivo": sorted(numeros_ciclo_positivo),
            "numeros_ciclo_negativo": sorted(numeros_ciclo_negativo),
            "recomendacao": "Numeros em ciclo positivo tem maior chance de aparecer"
        }
    
    # ==========================================
    # ESTRATEGIA AMERICANA - Monte Carlo Avancado
    # ==========================================
    
    def monte_carlo_avancado(self, resultados: list, config: dict, simulacoes: int = 50000) -> dict:
        """
        Simulacao Monte Carlo com 50.000+ iteracoes
        Tecnicas americanas de simulacao estocastica
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        
        # Calcular probabilidades historicas
        historico = Counter()
        for r in resultados:
            for d in r.get("listaDezenas", []):
                historico[int(d)] += 1
        
        total = sum(historico.values())
        probs = {n: historico.get(n, 0) / total for n in range(minimo, maximo + 1)}
        
        # Executar simulacoes
        contagem = Counter()
        contagem_combinacoes = Counter()
        
        for _ in range(simulacoes):
            numeros = []
            probs_temp = list(probs.values())
            nums = list(probs.keys())
            
            for _ in range(qtd_escolher):
                if sum(probs_temp) > 0:
                    escolhido = np.random.choice(nums, p=probs_temp)
                    numeros.append(int(escolhido))
                    idx = nums.index(escolhido)
                    probs_temp[idx] = 0
                    soma = sum(probs_temp)
                    if soma > 0:
                        probs_temp = [p/soma for p in probs_temp]
            
            numeros = sorted(numeros)
            contagem.update(numeros)
            contagem_combinacoes[tuple(numeros)] += 1
        
        # Estatisticas
        prob_estimadas = {n: round(contagem.get(n, 0) / simulacoes * 100, 4) 
                          for n in range(minimo, maximo + 1)}
        
        top_combinacoes = [
            {"numeros": list(c), "frequencia": f, "probabilidade": round(f/simulacoes*100, 4)}
            for c, f in contagem_combinacoes.most_common(20)
        ]
        
        return {
            "metodo": "Monte Carlo Avancado (Americas)",
            "simulacoes": simulacoes,
            "probabilidades_estimadas": prob_estimadas,
            "top_combinacoes": top_combinacoes,
            "top_numeros": sorted(prob_estimadas.items(), key=lambda x: x[1], reverse=True)[:15]
        }
    
    # ==========================================
    # ESTRATEGIA ASIATICA - Padroes Numerologicos
    # ==========================================
    
    def analise_padroes_asiatica(self, resultados: list, config: dict) -> dict:
        """
        Analise de padroes numericos asiaticos
        Inclui Fibonacci, primos, simetria e numerologia
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        # Numeros primos
        primos = self._encontrar_primos(minimo, maximo)
        
        # Sequencia de Fibonacci na faixa
        fibonacci = self._fibonacci_na_faixa(minimo, maximo)
        
        # Analisar presenca nos resultados
        todos_numeros = []
        for r in resultados:
            todos_numeros.extend([int(d) for d in r.get("listaDezenas", [])])
        
        contador = Counter(todos_numeros)
        
        # Frequencia de primos vs nao-primos
        freq_primos = sum(contador.get(p, 0) for p in primos)
        freq_nao_primos = sum(contador.get(n, 0) for n in range(minimo, maximo + 1) if n not in primos)
        total = freq_primos + freq_nao_primos
        
        # Numeros "da sorte" (aparecem mais que a media)
        media = total / (maximo - minimo + 1) if (maximo - minimo + 1) > 0 else 0
        numeros_sorte = [n for n in range(minimo, maximo + 1) if contador.get(n, 0) > media * 1.2]
        
        # Analise de simetria
        simetria = {}
        for num in range(minimo, maximo + 1):
            inverso = maximo - num + minimo
            if inverso <= maximo:
                freq_num = contador.get(num, 0)
                freq_inverso = contador.get(inverso, 0)
                simetria[num] = {
                    "par": inverso,
                    "freq": freq_num,
                    "freq_par": freq_inverso,
                    "balanceado": abs(freq_num - freq_inverso) < 3
                }
        
        return {
            "metodo": "Analise Asiatica de Padroes",
            "primos": primos,
            "fibonacci": fibonacci,
            "frequencia_primos": round(freq_primos / total * 100, 2) if total > 0 else 0,
            "frequencia_nao_primos": round(freq_nao_primos / total * 100, 2) if total > 0 else 0,
            "numeros_da_sorte": numeros_sorte,
            "simetria": simetria,
            "analise_sorte": {
                "total_sorte": len(numeros_sorte),
                "percentual": round(len(numeros_sorte) / (maximo - minimo + 1) * 100, 2)
            }
        }
    
    def _encontrar_primos(self, minimo: int, maximo: int) -> list:
        """Encontra numeros primos na faixa"""
        primos = []
        for num in range(max(2, minimo), maximo + 1):
            if self._eh_primo(num):
                primos.append(num)
        return primos
    
    def _eh_primo(self, n: int) -> bool:
        """Verifica se um numero e primo"""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def _fibonacci_na_faixa(self, minimo: int, maximo: int) -> list:
        """Retorna numeros de Fibonacci na faixa"""
        fib = [0, 1]
        while fib[-1] < maximo:
            fib.append(fib[-1] + fib[-2])
        return [f for f in fib if minimo <= f <= maximo]
    
    # ==========================================
    # ESTRATEGIA GLOBAL - Ensemble Universal
    # ==========================================
    
    def ensemble_universal(self, resultados: list, config: dict) -> dict:
        """
        Combina todas as estrategias mundiais em um ensemble universal
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        # Executar todas as estrategias
        ciclos = self.analise_ciclos_longos(resultados, config)
        monte_carlo = self.monte_carlo_avancado(resultados, config, 10000)
        padroes = self.analise_padroes_asiatica(resultados, config)
        
        # Probabilidades de cada metodo
        probs_ciclos = {n: 50 for n in range(minimo, maximo + 1)}  # Base
        for n in ciclos.get("numeros_ciclo_positivo", []):
            if n in probs_ciclos:
                probs_ciclos[n] += 30
        for n in ciclos.get("numeros_ciclo_negativo", []):
            if n in probs_ciclos:
                probs_ciclos[n] -= 20
        
        probs_monte = monte_carlo.get("probabilidades_estimadas", {})
        
        probs_padroes = {n: 50 for n in range(minimo, maximo + 1)}
        for n in padroes.get("numeros_da_sorte", []):
            if n in probs_padroes:
                probs_padroes[n] += 25
        
        # Combinar com pesos
        pesos = {"ciclos": 0.35, "monte_carlo": 0.40, "padroes": 0.25}
        
        probs_finais = {}
        for num in range(minimo, maximo + 1):
            soma = (
                probs_ciclos.get(num, 50) * pesos["ciclos"] +
                probs_monte.get(num, 50) * pesos["monte_carlo"] +
                probs_padroes.get(num, 50) * pesos["padroes"]
            )
            probs_finais[num] = round(soma, 4)
        
        # Normalizar
        soma_total = sum(probs_finais.values())
        if soma_total > 0:
            probs_finais = {k: round(v/soma_total * 100, 4) for k, v in probs_finais.items()}
        
        return {
            "metodo": "Ensemble Universal (Global)",
            "estrategias": ["Ciclos Longos (Europa)", "Monte Carlo (Americas)", "Padroes Asiaticos"],
            "pesos": pesos,
            "probabilidades_finais": probs_finais,
            "top_numeros": sorted(probs_finais.items(), key=lambda x: x[1], reverse=True)[:20],
            "detalhes": {
                "ciclos": ciclos,
                "monte_carlo": {"top": monte_carlo.get("top_numeros", [])[:10]},
                "padroes": {
                    "primos": padroes.get("primos", [])[:10],
                    "fibonacci": padroes.get("fibonacci", [])[:10],
                    "sorte": padroes.get("numeros_da_sorte", [])[:10]
                }
            }
        }
    
    # ==========================================
    # GERADOR DE SUGESTOES GLOBAIS
    # ========================================
    
    def gerar_sugestoes_globais(self, resultados: list, config: dict, quantidade: int = 10) -> list:
        """
        Gera sugestoes usando todas as tecnicas globais
        """
        print("\n🌍 Executando Analise Global Completa...")
        
        ensemble = self.ensemble_universal(resultados, config)
        probs = ensemble["probabilidades_finais"]
        
        # Ordenar numeros
        numeros_ordenados = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        
        # Tiers globais
        tier_s = [n for n, _ in numeros_ordenados[:15]]
        tier_a = [n for n, _ in numeros_ordenados[15:30]]
        tier_b = [n for n, _ in numeros_ordenados[30:]]
        
        combinacoes = []
        
        estrategias_globais = [
            ("europeu_balanceado", 0.5, 0.3, 0.2),
            ("americano_ousado", 0.7, 0.2, 0.1),
            ("asiatico_sorte", 0.4, 0.4, 0.2),
            ("global_enhanced", 0.6, 0.3, 0.1),
            ("hibrido_otimo", 0.55, 0.35, 0.1)
        ]
        
        for i in range(quantidade):
            est_nome, p_s, p_a, p_b = estrategias_globais[i % len(estrategias_globais)]
            
            qtd_s = int(qtd_escolher * p_s)
            qtd_a = int(qtd_escolher * p_a)
            qtd_b = qtd_escolher - qtd_s - qtd_a
            
            numeros = []
            
            if tier_s and qtd_s > 0:
                numeros.extend(list(np.random.choice(tier_s, min(qtd_s, len(tier_s)), replace=False)))
            if tier_a and qtd_a > 0:
                numeros.extend(list(np.random.choice(tier_a, min(qtd_a, len(tier_a)), replace=False)))
            if tier_b and qtd_b > 0:
                numeros.extend(list(np.random.choice(tier_b, min(qtd_b, len(tier_b)), replace=False)))
            
            while len(numeros) < qtd_escolher:
                num = np.random.randint(minimo, maximo + 1)
                if num not in numeros:
                    numeros.append(num)
            
            numeros = sorted([int(x) for x in numeros[:qtd_escolher]])
            
            confianca = sum(probs.get(n, 0) for n in numeros) / qtd_escolher
            
            combinacoes.append({
                "numeros": numeros,
                "estrategia": est_nome,
                "confianca": round(confianca, 2),
                "probabilidade_conjunta": round(math.prod([probs.get(n, 1)/100 for n in numeros]) * 100, 6)
            })
        
        combinacoes.sort(key=lambda x: x["confianca"], reverse=True)
        
        print(f"✅ Analise Global Concluida! {len(combinacoes)} combinacoes geradas")
        
        return {
            "ensemble": ensemble,
            "combinacoes": combinacoes,
            "total_geradas": len(combinacoes)
        }


# Instancia global
analisador_global = AnalisadorGlobal()
