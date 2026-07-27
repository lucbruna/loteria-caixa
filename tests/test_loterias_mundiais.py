import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loterias_mundiais import LOTERIAS_MUNDIAIS, comparar_loterias, obter_loterias_por_regiao, obter_tecnicas_por_regiao


def test_loterias_mundiais_contem_dados():
    assert len(LOTERIAS_MUNDIAIS) >= 30


def test_loteria_tem_campos_obrigatorios():
    for chave, loteria in LOTERIAS_MUNDIAIS.items():
        assert "nome" in loteria
        assert "min_num" in loteria
        assert "max_num" in loteria
        assert "pick_count" in loteria


def test_loterias_por_regiao():
    americas = obter_loterias_por_regiao("Americas")
    europa = obter_loterias_por_regiao("Europa")
    assert len(americas) >= 5
    assert len(europa) >= 10


def test_tecnicas_por_regiao():
    tecnicas = obter_tecnicas_por_regiao("asia")
    assert tecnicas is not None
    assert "tecnicas" in tecnicas


def test_comparar_loterias_usa_math_comb():
    result = comparar_loterias("powerball", "euromillions")
    assert result is not None
    d1 = result["dificuldade"]["loteria1"]
    d2 = result["dificuldade"]["loteria2"]
    # powerball: C(69,5) = 11,238,513; NOT 69^5 = 1,564,031,349
    assert d1 < 20_000_000
    # euromillions: C(50,5) = 2,118,760
    assert d2 == 2_118_760
