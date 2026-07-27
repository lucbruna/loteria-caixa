import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tecnologias_globais import TecnologiasGlobais


def test_calcular_probabilidade_combinatoria():
    tech = TecnologiasGlobais()
    prob = tech.calcular_probabilidade_combinatoria(60, 6, 6, 6)
    assert 0 < prob < 1


def test_calcular_odds_jackpot():
    tech = TecnologiasGlobais()
    odds = tech.calcular_odds_jackpot(60, 6)
    assert isinstance(odds, dict)
    assert "odds" in odds
    assert "total_combinacoes" in odds


def test_estrategias_retornam_dict():
    tech = TecnologiasGlobais()
    assert isinstance(tech.estrategia_syndicate_profissional(), dict)
    assert isinstance(tech.estrategia_delta_system(), dict)
    assert isinstance(tech.estrategia_ottosen(), dict)
    assert isinstance(tech.estrategia_gail_howard(), dict)
    assert isinstance(tech.estrategia_lottery_expert(), dict)


def test_algoritmo_balanceamento():
    tech = TecnologiasGlobais()
    nums = [1, 7, 15, 30, 45, 58]
    from config import LOTTERIES
    result = tech.algoritmo_balanceamento(nums, LOTTERIES["megasena"])
    assert "soma" in result
    assert "paridade" in result
    assert "distribuicao_faixas" in result
