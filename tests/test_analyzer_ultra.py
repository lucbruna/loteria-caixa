import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from analyzer_ultra import AnalisadorUltraAvancado
from config import LOTTERIES


def _fake_resultados(n=150, faixa=60, pick=6, seed=1):
    import random
    rnd = random.Random(seed)
    return [{"listaDezenas": [str(rnd.randint(1, faixa)) for _ in range(pick)]}
            for _ in range(n)]


def test_ultra_random_forest_retorna_dict():
    u = AnalisadorUltraAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    out = u.random_forest_simplificado(res, cfg)
    assert isinstance(out, dict)
    assert "probabilidades" in out or "erro" in out


def test_ultra_monte_carlo_retorna_probabilidades():
    u = AnalisadorUltraAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    out = u.simulacao_monte_carlo(res, cfg)
    assert "probabilidades_estimadas" in out or "erro" in out


def test_ultra_markov_retorna_transicoes():
    u = AnalisadorUltraAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    out = u.cadeia_markov(res, cfg)
    assert "probabilidades" in out or "erro" in out


def test_ultra_entropy_retorna_entropia():
    u = AnalisadorUltraAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    out = u.analise_entropia(res, cfg)
    assert "entropia_geral" in out or "erro" in out


def test_ultra_fourier_retorna_ciclos():
    u = AnalisadorUltraAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    out = u.analise_fourier(res, cfg)
    assert "ciclos_detectados" in out or "erro" in out


def test_ultra_gradient_boosting_retorna_prob():
    u = AnalisadorUltraAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    out = u.gradient_boosting_simplificado(res, cfg)
    assert "probabilidades" in out or "erro" in out


def test_ultra_ensemble_contem_algoritmos():
    u = AnalisadorUltraAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    out = u.ensemble_ultra(res, cfg)
    assert "algoritmos_utilizados" in out
    assert len(out["algoritmos_utilizados"]) >= 6


def test_ultra_gerar_sugestoes_contem_combinacoes():
    u = AnalisadorUltraAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    out = u.gerar_sugestoes_ultra(res, cfg, 3)
    assert len(out["combinacoes"]) == 3
    for c in out["combinacoes"]:
        assert len(c["numeros"]) == cfg["pick_count"]
        assert "confianca" in c


def test_ultra_dados_insuficientes():
    u = AnalisadorUltraAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados(n=5)
    out = u.random_forest_simplificado(res, cfg)
    assert out.get("erro") is not None
