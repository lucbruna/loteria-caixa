"""
Configurações do Sistema de Loterias
"""
import os
import sys

# Diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quando congelado (PyInstaller), os arquivos de leitura (static, etc.) ficam
# em sys._MEIPASS, e os dados graváveis devem ir para um local do usuario
# (APPDATA), pois a pasta de instalacao (ex.: Arquivos de Programas) pode ser
# somente-leitura.
if getattr(sys, "frozen", False):
    _APP_HOME = os.environ.get("APPDATA") or os.path.expanduser("~")
    _DATA_ROOT = os.path.join(_APP_HOME, "LoteriaFederal")
else:
    _DATA_ROOT = BASE_DIR

DATA_DIR = os.path.join(_DATA_ROOT, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
RESULTS_DIR = os.path.join(DATA_DIR, "results")

# Criar diretórios
for d in [DATA_DIR, CACHE_DIR, RESULTS_DIR]:
    os.makedirs(d, exist_ok=True)

# API Caixa Econômica Federal
API_BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api"

# Configurações das Loterias
LOTTERIES = {
    "megasena": {
        "name": "Mega-Sena",
        "api_name": "megasena",
        "min_num": 1,
        "max_num": 60,
        "pick_count": 6,
        "draws_per_week": 3,  # Ter, Qui, Sáb
        "cost_per_bet": 5.00,
        "color": "#00A859",
        "icon": "🎰"
    },
    "lotofacil": {
        "name": "Lotofácil",
        "api_name": "lotofacil",
        "min_num": 1,
        "max_num": 25,
        "pick_count": 15,
        "draws_per_week": 6,  # Seg a Sex + Sáb
        "cost_per_bet": 2.50,
        "color": "#9B59B6",
        "icon": "🎯"
    },
    "lotomania": {
        "name": "Lotomania",
        "api_name": "lotomania",
        "min_num": 0,
        "max_num": 99,
        "pick_count": 20,
        "draws_per_week": 3,  # Ter, Qui, Sáb
        "cost_per_bet": 2.50,
        "color": "#E74C3C",
        "icon": "🍀"
    },
    "quina": {
        "name": "Quina",
        "api_name": "quina",
        "min_num": 1,
        "max_num": 80,
        "pick_count": 5,
        "draws_per_week": 5,  # Seg a Sex
        "cost_per_bet": 2.00,
        "color": "#3498DB",
        "icon": "⭐"
    },
    "loteca": {
        "name": "Loteca",
        "api_name": "loteca",
        "min_num": 1,
        "max_num": 14,
        "pick_count": 14,
        "draws_per_week": 2,
        "cost_per_bet": 1.50,
        "color": "#F39C12",
        "icon": "⚽"
    },
    "timemania": {
        "name": "Timemania",
        "api_name": "timemania",
        "min_num": 1,
        "max_num": 80,
        "pick_count": 10,
        "draws_per_week": 3,
        "cost_per_bet": 2.00,
        "color": "#1ABC9C",
        "icon": "🎮"
    },
    "diadesorte": {
        "name": "Dia de Sorte",
        "api_name": "diadesorte",
        "min_num": 1,
        "max_num": 31,
        "pick_count": 7,
        "draws_per_week": 6,
        "cost_per_bet": 2.00,
        "color": "#E67E22",
        "icon": "📅"
    }
}

# Cache timeout (em segundos)
CACHE_TIMEOUT = 3600  # 1 hora

# Configurações da IA
AI_CONFIG = {
    "analysis_depth": 50,  # Últimos N concursos para análise
    "frequency_weight": 0.3,
    "recency_weight": 0.3,
    "pattern_weight": 0.2,
    "pair_weight": 0.2
}

# Flask config (sobrescreva via variaveis de ambiente: FLASK_HOST, FLASK_PORT, FLASK_DEBUG)
FLASK_HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").strip().lower() in ("1", "true", "yes", "on")

# Reprodutibilidade das sugestoes (opcional).
# Defina AI_SEED para obter sempre os mesmos jogos gerados.
# Vazio (padrao) = aleatorio a cada execucao.
_AI_SEED_RAW = os.environ.get("AI_SEED", "").strip()
AI_SEED = int(_AI_SEED_RAW) if _AI_SEED_RAW else None

if AI_SEED is not None:
    import random
    import numpy as np
    random.seed(AI_SEED)
    np.random.seed(AI_SEED)


# Garante saida UTF-8 mesmo em consoles Windows (cp1252), evitando que
# prints com emojis quebrem a aplicacao (ex.: /api/ultra e o menu).
import sys
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
