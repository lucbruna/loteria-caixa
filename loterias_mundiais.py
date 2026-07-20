"""
Base de Dados Global de Loterias Mundiais
Todas as principais loterias do mundo com configuracoes e tecnicas de analise
"""

# ========================================
# LOTERIAS MUNDIAIS - CONFIGURACOES
# ========================================

LOTERIAS_MUNDIAIS = {
    # ==========================================
    # AMERICAS
    # ==========================================
    
    # EUA
    "powerball": {
        "nome": "Powerball",
        "pais": "EUA",
        "regiao": "Americas",
        "icone": "🇺🇸",
        "min_num": 1,
        "max_num": 69,
        "pick_count": 5,
        "bonus": {"min": 1, "max": 26, "count": 1},
        "cor": "#E31937",
        "frequencia": "3x semana (Seg, Qua, Sex)",
        "custo": 2.00,
        "descricao": "Maior loteria dos EUA, jackpots recordes"
    },
    "mega_millions": {
        "nome": "Mega Millions",
        "pais": "EUA",
        "regiao": "Americas",
        "icone": "🇺🇸",
        "min_num": 1,
        "max_num": 70,
        "pick_count": 5,
        "bonus": {"min": 1, "max": 25, "count": 1},
        "cor": "#FFD700",
        "frequencia": "2x semana (Ter, Sex)",
        "custo": 2.00,
        "descricao": "Jackpots milionarioes multi-estadual"
    },
    "lotto_americano": {
        "nome": "Lotto America",
        "pais": "EUA",
        "regiao": "Americas",
        "icone": "🇺🇸",
        "min_num": 1,
        "max_num": 52,
        "pick_count": 5,
        "bonus": {"min": 1, "max": 10, "count": 1},
        "cor": "#002868",
        "frequencia": "2x semana (Qua, Dom)",
        "custo": 1.00,
        "descricao": "Lotto multi-estadual acessivel"
    },
    
    # CANADA
    "lotto_max": {
        "nome": "Lotto Max",
        "pais": "Canada",
        "regiao": "Americas",
        "icone": "🇨🇦",
        "min_num": 1,
        "max_num": 50,
        "pick_count": 7,
        "cor": "#FF0000",
        "frequencia": "2x semana (Ter, Sex)",
        "custo": 5.00,
        "descricao": "Maior loteria do Canada"
    },
    "lotto_649": {
        "nome": "Lotto 6/49",
        "pais": "Canada",
        "regiao": "Americas",
        "icone": "🇨🇦",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 6,
        "cor": "#FF0000",
        "frequencia": "2x semana (Qua, Dom)",
        "custo": 3.00,
        "descricao": "Classica loteria canadense"
    },
    
    # MEXICO
    "melate": {
        "nome": "Melate",
        "pais": "Mexico",
        "regiao": "Americas",
        "icone": "🇲🇽",
        "min_num": 1,
        "max_num": 39,
        "pick_count": 6,
        "bonus": {"min": 0, "max": 9, "count": 1},
        "cor": "#006847",
        "frequencia": "3x semana",
        "custo": 15.00,
        "descricao": "Principal loteria mexicana"
    },
    
    # ARGENTINA
    "lotto_argentina": {
        "nome": "Loto",
        "pais": "Argentina",
        "regiao": "Americas",
        "icone": "🇦🇷",
        "min_num": 1,
        "max_num": 45,
        "pick_count": 6,
        "cor": "#75AADB",
        "frequencia": "3x semana",
        "custo": 100.00,
        "descricao": "Loteria principal da Argentina"
    },
    
    # COLOMBIA
    "baloto": {
        "nome": "Baloto",
        "pais": "Colombia",
        "regiao": "Americas",
        "icone": "🇨🇴",
        "min_num": 1,
        "max_num": 43,
        "pick_count": 6,
        "bonus": {"min": 1, "max": 16, "count": 1},
        "cor": "#FCD116",
        "frequencia": "2x semana (Qua, Dom)",
        "custo": 3500.00,
        "descricao": "Maior loteria da Colombia"
    },
    
    # ==========================================
    # EUROPA
    # ==========================================
    
    # EUROPEU
    "euromillions": {
        "nome": "EuroMillions",
        "pais": "Europa",
        "regiao": "Europa",
        "icone": "🇪🇺",
        "min_num": 1,
        "max_num": 50,
        "pick_count": 5,
        "bonus": {"min": 1, "max": 12, "count": 2},
        "cor": "#003399",
        "frequencia": "2x semana (Ter, Sex)",
        "custo": 2.50,
        "descricao": "A maior loteria da Europa, jackpots de atras 200M EUR"
    },
    "eurojackpot": {
        "nome": "Eurojackpot",
        "pais": "Europa",
        "regiao": "Europa",
        "icone": "🇪🇺",
        "min_num": 1,
        "max_num": 50,
        "pick_count": 5,
        "bonus": {"min": 1, "max": 12, "count": 2},
        "cor": "#005EB8",
        "frequencia": "2x semana (Ter, Sex)",
        "custo": 2.00,
        "descricao": "Alternativa ao EuroMillions com mais chances"
    },
    
    # UK
    "uk_lotto": {
        "nome": "UK Lotto",
        "pais": "Reino Unido",
        "regiao": "Europa",
        "icone": "🇬🇧",
        "min_num": 1,
        "max_num": 59,
        "pick_count": 6,
        "cor": "#003078",
        "frequencia": "2x semana (Qua, Sab)",
        "custo": 2.00,
        "descricao": "Loteria nacional britanica"
    },
    "thunderball": {
        "nome": "Thunderball",
        "pais": "Reino Unido",
        "regiao": "Europa",
        "icone": "🇬🇧",
        "min_num": 1,
        "max_num": 39,
        "pick_count": 5,
        "bonus": {"min": 1, "max": 14, "count": 1},
        "cor": "#CF0A2C",
        "frequencia": "3x semana (Qua, Sex, Dom)",
        "custo": 1.00,
        "descricao": "Loteria de premios garantidos"
    },
    
    # ESPANHA
    "el_gordo": {
        "nome": "El Gordo de la Primitiva",
        "pais": "Espanha",
        "regiao": "Europa",
        "icone": "🇪🇸",
        "min_num": 1,
        "max_num": 54,
        "pick_count": 5,
        "bonus": {"min": 0, "max": 9, "count": 1},
        "cor": "#AA151B",
        "frequencia": "1x semana (Dom)",
        "custo": 1.00,
        "descricao": "Classica loteria espanhola"
    },
    "bonoloto": {
        "nome": "Bonoloto",
        "pais": "Espanha",
        "regiao": "Europa",
        "icone": "🇪🇸",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 6,
        "cor": "#AA151B",
        "frequencia": "Diaria (Dom-Sex)",
        "custo": 0.50,
        "descricao": "Loteria diaria espanhola"
    },
    "primitiva": {
        "nome": "La Primitiva",
        "pais": "Espanha",
        "regiao": "Europa",
        "icone": "🇪🇸",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 6,
        "bonus": {"min": 0, "max": 9, "count": 1},
        "cor": "#AA151B",
        "frequencia": "2x semana (Qui, Sab)",
        "custo": 1.00,
        "descricao": "A mais antiga loteria da Espanha"
    },
    
    # FRANCA
    "loto_franca": {
        "nome": "Loto",
        "pais": "Franca",
        "regiao": "Europa",
        "icone": "🇫🇷",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 5,
        "bonus": {"min": 1, "max": 10, "count": 1},
        "cor": "#002395",
        "frequencia": "3x semana (Seg, Qua, Sex)",
        "custo": 2.00,
        "descricao": "Loteria nacional francesa"
    },
    
    # ALEMANHA
    "lotto_alemanha": {
        "nome": "Lotto 6 aus 49",
        "pais": "Alemanha",
        "regiao": "Europa",
        "icone": "🇩🇪",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 6,
        "bonus": {"min": 0, "max": 9, "count": 1},
        "cor": "#000000",
        "frequencia": "2x semana (Qua, Sab)",
        "custo": 1.20,
        "descricao": "Classica loteria alema"
    },
    
    # ITALIA
    "superenalotto": {
        "nome": "SuperEnalotto",
        "pais": "Italia",
        "regiao": "Europa",
        "icone": "🇮🇹",
        "min_num": 1,
        "max_num": 90,
        "pick_count": 6,
        "bonus": {"min": 1, "max": 90, "count": 1},
        "cor": "#008C45",
        "frequencia": "3x semana (Ter, Qui, Sab)",
        "custo": 1.00,
        "descricao": "Maior loteria da Italia, jackpots enormes"
    },
    
    # POLONIA
    "lotto_polonia": {
        "nome": "Lotto",
        "pais": "Polonia",
        "regiao": "Europa",
        "icone": "🇵🇱",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 6,
        "cor": "#DC143C",
        "frequencia": "3x semana (Qua, Qui, Sab)",
        "custo": 3.00,
        "descricao": "Loteria nacional polonesa"
    },
    
    # RUSSIA
    "gosloto_7_49": {
        "nome": "Gosloto 7/49",
        "pais": "Russia",
        "regiao": "Europa",
        "icone": "🇷🇺",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 7,
        "cor": "#0039A6",
        "frequencia": "Diaria",
        "custo": 100.00,
        "descricao": "Loteria estatal russa"
    },
    
    # ==========================================
    # ASIA
    # ==========================================
    
    # CHINA
    "ssq_china": {
        "nome": "Shuang Se Qiu",
        "pais": "China",
        "regiao": "Asia",
        "icone": "🇨🇳",
        "min_num": 1,
        "max_num": 33,
        "pick_count": 6,
        "bonus": {"min": 1, "max": 16, "count": 1},
        "cor": "#DE2910",
        "frequencia": "3x semana (Ter, Qui, Dom)",
        "custo": 2.00,
        "descricao": "Principal loteria chinesa"
    },
    "dlt_china": {
        "nome": "Da Le Tou",
        "pais": "China",
        "regiao": "Asia",
        "icone": "🇨🇳",
        "min_num": 1,
        "max_num": 35,
        "pick_count": 5,
        "bonus": {"min": 1, "max": 12, "count": 2},
        "cor": "#DE2910",
        "frequencia": "2x semana (Seg, Qua)",
        "custo": 2.00,
        "descricao": "Loteria de grande premio da China"
    },
    
    # JAPAO
    "loto6_japao": {
        "nome": "Loto 6",
        "pais": "Japao",
        "regiao": "Asia",
        "icone": "🇯🇵",
        "min_num": 1,
        "max_num": 43,
        "pick_count": 6,
        "bonus": {"min": 1, "max": 43, "count": 1},
        "cor": "#BC002D",
        "frequencia": "2x semana (Qua, Dom)",
        "custo": 200.00,
        "descricao": "Loteria popular japonesa"
    },
    
    # COREIA DO SUL
    "lotto_coreia": {
        "nome": "Lotto 6/45",
        "pais": "Coreia do Sul",
        "regiao": "Asia",
        "icone": "🇰🇷",
        "min_num": 1,
        "max_num": 45,
        "pick_count": 6,
        "cor": "#003478",
        "frequencia": "2x semana (Qua, Sab)",
        "custo": 1000.00,
        "descricao": "Loteria nacional coreana"
    },
    
    # FILIPINAS
    "lotto_filipinas": {
        "nome": "PCSO Lotto 6/42",
        "pais": "Filipinas",
        "regiao": "Asia",
        "icone": "🇵🇭",
        "min_num": 1,
        "max_num": 42,
        "pick_count": 6,
        "cor": "#0038A8",
        "frequencia": "3x semana",
        "custo": 20.00,
        "descricao": "Loteria das Filipinas"
    },
    
    # INDIA
    "lotto_india": {
        "nome": "State Lotteries",
        "pais": "India",
        "regiao": "Asia",
        "icone": "🇮🇳",
        "min_num": 1,
        "max_num": 50,
        "pick_count": 6,
        "cor": "#FF9933",
        "frequencia": "Diaria",
        "custo": 50.00,
        "descricao": "Sistema de loterias estaduais da India"
    },
    
    # SINGAPURA
    "toto_singapura": {
        "nome": "Toto",
        "pais": "Singapura",
        "regiao": "Asia",
        "icone": "🇸🇬",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 6,
        "bonus": {"min": 1, "max": 49, "count": 1},
        "cor": "#EF3340",
        "frequencia": "2x semana (Qua, Dom)",
        "custo": 1.00,
        "descricao": "Loteria de Singapura"
    },
    
    # ==========================================
    # OCEANIA
    # ==========================================
    
    # AUSTRALIA
    "oz_lotto": {
        "nome": "Oz Lotto",
        "pais": "Australia",
        "regiao": "Oceania",
        "icone": "🇦🇺",
        "min_num": 1,
        "max_num": 45,
        "pick_count": 7,
        "cor": "#00008B",
        "frequencia": "1x semana (Ter)",
        "custo": 1.30,
        "descricao": "Loteria nacional australiana"
    },
    "powerball_australia": {
        "nome": "Powerball Australia",
        "pais": "Australia",
        "regiao": "Oceania",
        "icone": "🇦🇺",
        "min_num": 1,
        "max_num": 35,
        "pick_count": 7,
        "bonus": {"min": 1, "max": 20, "count": 1},
        "cor": "#00008B",
        "frequencia": "1x semana (Qui)",
        "custo": 2.15,
        "descricao": "Maior loteria da Australia"
    },
    "lottoland_australia": {
        "nome": "Saturday Lotto",
        "pais": "Australia",
        "regiao": "Oceania",
        "icone": "🇦🇺",
        "min_num": 1,
        "max_num": 45,
        "pick_count": 6,
        "bonus": {"min": 1, "max": 45, "count": 2},
        "cor": "#00008B",
        "frequencia": "1x semana (Sab)",
        "custo": 0.65,
        "descricao": "Loteria classica australiana"
    },
    
    # NOVA ZELANDIA
    "lotto_nz": {
        "nome": "Lotto NZ",
        "pais": "Nova Zelandia",
        "regiao": "Oceania",
        "icone": "🇳🇿",
        "min_num": 1,
        "max_num": 40,
        "pick_count": 6,
        "bonus": {"min": 1, "max": 10, "count": 1},
        "cor": "#000000",
        "frequencia": "2x semana (Qua, Sab)",
        "custo": 0.70,
        "descricao": "Loteria nacional neozelandesa"
    },
    
    # ==========================================
    # AFRICA
    # ==========================================
    
    "lotto_sul_africa": {
        "nome": "LOTTO",
        "pais": "Africa do Sul",
        "regiao": "Africa",
        "icone": "🇿🇦",
        "min_num": 1,
        "max_num": 52,
        "pick_count": 6,
        "bonus": {"min": 1, "max": 52, "count": 1},
        "cor": "#007749",
        "frequencia": "2x semana (Qua, Sab)",
        "custo": 5.00,
        "descricao": "Loteria nacional sul-africana"
    },
    "powerball_sul_africa": {
        "nome": "PowerBall",
        "pais": "Africa do Sul",
        "regiao": "Africa",
        "icone": "🇿🇦",
        "min_num": 1,
        "max_num": 50,
        "pick_count": 5,
        "bonus": {"min": 1, "max": 20, "count": 1},
        "cor": "#007749",
        "frequencia": "2x王朝 (Ter, Qui)",
        "custo": 5.00,
        "descricao": "PowerBall sul-africano"
    },
    
    # NIGERIA
    "lotto_nigeria": {
        "nome": "Premier Lotto",
        "pais": "Nigeria",
        "regiao": "Africa",
        "icone": "🇳🇬",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 5,
        "cor": "#008751",
        "frequencia": "Diaria",
        "custo": 100.00,
        "descricao": "Loteria popular nigeriana"
    },
    
    # KENIA
    "lotto_kenia": {
        "nome": "Kenya Lotto",
        "pais": "Kenia",
        "regiao": "Africa",
        "icone": "🇰🇪",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 6,
        "cor": "#006600",
        "frequencia": "2x semana",
        "custo": 50.00,
        "descricao": "Loteria kenyana"
    },
    
    # ==========================================
    # LOTERIAS VIRTUAIS/ONLINE
    # ==========================================
    
    "loterias_virtuais": {
        "nome": "Loterias Online",
        "pais": "Global",
        "regiao": "Global",
        "icone": "🌐",
        "min_num": 1,
        "max_num": 49,
        "pick_count": 6,
        "cor": "#9B59B6",
        "frequencia": "Variavel",
        "custo": 1.00,
        "descricao": "Plataformas online como Lottoland, TheLotter, etc."
    }
}

