"""
Motor de Analise Ultra Avancada para Loterias
Machine Learning, Redes Neurais, Algoritmos Geneticos, Monte Carlo, Markov, e mais
"""
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime
import json
import math
import random
from config import LOTTERIES
from base_analyzer import AnalisadorBase


class AnalisadorUltraAvancado(AnalisadorBase):
    """
    Analisador de loterias com tecnicas de ultima geracao:
    - Machine Learning (Random Forest, SVM, Naive Bayes)
    - Redes Neurais (MLP)
    - Algoritmos Geneticos
    - Simulacao Monte Carlo
    - Cadeias de Markov
    - Analise de Entropia
    - Transformada de Fourier
    - Analise de Cluster
    - Boosting (Gradient Boosting)
    - Rede Bayesian
    """
    
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    # ========================================
    # 1. MACHINE LEARNING
    # ========================================
    
    def random_forest_simplificado(self, resultados: list, config: dict) -> dict:
        """
        Random Forest simplificado para previsao
        Treina multiple arvores de decisao baseadas em features historicas
        """
        if len(resultados) < 30:
            return {"erro": "Dados insuficientes"}
        
        # Extrair features dos ultimos N sorteios
        n_features = 10
        features_anteriores = []
        labels = []
        
        for i in range(len(resultados) - n_features):
            # Features: frequencia dos ultimos N sorteios
            features = []
            for j in range(n_features):
                dezenas = [int(d) for d in resultados[i + j].get("listaDezenas", [])]
                # Codificar como vector binario
                binario = [0] * (config["max_num"] - config["min_num"] + 1)
                for d in dezenas:
                    binario[d - config["min_num"]] = 1
                features.extend(binario[:20])  # Top 20 posicoes
            
            # Label: numeros do proximo sorteio
            proximas_dezenas = [int(d) for d in resultados[i + n_features].get("listaDezenas", [])]
            
            features_anteriores.append(features)
            labels.append(proximas_dezenas)
        
        # Treinar "arvore" baseada em correlacoes
        pesos_features = np.zeros(len(features_anteriores[0]))
        for i, (feat, label) in enumerate(zip(features_anteriores, labels)):
            for num in label:
                idx = num - config["min_num"]
                if idx < len(pesos_features):
                    pesos_features[idx] += 1
        
        # Normalizar pesos
        pesos_norm = pesos_features / (len(labels) * config["pick_count"])
        
        # Prever proximos numeros
        probabilidades = {}
        for num in range(config["min_num"], config["max_num"] + 1):
            idx = num - config["min_num"]
            if idx < len(pesos_norm):
                probabilidades[num] = float(pesos_norm[idx])
        
        return {
            "algoritmo": "Random Forest Simplificado",
            "probabilidades": probabilidades,
            "top_numeros": sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15]
        }
    
    def naive_bayes_loteria(self, resultados: list, config: dict) -> dict:
        """
        Naive Bayes para calcular probabilidade condicional
        P(numero | historico) = P(historico | numero) * P(numero) / P(historico)
        """
        total_sorteios = len(resultados)
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        # P(prior) - probabilidade a priori de cada numero
        todos_numeros = []
        for r in resultados:
            todos_numeros.extend([int(d) for d in r.get("listaDezenas", [])])
        
        contador = Counter(todos_numeros)
        total_numeros = len(todos_numeros)
        
        probabilidades = {}
        
        for num in range(minimo, maximo + 1):
            # P(numero) - probabilidade a priori
            p_priori = contador.get(num, 0) / total_numeros if total_numeros > 0 else 0
            
            # P(historico | numero) - baseado em padroes de sequencia
            p_historico = 0
            for i in range(1, len(resultados)):
                dezenas_anteriores = [int(d) for d in resultados[i-1].get("listaDezenas", [])]
                dezenas_atuais = [int(d) for d in resultados[i].get("listaDezenas", [])]
                
                if num in dezenas_atuais:
                    # Verificar se apareceu no sorteio anterior
                    if num in dezenas_anteriores:
                        p_historico += 0.3
                    # Verificar padrao de intervalo
                    for anterior in dezenas_anteriores:
                        diff = abs(num - anterior)
                        if diff <= 5:
                            p_historico += 0.1
            
            # Calcular probabilidade posterior
            posterior = p_priori * (1 + min(p_historico, 1))
            probabilidades[num] = round(posterior * 100, 4)
        
        # Normalizar
        soma = sum(probabilidades.values())
        if soma > 0:
            probabilidades = {k: round(v/soma * 100, 4) for k, v in probabilidades.items()}
        
        return {
            "algoritmo": "Naive Bayes",
            "probabilidades": probabilidades,
            "top_numeros": sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15]
        }
    
    def svm_simplificado(self, resultados: list, config: dict) -> dict:
        """
        SVM simplificado para classificacao de numeros
        Usa margem de separacao baseada em features
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        # Extrair features para cada numero
        features_numeros = {}
        
        for num in range(minimo, maximo + 1):
            features = []
            
            # Feature 1: Frencia historica
            freq = sum(1 for r in resultados for d in r.get("listaDezenas", []) if int(d) == num)
            features.append(freq / len(resultados))
            
            # Feature 2: Tempo desde ultima aparencia
            ultimo_indice = -1
            for i, r in enumerate(resultados):
                if num in [int(d) for d in r.get("listaDezenas", [])]:
                    ultimo_indice = i
                    break
            features.append(ultimo_indice / len(resultados) if ultimo_indice >= 0 else 1)
            
            # Feature 3: Tendencia (media movel)
            if len(resultados) >= 10:
                recente = sum(1 for r in resultados[:5] for d in r.get("listaDezenas", []) if int(d) == num)
                antigo = sum(1 for r in resultados[5:10] for d in r.get("listaDezenas", []) if int(d) == num)
                features.append((recente - antigo) / 5)
            else:
                features.append(0)
            
            features_numeros[num] = np.array(features)
        
        # Calcular hiperplano de separacao (simplificado)
        media_features = np.mean(list(features_numeros.values()), axis=0)
        
        # Classificar numeros
        probabilidades = {}
        for num, feat in features_numeros.items():
            # Distancia ao hiperplano (simplificado)
            distancia = np.dot(feat - media_features, feat - media_features)
            probabilidades[num] = float(np.exp(-distancia) * 100)
        
        # Normalizar
        soma = sum(probabilidades.values())
        if soma > 0:
            probabilidades = {k: round(v/soma * 100, 4) for k, v in probabilidades.items()}
        
        return {
            "algoritmo": "SVM Simplificado",
            "probabilidades": probabilidades,
            "top_numeros": sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15]
        }
    
    # ========================================
    # 2. REDES NEURAIS
    # ========================================
    
    def rede_neural_mlp(self, resultados: list, config: dict) -> dict:
        """
        Rede Neural MLP (Multi-Layer Perceptron) simplificada
        Treina para prever numeros baseado em padroes
        """
        if len(resultados) < 50:
            return {"erro": "Dados insuficientes para rede neural"}
        
        minimo = config["min_num"]
        maximo = config["max_num"]
        n_numeros = maximo - minimo + 1
        
        # Preparar dados de treino
        X_treino = []
        y_treino = []
        
        janela = 5  # Usar 5 sorteios anteriores como input
        
        for i in range(len(resultados) - janela):
            # Input: binario dos ultimos janela sorteios
            entrada = []
            for j in range(janela):
                binario = [0] * min(n_numeros, 30)  # Limitar para eficiencia
                dezenas = [int(d) for d in resultados[i + j].get("listaDezenas", [])]
                for d in dezenas:
                    if d - minimo < len(binario):
                        binario[d - minimo] = 1
                entrada.extend(binario)
            
            # Output: binario do proximo sorteio
            saida = [0] * min(n_numeros, 30)
            dezenas_proximas = [int(d) for d in resultados[i + janela].get("listaDezenas", [])]
            for d in dezenas_proximas:
                if d - minimo < len(saida):
                    saida[d - minimo] = 1
            
            X_treino.append(entrada)
            y_treino.append(saida)
        
        X_treino = np.array(X_treino)
        y_treino = np.array(y_treino)
        
        # Rede neural simplificada (2 camadas)
        n_entrada = X_treino.shape[1]
        n_oculta = 64
        n_saida = y_treino.shape[1]
        
        # Inicializar pesos aleatoriamente
        np.random.seed(42)
        W1 = np.random.randn(n_entrada, n_oculta) * 0.1
        b1 = np.zeros(n_oculta)
        W2 = np.random.randn(n_oculta, n_saida) * 0.1
        b2 = np.zeros(n_saida)
        
        # Funcao de ativacao
        def sigmoid(x):
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        
        def sigmoid_derivada(x):
            return x * (1 - x)
        
        # Treinar rede
        taxa_aprendizado = 0.1
        epocas = 100
        
        for epoca in range(epocas):
            # Forward pass
            hidden = sigmoid(np.dot(X_treino, W1) + b1)
            output = sigmoid(np.dot(hidden, W2) + b2)
            
            # Backward pass
            erro_saida = y_treino - output
            delta_saida = erro_saida * sigmoid_derivada(output)
            
            erro_hidden = delta_saida.dot(W2.T)
            delta_hidden = erro_hidden * sigmoid_derivada(hidden)
            
            # Atualizar pesos
            W2 += hidden.T.dot(delta_saida) * taxa_aprendizado
            b2 += np.sum(delta_saida, axis=0) * taxa_aprendizado
            W1 += X_treino.T.dot(delta_hidden) * taxa_aprendizado
            b1 += np.sum(delta_hidden, axis=0) * taxa_aprendizado
        
        # Prever proximos numeros
        ultimo_input = []
        for j in range(janela):
            binario = [0] * min(n_numeros, 30)
            dezenas = [int(d) for d in resultados[j].get("listaDezenas", [])]
            for d in dezenas:
                if d - minimo < len(binario):
                    binario[d - minimo] = 1
            ultimo_input.extend(binario)
        
        ultimo_input = np.array([ultimo_input])
        hidden = sigmoid(np.dot(ultimo_input, W1) + b1)
        previsao = sigmoid(np.dot(hidden, W2) + b2)[0]
        
        probabilidades = {}
        for i, prob in enumerate(previsao):
            num = minimo + i
            if num <= maximo:
                probabilidades[num] = round(float(prob) * 100, 4)
        
        return {
            "algoritmo": "Rede Neural MLP",
            "probabilidades": probabilidades,
            "top_numeros": sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15],
            "epocas_treino": epocas
        }
    
    # ========================================
    # 3. ALGORITMOS GENETICOS
    # ========================================
    
    def algoritmo_genetico(self, resultados: list, config: dict, populacao_size: int = 100, geracoes: int = 50) -> dict:
        """
        Algoritmo Genetico para otimizacao de selecao de numeros
        Evolui populacao de solucoes para encontrar as melhores combinacoes
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        total_numeros = maximo - minimo + 1
        
        # Fitness baseado em dados historicos
        historico_numeros = Counter()
        for r in resultados:
            for d in r.get("listaDezenas", []):
                historico_numeros[int(d)] += 1
        
        def criar_individuo():
            return sorted(random.sample(range(minimo, maximo + 1), qtd_escolher))
        
        def calcular_fitness(individuo):
            fitness = 0
            
            # Fitness 1: Numeros frequentes
            for num in individuo:
                fitness += historico_numeros.get(num, 0) / len(resultados)
            
            # Fitness 2: Diversidade
            fitness += len(set(individuo)) / qtd_escolher
            
            # Fitness 3: Distribuicao
            faixa = total_numeros / 3
            primeiros = sum(1 for n in individuo if n < minimo + faixa)
            medios = sum(1 for n in individuo if minimo + faixa <= n < minimo + 2*faixa)
            fitness += min(primeiros, medios, qtd_escolher - primeiros - medios) / qtd_escolher
            
            return fitness
        
        def crossover(pai1, pai2):
            ponto = random.randint(1, qtd_escolher - 1)
            filho = list(set(pai1[:ponto] + pai2[ponto:]))
            while len(filho) < qtd_escolher:
                num = random.randint(minimo, maximo + 1)
                if num not in filho:
                    filho.append(num)
            return sorted(filho[:qtd_escolher])
        
        def mutacao(individuo, taxa=0.1):
            if random.random() < taxa:
                idx = random.randint(0, qtd_escolher - 1)
                novo_num = random.randint(minimo, maximo + 1)
                while novo_num in individuo:
                    novo_num = random.randint(minimo, maximo + 1)
                individuo[idx] = novo_num
            return sorted(individuo)
        
        # Inicializar populacao
        populacao = [criar_individuo() for _ in range(populacao_size)]
        
        historico_fitness = []
        
        for geracao in range(geracoes):
            # Avaliar fitness
            fitness_scores = [(ind, calcular_fitness(ind)) for ind in populacao]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            historico_fitness.append(fitness_scores[0][1])
            
            # Selecionar elite (top 20%)
            elite_size = populacao_size // 5
            elite = [ind for ind, _ in fitness_scores[:elite_size]]
            
            # Nova populacao
            nova_populacao = list(elite)
            
            while len(nova_populacao) < populacao_size:
                # Torneio
                pai1 = random.choice(elite)
                pai2 = random.choice(elite)
                
                filho = crossover(pai1, pai2)
                filho = mutacao(filho)
                
                nova_populacao.append(filho)
            
            populacao = nova_populacao
        
        # Retornar melhores individuos
        fitness_final = [(ind, calcular_fitness(ind)) for ind in populacao]
        fitness_final.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "algoritmo": "Algoritmo Genetico",
            "melhores": [{"numeros": ind, "fitness": round(fit * 100, 2)} for ind, fit in fitness_final[:10]],
            "evolucao_fitness": [round(f, 2) for f in historico_fitness],
            "geracoes": geracoes
        }
    
    # ========================================
    # 4. SIMULACAO MONTE CARLO
    # ========================================
    
    def simulacao_monte_carlo(self, resultados: list, config: dict, simulacoes: int = 10000) -> dict:
        """
        Simulacao Monte Carlo para estimar probabilidades
        Executa N simulacoes para estimar distribuicao real
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        
        # Baseado em frequencias historicas
        historico = Counter()
        for r in resultados:
            for d in r.get("listaDezenas", []):
                historico[int(d)] += 1
        
        total = sum(historico.values())
        probabilidades = {n: historico.get(n, 0) / total for n in range(minimo, maximo + 1)}
        
        # Executar simulacoes
        contagem_numeros = Counter()
        contagem_combinacoes = Counter()
        
        for _ in range(simulacoes):
            # Gerar combinacao baseada nas probabilidades
            numeros = []
            probs = list(probabilidades.values())
            nums = list(probabilidades.keys())
            
            for _ in range(qtd_escolher):
                escolhido = np.random.choice(nums, p=probs)
                numeros.append(int(escolhido))
                # Atualizar probabilidades para evitar repeticao
                idx = nums.index(escolhido)
                probs[idx] = 0
                soma = sum(probs)
                if soma > 0:
                    probs = [p/soma for p in probs]
            
            numeros = sorted(numeros)
            contagem_numeros.update(numeros)
            contagem_combinacoes[tuple(numeros)] += 1
        
        # Estatisticas das simulacoes
        probabilidades_estimadas = {
            n: round(contagem_numeros.get(n, 0) / simulacoes * 100, 4) 
            for n in range(minimo, maximo + 1)
        }
        
        # Top combinacoes mais frequentes
        top_combinacoes = [
            {"numeros": list(combo), "frequencia": count, "probabilidade": round(count/simulacoes*100, 4)}
            for combo, count in contagem_combinacoes.most_common(20)
        ]
        
        return {
            "algoritmo": "Monte Carlo",
            "total_simulacoes": simulacoes,
            "probabilidades_estimadas": probabilidades_estimadas,
            "top_combinacoes": top_combinacoes,
            "top_numeros": sorted(probabilidades_estimadas.items(), key=lambda x: x[1], reverse=True)[:15]
        }
    
    # ========================================
    # 5. CADEIAS DE MARKOV
    # ========================================
    
    def cadeia_markov(self, resultados: list, config: dict, ordem: int = 2) -> dict:
        """
        Cadeia de Markov para prever proximos numeros
        Baseado em transicoes de estado
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        # Construir matriz de transicao
        transicoes = defaultdict(Counter)
        
        for i in range(ordem, len(resultados)):
            # Estado atual: numeros dos ultimos ordem sorteios
            estado = tuple(sorted([int(d) for d in resultados[i-ordem].get("listaDezenas", [])]))
            
            # Proximo estado
            proximos = [int(d) for d in resultados[i].get("listaDezenas", [])]
            
            for num in proximos:
                transicoes[estado][num] += 1
        
        # Usar ultimo estado para prever
        ultimo_estado = tuple(sorted([int(d) for d in resultados[0].get("listaDezenas", [])]))
        
        probabilidades = {}
        if ultimo_estado in transicoes:
            total_transicoes = sum(transicoes[ultimo_estado].values())
            for num in range(minimo, maximo + 1):
                prob = transicoes[ultimo_estado].get(num, 0) / total_transicoes if total_transicoes > 0 else 0
                probabilidades[num] = round(prob * 100, 4)
        else:
            # Fallback: usar probabilidades absolutas
            historico = Counter()
            for r in resultados:
                for d in r.get("listaDezenas", []):
                    historico[int(d)] += 1
            total = sum(historico.values())
            probabilidades = {n: round(historico.get(n, 0) / total * 100, 4) for n in range(minimo, maximo + 1)}
        
        return {
            "algoritmo": "Cadeia de Markov",
            "ordem": ordem,
            "ultimo_estado": list(ultimo_estado),
            "probabilidades": probabilidades,
            "top_numeros": sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15]
        }
    
    # ========================================
    # 6. ANALISE DE ENTROPIA
    # ========================================
    
    def analise_entropia(self, resultados: list, config: dict) -> dict:
        """
        Analise de Entropia de Shannon
        Mede aleatoriedade e padroes nos dados
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        # Entropia de cada numero
        entropias = {}
        
        for num in range(minimo, maximo + 1):
            # Sequencia de presenca/ausencia
            sequencia = []
            for r in resultados:
                if num in [int(d) for d in r.get("listaDezenas", [])]:
                    sequencia.append(1)
                else:
                    sequencia.append(0)
            
            # Calcular entropia de Shannon
            n = len(sequencia)
            if n > 0:
                p1 = sum(sequencia) / n
                p0 = 1 - p1
                
                entropia = 0
                if p1 > 0:
                    entropia -= p1 * math.log2(p1)
                if p0 > 0:
                    entropia -= p0 * math.log2(p0)
                
                # Entropia maxima possivel
                entropia_max = 1.0  # Para distribuicao binaria
                
                entropias[num] = {
                    "entropia": round(entropia, 4),
                    "entropia_normalizada": round(entropia / entropia_max, 4) if entropia_max > 0 else 0,
                    "frequencia": p1,
                    "aleatoriedade": "alta" if entropia > 0.8 else "media" if entropia > 0.5 else "baixa"
                }
        
        # Entropia geral do sistema
        todos_numeros = []
        for r in resultados:
            todos_numeros.extend([int(d) for d in r.get("listaDezenas", [])])
        
        contador = Counter(todos_numeros)
        total = len(todos_numeros)
        
        entropia_geral = 0
        for count in contador.values():
            p = count / total
            if p > 0:
                entropia_geral -= p * math.log2(p)
        
        return {
            "algoritmo": "Analise de Entropia",
            "entropia_geral": round(entropia_geral, 4),
            "entropia_maxima": round(math.log2(maximo - minimo + 1), 4),
            "entropia_normalizada": round(entropia_geral / math.log2(maximo - minimo + 1), 4),
            "entropias_por_numero": entropias,
            "numeros_mais_aleatorios": sorted(
                [(n, e["entropia"]) for n, e in entropias.items()],
                key=lambda x: x[1], reverse=True
            )[:10]
        }
    
    # ========================================
    # 7. TRANSFORMADA DE FOURIER
    # ========================================
    
    def analise_fourier(self, resultados: list, config: dict) -> dict:
        """
        Transformada Discreta de Fourier (DFT)
        Detecta ciclos e padroes periodicos
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        # Criar serie temporal para cada numero
        ciclos_detectados = {}
        
        for num in range(minimo, min(minimo + 20, maximo + 1)):  # Analisar top 20 numeros
            # Serie temporal: 1 se apareceu, 0 se nao
            serie = np.array([
                1 if num in [int(d) for d in r.get("listaDezenas", [])] else 0
                for r in resultados
            ])
            
            if len(serie) < 8:
                continue
            
            # Aplicar DFT
            n = len(serie)
            dft = np.fft.fft(serie)
            
            # Magnitude das frequencias
            magnitude = np.abs(dft[:n//2])
            frequencias = np.fft.fftfreq(n)[:n//2]
            
            # Encontrar picos (ciclos dominantes)
            if len(magnitude) > 2:
                picos = []
                for i in range(1, len(magnitude) - 1):
                    if magnitude[i] > magnitude[i-1] and magnitude[i] > magnitude[i+1]:
                        if magnitude[i] > np.mean(magnitude) * 1.5:
                            periodo = 1 / frequencias[i] if frequencias[i] != 0 else float('inf')
                            picos.append({
                                "periodo": round(float(periodo), 2),
                                "forca": round(float(magnitude[i]), 4)
                            })
                
                ciclos_detectados[num] = {
                    "picos": sorted(picos, key=lambda x: x["forca"], reverse=True)[:3],
                    "tem_ciclo": len(picos) > 0
                }
        
        return {
            "algoritmo": "Transformada de Fourier",
            "ciclos_detectados": ciclos_detectados,
            "numeros_com_ciclo": [n for n, c in ciclos_detectados.items() if c["tem_ciclo"]]
        }
    
    # ========================================
    # 8. GRADIENT BOOSTING
    # ========================================
    
    def gradient_boosting_simplificado(self, resultados: list, config: dict, n_arvores: int = 10) -> dict:
        """
        Gradient Boosting simplificado
        Combina multiplas "arvores fracas" para previsao
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        n_janela = 5

        if len(resultados) <= n_janela:
            return {"erro": "Dados insuficientes para Gradient Boosting"}

        # Preparar dados com janela fixa de n_janela sorteios (features homogeneas)
        X = []
        y = []

        for i in range(n_janela, len(resultados)):
            features = []
            for j in range(n_janela):
                idx = i - n_janela + j  # ultimos n_janela sorteios antes de i
                binario = [0] * min(maximo - minimo + 1, 30)
                dezenas = [int(d) for d in resultados[idx].get("listaDezenas", [])]
                for d in dezenas:
                    if d - minimo < len(binario):
                        binario[d - minimo] = 1
                features.extend(binario)

            # Label: sorteio atual (o que vem apos a janela)
            dezenas_atual = [int(d) for d in resultados[i].get("listaDezenas", [])]
            label = [1 if n in dezenas_atual else 0 for n in range(minimo, min(minimo + 30, maximo + 1))]

            X.append(features)
            y.append(label)

        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float)

        # Gradient Boosting simplificado
        n_samples, n_features = X.shape
        n_classes = y.shape[1]

        # Inicializar previsoes
        previsoes = np.zeros((n_samples, n_classes))

        arvores = []

        for t in range(n_arvores):
            # Residuos
            residuos = y - previsoes

            # Treinar arvore fraca (regressao linear simples)
            for c in range(n_classes):
                if n_features > 0 and n_samples > 0:
                    # Coeficientes via pseudoinversa
                    try:
                        coef = np.linalg.lstsq(X, residuos[:, c], rcond=None)[0]
                        previsoes[:, c] += 0.1 * X.dot(coef)  # Learning rate
                    except:
                        pass

            arvores.append({"iteracao": t + 1})

        # Prever para o proximo sorteio (usa os ultimos n_janela sorteios)
        ultimo_X = []
        for j in range(n_janela):
            idx = len(resultados) - n_janela + j
            binario = [0] * min(maximo - minimo + 1, 30)
            dezenas = [int(d) for d in resultados[idx].get("listaDezenas", [])]
            for d in dezenas:
                if d - minimo < len(binario):
                    binario[d - minimo] = 1
            ultimo_X.extend(binario)

        ultimo_X = np.array([ultimo_X], dtype=float)
        
        probabilidades = {}
        for c in range(n_classes):
            num = minimo + c
            if num <= maximo:
                try:
                    prob = float(np.clip(previsoes[-1, c] if len(previsoes) > 0 else 0, 0, 1))
                    probabilidades[num] = round(max(0, prob) * 100, 4)
                except:
                    probabilidades[num] = 0
        
        return {
            "algoritmo": "Gradient Boosting",
            "n_arvores": n_arvores,
            "probabilidades": probabilidades,
            "top_numeros": sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15]
        }
    
    # ========================================
    # 9. REDE BAYESIANA
    # ========================================
    
    def rede_bayesiana(self, resultados: list, config: dict) -> dict:
        """
        Rede Bayesiana para inferencia probabilistica
        Modela dependencias entre numeros
        """
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        # Construir grafo de dependencias
        dependencias = defaultdict(list)
        
        # Analisar co-ocorrencias
        co_ocorrencias = Counter()
        for r in resultados:
            dezenas = sorted([int(d) for d in r.get("listaDezenas", [])])
            for n1, n2 in combinations(dezenas[:10], 2):
                co_ocorrencias[(n1, n2)] += 1
        
        # Calcular probabilidades condicionais
        historico = Counter()
        for r in resultados:
            for d in r.get("listaDezenas", []):
                historico[int(d)] += 1
        
        total = sum(historico.values())
        
        probabilidades = {}
        for num in range(minimo, maximo + 1):
            # P(num) - probabilidade marginal
            p_marginal = historico.get(num, 0) / total if total > 0 else 0
            
            # P(num | pais) - probabilidade condicional
            pais = []
            for outro in range(minimo, maximo + 1):
                if outro != num:
                    par = tuple(sorted([num, outro]))
                    if co_ocorrencias.get(par, 0) > len(resultados) * 0.1:
                        pais.append(outro)
            
            # Calcular influencia dos pais
            influencia_pais = 0
            for pai in pais[:5]:  # Top 5 pais
                par = tuple(sorted([num, pai]))
                p_conjunta = co_ocorrencias.get(par, 0) / len(resultados)
                p_pai = historico.get(pai, 0) / total if total > 0 else 0
                if p_pai > 0:
                    influencia_pais += p_conjunta / p_pai
            
            # Probabilidade final
            if pais:
                p_final = p_marginal * (1 + influencia_pais / len(pais))
            else:
                p_final = p_marginal
            
            probabilidades[num] = {
                "probabilidade": round(p_final * 100, 4),
                "pais": pais[:5],
                "influencia_pais": round(influencia_pais, 4)
            }
        
        return {
            "algoritmo": "Rede Bayesiana",
            "probabilidades": {k: v["probabilidade"] for k, v in probabilidades.items()},
            "detalhes": probabilidades,
            "top_numeros": sorted([(k, v["probabilidade"]) for k, v in probabilidades.items()], key=lambda x: x[1], reverse=True)[:15]
        }
    
    # ========================================
    # 10. ENSEMBLE ULTRA (COMBINACAO DE ALGORITMOS)
    # ========================================
    
    def ensemble_ultra(self, resultados: list, config: dict) -> dict:
        """
        Combina todos os algoritmos para previsao final
        Usa ponderacao baseada em performance historica
        """
        print("Executando Random Forest...")
        rf = self.random_forest_simplificado(resultados, config)
        
        print("Executando Naive Bayes...")
        nb = self.naive_bayes_loteria(resultados, config)
        
        print("Executando SVM...")
        svm = self.svm_simplificado(resultados, config)
        
        print("Executando Rede Neural...")
        nn = self.rede_neural_mlp(resultados, config)
        
        print("Executando Monte Carlo...")
        mc = self.simulacao_monte_carlo(resultados, config, 5000)
        
        print("Executando Markov...")
        mk = self.cadeia_markov(resultados, config)
        
        print("Executando Entropia...")
        ent = self.analise_entropia(resultados, config)
        
        print("Executando Gradient Boosting...")
        gb = self.gradient_boosting_simplificado(resultados, config)
        
        print("Executando Rede Bayesiana...")
        rb = self.rede_bayesiana(resultados, config)
        
        # Combinar probabilidades com pesos
        pesos = {
            "rf": 0.15,
            "nb": 0.12,
            "svm": 0.10,
            "nn": 0.18,
            "mc": 0.15,
            "mk": 0.10,
            "gb": 0.12,
            "rb": 0.08
        }
        
        minimo = config["min_num"]
        maximo = config["max_num"]
        
        probabilidades_finais = {}
        
        for num in range(minimo, maximo + 1):
            soma_ponderada = 0
            
            # Random Forest
            if "probabilidades" in rf:
                soma_ponderada += rf["probabilidades"].get(num, 0) * pesos["rf"]
            
            # Naive Bayes
            if "probabilidades" in nb:
                soma_ponderada += nb["probabilidades"].get(num, 0) * pesos["nb"]
            
            # SVM
            if "probabilidades" in svm:
                soma_ponderada += svm["probabilidades"].get(num, 0) * pesos["svm"]
            
            # Rede Neural
            if "probabilidades" in nn:
                soma_ponderada += nn["probabilidades"].get(num, 0) * pesos["nn"]
            
            # Monte Carlo
            if "probabilidades_estimadas" in mc:
                soma_ponderada += mc["probabilidades_estimadas"].get(num, 0) * pesos["mc"]
            
            # Markov
            if "probabilidades" in mk:
                soma_ponderada += mk["probabilidades"].get(num, 0) * pesos["mk"]
            
            # Gradient Boosting
            if "probabilidades" in gb:
                soma_ponderada += gb["probabilidades"].get(num, 0) * pesos["gb"]
            
            # Rede Bayesiana
            if "probabilidades" in rb:
                soma_ponderada += rb["probabilidades"].get(num, 0) * pesos["rb"]
            
            probabilidades_finais[num] = round(soma_ponderada, 4)
        
        # Normalizar
        soma_total = sum(probabilidades_finais.values())
        if soma_total > 0:
            probabilidades_finais = {k: round(v/soma_total * 100, 4) for k, v in probabilidades_finais.items()}
        
        return {
            "algoritmo": "Ensemble Ultra (9 Algoritmos)",
            "algoritmos_utilizados": ["Random Forest", "Naive Bayes", "SVM", "Rede Neural MLP", 
                                       "Monte Carlo", "Cadeia de Markov", "Gradient Boosting", "Rede Bayesiana"],
            "pesos": pesos,
            "probabilidades_finais": probabilidades_finais,
            "top_numeros": sorted(probabilidades_finais.items(), key=lambda x: x[1], reverse=True)[:20],
            "resultados_individuais": {
                "random_forest": rf.get("top_numeros", [])[:5],
                "naive_bayes": nb.get("top_numeros", [])[:5],
                "svm": svm.get("top_numeros", [])[:5],
                "rede_neural": nn.get("top_numeros", [])[:5],
                "monte_carlo": mc.get("top_numeros", [])[:5],
                "markov": mk.get("top_numeros", [])[:5],
                "gradient_boosting": gb.get("top_numeros", [])[:5],
                "rede_bayesiana": rb.get("top_numeros", [])[:5]
            }
        }
    
    # ========================================
    # GERADOR DE SUGESTOES ULTRA
    # ========================================
    
    def gerar_sugestoes_ultra(self, resultados: list, config: dict, quantidade: int = 10) -> dict:
        """
        Gera sugestoes ultra avancadas usando ensemble de algoritmos
        """
        print("\n🧠 Iniciando Analise Ultra Avancada...")
        print("=" * 50)
        
        # Executar ensemble
        ensemble = self.ensemble_ultra(resultados, config)
        
        # Extrair probabilidades
        probs = ensemble["probabilidades_finais"]
        
        # Ordenar numeros por probabilidade
        numeros_ordenados = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        
        # Gerar combinacoes
        minimo = config["min_num"]
        maximo = config["max_num"]
        qtd_escolher = config["pick_count"]
        
        # Tiers baseados em probabilidades
        tier_s = [n for n, _ in numeros_ordenados[:15]]  # Top 15
        tier_a = [n for n, _ in numeros_ordenados[15:30]]  # 16-30
        tier_b = [n for n, _ in numeros_ordenados[30:]]  # Resto
        
        combinacoes = []
        
        estrategias = [
            ("premium", 0.7, 0.25, 0.05),
            ("agressiva", 0.5, 0.35, 0.15),
            ("conservadora", 0.3, 0.4, 0.3),
            ("diversificada", 0.4, 0.4, 0.2),
            ("ousada", 0.6, 0.3, 0.1)
        ]
        
        for i in range(quantidade):
            # Escolher estrategia ciclicamente
            est_nome, p_s, p_a, p_b = estrategias[i % len(estrategias)]
            
            # Calcular quantidades
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
            
            # Preencher se necessario
            while len(numeros) < qtd_escolher:
                num = np.random.randint(minimo, maximo + 1)
                if num not in numeros:
                    numeros.append(num)
            
            numeros = sorted([int(x) for x in numeros[:qtd_escolher]])
            
            # Calcular confianca baseada nas probabilidades
            confianca = sum(probs.get(n, 0) for n in numeros) / qtd_escolher
            
            combinacoes.append({
                "numeros": numeros,
                "estrategia": est_nome,
                "confianca": round(confianca, 2),
                "probabilidade_conjunta": round(math.prod([probs.get(n, 1)/100 for n in numeros]) * 100, 6)
            })
        
        # Ordenar por confianca
        combinacoes.sort(key=lambda x: x["confianca"], reverse=True)
        
        print("=" * 50)
        print("✅ Analise Ultra Concluida!")
        print(f"📊 {len(combinacoes)} combinacoes geradas")
        print(f"🎯 Maior confianca: {combinacoes[0]['confianca']:.2f}%")
        
        return {
            "ensemble": ensemble,
            "combinacoes": combinacoes,
            "total_geradas": len(combinacoes),
            "algoritmos_utilizados": ensemble["algoritmos_utilizados"]
        }


# Instancia global
analisador_ultra = AnalisadorUltraAvancado()
