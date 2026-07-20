"""
Testes de regressao para funcionalidades_avancadas.
Garante que o uso do nucleo base (base_analyzer) preserva o comportamento
original da frequencia inline. Offline (sem rede).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from collections import Counter
from config import LOTTERIES
from funcionalidades_avancadas import FuncionalidadesAvancadas as FA


def _fake_resultados(n=150, seed=3):
    import random
    rnd = random.Random(seed)
    return [{"listaDezenas": [str(rnd.randint(1, 60)) for _ in range(6)]}
            for _ in range(n)]


def test_ensemble_freq_usa_nucleo_base():
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    nums = [3, 7, 12, 23, 41, 58]

    out = FA.ensemble_scorer_avancado(nums, res, cfg)

    # Replica o calculo inline original para comparar
    historico = Counter()
    for r in res:
        for d in r["listaDezenas"]:
            historico[int(d)] += 1
    total = sum(historico.values())
    esperado = round(float(np.mean(
        [historico.get(n, 0) / total if total > 0 else 0 for n in nums]) * 100), 2)

    assert abs(out["scores"]["frequencia"] - esperado) < 1e-9
    assert 1 <= out["score_final"] <= 99


def test_gerar_jogos_inteligentes():
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    jogos = FA.gerar_jogos_inteligentes(res, cfg, 5)
    assert len(jogos) == 5
    for j in jogos:
        assert len(j["numeros"]) == cfg["pick_count"]
        assert all(cfg["min_num"] <= n <= cfg["max_num"] for n in j["numeros"])


def test_backtest_auto_tune_wheeling():
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    bt = FA.backtest_walk_forward(res, cfg, 50)
    assert "vantagem_percentual" in bt
    at = FA.auto_tune(res, cfg)
    assert at["melhor_config"] is not None
    wh = FA.wheeling_otimizado(list(range(1, 21)), 5, cfg)
    assert wh["qtd_jogos"] == 5