# ==========================================
# TECNICAS DE ANALISE GLOBAIS
# ==========================================

TECNICAS_ANALISE_MUNDIAL = {
    "europa": {
        "nome": "Escola Europeia de Analise",
        "tecnicas": [
            "Analise de Ciclos Longos (100+ sorteios)",
            "Teoria dos Numeros Quentes/Frios (Hot/Cold)",
            "Analise de Pares e Trios Frequentes",
            "Distribuicao por Faixas (Quartis)",
            "Analise de Tendencia com Media Movel",
            "Padroes de Consecutivos",
            "Analise de Intervalos (Gaps)",
            "Teste Chi-Quadrado de Uniformidade",
            "Distribuicao Binomial",
            "Analise de Autocorrelacao"
        ],
        "algoritmos": [
            "ARIMA (AutoRegressive Integrated Moving Average)",
            "Exponential Smoothing",
            "K-Nearest Neighbors (KNN)",
            "Support Vector Machines (SVM)",
            "Random Forest",
            "Gradient Boosting (XGBoost)"
        ]
    },
    "america": {
        "nome": "Escola Americana de Analise",
        "tecnicas": [
            "Frequencia Relativa e Absoluta",
            "Analise de Combinacoes Vencedoras",
            "Estatistica Descritiva Completa",
            "Distribuicao de Poisson",
            "Teoria da Probabilidade Condicional",
            "Simulacao Monte Carlo",
            "Analise de Regressao",
            "Redes Neurais (Deep Learning)",
            "Algoritmos Geneticos",
            "Otimizacao por Enxame de Particulas"
        ],
        "algoritmos": [
            "Long Short-Term Memory (LSTM)",
            "Convolutional Neural Networks (CNN)",
            "Reinforcement Learning",
            "Bayesian Networks",
            "Hidden Markov Models",
            "Ensemble Methods"
        ]
    },
    "asia": {
        "nome": "Escola Asiatica de Analise",
        "tecnicas": [
            "Analise de Feng Shui Numerico",
            "Teoria dos Numeros da Sorte",
            "Analise de Padroes Culturais",
            "Sequencias Fibonacci",
            "Numeros Primos e Divisibilidade",
            "Analise de Soma e Produto",
            "Padroes Espelhados",
            "Analise de Simetria",
            "Cadeias de Markov de Alta Ordem",
            "Processos Estocasticos"
        ],
        "algoritmos": [
            "Machine Learning Avancado",
            "Deep Belief Networks",
            "Generative Adversarial Networks (GAN)",
            "Autoencoders",
            "Transformer Models",
            "Attention Mechanisms"
        ]
    }
}

