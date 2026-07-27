import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LOTTERIES
from funcionalidades_avancadas import FuncionalidadesAvancadas as FA


def _fake_resultados(n=150, seed=3):
    import random
    rnd = random.Random(seed)
    return [{"listaDezenas": [str(rnd.randint(1, 60)) for _ in range(6)]}
            for _ in range(n)]


def test_teste_chi_quadrado():
    res = _fake_resultados()
    freq = {}
    for r in res:
        for d in r["listaDezenas"]:
            freq[int(d)] = freq.get(int(d), 0) + 1
    expected = {n: len(res) * 6 / 60 for n in range(1, 61)}
    result = FA.teste_chi_quadrado(freq, expected)
    assert "chi2" in result
    assert "p_valor" in result


def test_teste_ks():
    dados1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    dados2 = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    result = FA.teste_ks(dados1, dados2)
    assert "estatistica_D" in result
    assert result["estatistica_D"] > 0.5  # distribuições muito diferentes


def test_teste_ks_distribuicoes_similares():
    dados1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    dados2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = FA.teste_ks(dados1, dados2)
    assert result["estatistica_D"] == 0.0


def test_kelly_criterion():
    result = FA.kelly_criterion(5.0, 5_000_000, 0.00000002)
    assert "kelly_fraction" in result
    assert "recomendacao" in result


def test_kelly_criterion_invalido():
    result = FA.kelly_criterion(5.0, 5_000_000, 0)
    assert "erro" in result


def test_importar_csv():
    cfg = LOTTERIES["megasena"]
    csv_content = "1,2,3,4,5,6\n7,8,9,10,11,12\n"
    result = FA.importar_csv(csv_content, cfg)
    assert result["resultados_importados"] == 2
