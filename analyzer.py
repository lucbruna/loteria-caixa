"""
Motor de Analise e IA Avancada para Loterias
Compatibilidade: mantem ``AnalisadorLoteriasAvancado`` como a implementacao
principal, agora herdando todo o nucleo estatistico de ``AnalisadorBase``
(base_analyzer.py).
"""
from base_analyzer import AnalisadorBase


class AnalisadorLoteriasAvancado(AnalisadorBase):
    """Analisador principal (estatistica + sugestoes multi-criterio).

    Todo o nucleo de calculo esta em ``AnalisadorBase``; esta classe existe
    para preservar a API publica e permitir especializacoes futuras.
    """
    pass


# Instancia global
analisador = AnalisadorLoteriasAvancado()