# ==========================================
# ESTRATEGIAS GLOBAIS COMPROVADAS
# ==========================================

ESTRATEGIAS_GLOBAIS = {
    "frequencia_balanceada": {
        "nome": "Frequencia Balanceada",
        "descricao": "Combina numeros quentes (frequentemente sorteados) com frios (atrasados)",
        "composicao": {"quentes": 0.4, "frios": 0.3, "medios": 0.3},
        "eficacia": "Alta",
        "origem": "Europa"
    },
    "distribuicao_faixas": {
        "nome": "Distribuicao por Faixas",
        "descricao": "Distribui numeros uniformemente entre baixos, medios e altos",
        "composicao": {"baixos": 0.33, "medios": 0.34, "altos": 0.33},
        "eficacia": "Alta",
        "origem": "Americas"
    },
    "par_impar": {
        "nome": "Balanceamento Par/Impar",
        "descricao": "Mantem equilibrio entre numeros pares e impares",
        "composicao": {"pares": 0.5, "impares": 0.5},
        "eficacia": "Media",
        "origem": "Global"
    },
    "soma_otima": {
        "nome": "Soma Otimizada",
        "descricao": "Seleciona numeros cuja soma esta dentro do desvio padrao historico",
        "composicao": {"faixa_soma": "media +/- 1.5 dp"},
        "eficacia": "Alta",
        "origem": "Europa"
    },
    "intervalos_atrasados": {
        "nome": "Numeros Atrasados",
        "descricao": "Foca em numeros que estao ha tempo acima da media sem aparecer",
        "composicao": {"atrasados": 0.6, "quentes": 0.4},
        "eficacia": "Media-Alta",
        "origem": "Americas"
    },
    "padroes_sequenciais": {
        "nome": "Padroes Sequenciais",
        "descricao": "Analisa padroes de consecutivos e sequencias",
        "composicao": {"consecutivos": 0.2, "saltos": 0.8},
        "eficacia": "Media",
        "origem": "Asia"
    },
    "ensemble_ml": {
        "nome": "Ensemble Machine Learning",
        "descricao": "Combina multiplos algoritmos de ML para previsao",
        "composicao": {"rf": 0.2, "nn": 0.25, "svm": 0.15, "gb": 0.2, "bayes": 0.2},
        "eficacia": "Muito Alta",
        "origem": "Global"
    },
    "monte_carlo_avancado": {
        "nome": "Monte Carlo Avancado",
        "descricao": "Simulacao estocastica com 100k+ iteracoes",
        "composicao": {"simulacoes": 100000},
        "eficacia": "Alta",
        "origem": "Americas"
    },
    "deep_learning": {
        "nome": "Deep Learning (LSTM/CNN)",
        "descricao": "Redes neurais profundas para series temporais",
        "composicao": {"camadas": 5, "neuronios": 128},
        "eficacia": "Muito Alta",
        "origem": "Global"
    },
    "analise_ciclica": {
        "nome": "Analise Ciclica Fourier",
        "descricao": "Detecta ciclos periodicos nos dados usando Transformada de Fourier",
        "composicao": {"janela": 50, "frequencias": 10},
        "eficacia": "Media-Alta",
        "origem": "Europa"
    }
}

