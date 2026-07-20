"""
Testes do nucleo de analise (offline, sem acesso a API da Caixa).
Execute com:  pytest
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LOTTERIES
from base_analyzer import AnalisadorBase
from analyzer import AnalisadorLoteriasAvancado
from analyzer_ultra import AnalisadorUltraAvancado
from analyzer_global import AnalisadorGlobal


def _fake_resultados(n=120, faixa=60, pick=6, seed=1):
    import random
    rnd = random.Random(seed)
    return [{"listaDezenas": [str(rnd.randint(1, faixa)) for _ in range(pick)]}
            for _ in range(n)]


def test_base_calcula_frequencia():
    a = AnalisadorBase()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    freq = a.calcular_frequencia_absoluta(res, cfg)
    assert "frequencia" in freq
    assert freq["total_sorteios"] == len(res)
    assert len(freq["mais_frequentes"]) <= 15
    # todo numero da faixa deve estar presente
    assert all(cfg["min_num"] <= num <= cfg["max_num"] for num, _ in freq["frequencia"].items())


def test_resumo_estatisticas_chaves():
    a = AnalisadorBase()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    stats = a.obter_resumo_estatisticas(res, cfg)
    for chave in ("frequencia", "probabilidades", "intervalos", "tendencias",
                  "sequencias", "distribuicao", "paridade", "descritivas", "conjunta"):
        assert chave in stats
    # 'conjunta' tem a sub-chave 'pares' usada por /api/combinacoes
    assert "pares" in stats["conjunta"]


def test_sugestao_ia_quantidade_e_faixa():
    a = AnalisadorLoteriasAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    sugs = a.gerar_sugestao_ia(res, cfg, 5)
    assert len(sugs) == 5
    for s in sugs:
        assert len(s["numeros"]) == cfg["pick_count"]
        assert all(cfg["min_num"] <= n <= cfg["max_num"] for n in s["numeros"])
        assert "motivos" in s


def test_confianca_e_motivos():
    a = AnalisadorLoteriasAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados()
    stats = a.obter_resumo_estatisticas(res, cfg)
    base = [3, 7, 12, 23, 41, 58]
    conf = a._calcular_confianca(base, stats["frequencia"], stats["conjunta"]["pares"], stats["intervalos"])
    mot = a._gerar_motivos(base, stats["frequencia"], stats["tendencias"], stats["intervalos"])
    assert 10 <= conf <= 95
    assert isinstance(mot, list) and len(mot) >= 1


def test_subclasses_herdam_base():
    assert issubclass(AnalisadorLoteriasAvancado, AnalisadorBase)
    assert issubclass(AnalisadorUltraAvancado, AnalisadorBase)
    assert issubclass(AnalisadorGlobal, AnalisadorBase)
    # metodos do nucleo disponiveis nas subclasses
    u = AnalisadorUltraAvancado()
    g = AnalisadorGlobal()
    assert hasattr(u, "calcular_frequencia_absoluta")
    assert hasattr(g, "obter_resumo_estatisticas")


def test_reprodutibilidade_com_seed(monkeypatch):
    import random
    import numpy as np
    monkeypatch.setenv("AI_SEED", "42")
    # recarrega config para aplicar o seed
    import importlib
    import config
    importlib.reload(config)
    random.seed(42)
    np.random.seed(42)

    a = AnalisadorLoteriasAvancado()
    cfg = LOTTERIES["megasena"]
    res = _fake_resultados(seed=7)
    s1 = a.gerar_sugestao_ia(res, cfg, 3)
    random.seed(42)
    np.random.seed(42)
    s2 = a.gerar_sugestao_ia(res, cfg, 3)
    assert [x["numeros"] for x in s1] == [x["numeros"] for x in s2]