# ==========================================
# ESTATISTICAS GLOBAIS DE ACERTIVIDADE
# ==========================================

ACERTIVIDADE_GLOBAL = {
    "powerball": {
        "jackpot_odds": "1 em 292,201,338",
        "qualquer_premio": "1 em 24.9",
        "media_sorteios_mes": 12,
        "jackpot medio": "$100M+ USD",
        "recorde": "$2.04B USD (2022)"
    },
    "mega_millions": {
        "jackpot_odds": "1 em 302,575,350",
        "qualquer_premio": "1 em 24",
        "media_sorteios_mes": 8,
        "jackpot medio": "$80M+ USD",
        "recorde": "$1.537B USD (2018)"
    },
    "euromillions": {
        "jackpot_odds": "1 em 139,838,160",
        "qualquer_premio": "1 em 13",
        "media_sorteios_mes": 8,
        "jackpot medio": "€50M+ EUR",
        "recorde": "€230M EUR (2023)"
    },
    "megasena": {
        "jackpot_odds": "1 em 50,063,860",
        "qualquer_premio": "1 em 3,132",
        "media_sorteios_mes": 12,
        "jackpot medio": "R$30M+ BRL",
        "recorde": "R$525M BRL (2023)"
    }
}


def obter_todas_loterias():
    """Retorna todas as loterias mundiais"""
    return LOTERIAS_MUNDIAIS


def obter_loterias_por_regiao(regiao: str):
    """Retorna loterias de uma regiao especifica"""
    return {k: v for k, v in LOTERIAS_MUNDIAIS.items() if v.get("regiao") == regiao}


def obter_tecnicas_por_regiao(regiao: str):
    """Retorna tecnicas de analise de uma regiao"""
    return TECNICAS_ANALISE_MUNDIAL.get(regiao, {})


def obter_estrategias_globais():
    """Retorna todas as estrategias globais"""
    return ESTRATEGIAS_GLOBAIS


def obter_estatisticas_acertividade():
    """Retorna estatisticas de acertividade global"""
    return ACERTIVIDADE_GLOBAL


def comparar_loterias(loteria1: str, loteria2: str):
    """Compara duas loterias"""
    l1 = LOTERIAS_MUNDIAIS.get(loteria1)
    l2 = LOTERIAS_MUNDIAIS.get(loteria2)
    
    if not l1 or not l2:
        return None
    
    return {
        "loteria1": l1,
        "loteria2": l2,
        "dificuldade": {
            "loteria1": l1["max_num"] ** l1["pick_count"],
            "loteria2": l2["max_num"] ** l2["pick_count"]
        },
        "custo_por_jogo": {
            "loteria1": l1["custo"],
            "loteria2": l2["custo"]
        }
    }
