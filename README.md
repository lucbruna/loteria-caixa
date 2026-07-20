# 🎰 Loteria Federal - Sistema Completo de Análise

Sistema completo de análise de loterias brasileiras com inteligência artificial, conectado à API oficial da Caixa Econômica Federal.

## 🚀 Funcionalidades

- **Dados Oficiais**: Conectado à API da Caixa Econômica Federal
- **Todas as Loterias**: Mega-Sena, Lotofácil, Lotomania, Quina, Loteca, Timemania, Dia de Sorte
- **Análise IA**: Algoritmos estatísticos avançados para sugestão de números
- **Dashboard Visual**: Interface web completa e responsiva
- **Estatísticas Detalhadas**: Frequência, pares, tendências, intervalos
- **Calculadora de Apostas**: Custos e combinações

## 📋 Pré-requisitos

- Python 3.8+
- pip

## 🛠️ Instalação

```bash
# Navegue até o diretório do projeto
cd "E:\LOTERIA FEDERAL"

# Instale as dependências
pip install -r requirements.txt
```

## 🎯 Uso

### Modo Terminal (Menu Interativo)

```bash
python main.py
```

### Modo Dashboard (Web)

```bash
python app.py
```

Acesse: http://localhost:5000

## 📊 Estrutura do Projeto

```
LOTERIA FEDERAL/
├── app.py              # Servidor Flask (Backend API)
├── main.py             # Menu principal interativo
├── config.py           # Configurações do sistema
├── api_client.py       # Cliente da API da Caixa
├── analyzer.py         # Motor de análise e IA
├── requirements.txt    # Dependências Python
├── static/
│   └── index.html      # Dashboard web completo
└── data/
    ├── cache/          # Cache dos dados da API
    └── results/        # Relatórios gerados
```

## 🔧 API Endpoints

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/todos-ultimos` | Últimos resultados de todas as loterias |
| `GET /api/ultimo/<lottery>` | Último resultado de uma loteria |
| `GET /api/historico/<lottery>/<count>` | Histórico de resultados (até 200) |
| `GET /api/analise/<lottery>` | Análise completa com IA (estatísticas + sugestões) |
| `GET /api/sugerir/<lottery>/<count>` | Sugestões de números (até 100) |
| `GET /api/combinacoes/<lottery>/<quantidade>` | Geração de combinações em massa (até 20000) |
| `GET /api/estatisticas/<lottery>` | Estatísticas detalhadas |
| `GET /api/calculadora-apostas` | Calculadora de custos e combinações |
| `GET /api/detalhes/<lottery>` | Detalhes (último sorteio + análise + sugestões) |
| `GET /api/ultra/<lottery>/<quantidade>` | Análise Ultra (ensemble de 9 algoritmos) |
| `GET /api/global/<lottery>/<quantidade>` | Análise Global (técnicas mundiais) |
| `GET /api/tecnologias_avancadas/<lottery>` | LSTM, Q-Learning, Fuzzy, Chaos, Wavelet, etc. |
| `GET /api/backtest/<lottery>/<janelas>` | Backtest walk-forward da IA |
| `GET /api/kelly` | Kelly Criterion (`?custo&premio&probabilidade`) |
| `GET /api/wheeling/<lottery>/<qtd_jogos>` | Fechamento/wheeling otimizado |
| `GET /api/auto_tune/<lottery>` | Auto-tune de hiperparâmetros |
| `GET /api/gerar_jogos/<lottery>/<quantidade>` | Jogos inteligentes (todas as técnicas) |
| `GET /api/ensemble/<lottery>` | Ensemble combinando Ultra + Global + Inteligente |
| `GET /api/loterias_mundiais` | Loterias e técnicas mundiais |
| `GET /api/tecnologias` | Fórmulas e estratégias comprovadas |
| `GET /api/calcular_odds/<p>/<w>/<m>` | Odds para qualquer configuração |
| `POST /api/importar_csv` | Importa histórico de CSV (`{conteudo, loteria}`) |

> **Configuração (variáveis de ambiente):** `FLASK_HOST` (padrão `127.0.0.1`),
> `FLASK_PORT` (padrão `5000`) e `FLASK_DEBUG` (padrão `False`).
> Em produção, **nunca** deixe `FLASK_DEBUG=True` exposto em rede.
> Defina `AI_SEED` (ex.: `AI_SEED=42`) para tornar as sugestões reprodutíveis.

## 🧱 Arquitetura

O núcleo estatístico (frequência, probabilidades, intervalos, tendências,
sequências, distribuição, paridade e geração de sugestões) vive em
`base_analyzer.py` (`AnalisadorBase`). Os analyzers especializados herdam dele:

- `analyzer.py` → `AnalisadorLoteriasAvancado` (IA multi-critério)
- `analyzer_ultra.py` → `AnalisadorUltraAvancado` (ensemble de 9 algoritmos)
- `analyzer_global.py` → `AnalisadorGlobal` (técnicas mundiais)

Isso elimina duplicação e mantém uma única fonte de verdade para os cálculos.

## 🧪 Testes

```bash
pip install -r requirements-dev.txt
pytest
```

## 🤖 Análise IA

O sistema utiliza múltiplos algoritmos:

1. **Análise de Frequência**: Números mais e menos sorteados
2. **Análise de Pares**: Combinações que aparecem juntas
3. **Análise de Intervalos**: Tempo entre aparições
4. **Análise de Tendências**: Números em alta ou baixa
5. **Análise de Padrões**: Consecutivos, soma, distribuição

## ⚠️ Aviso Importante

Este sistema é **apenas para fins educacionais e de entretenimento**. Loterias são jogos de azar e não existe fórmula mágica para ganhar. Jogue com responsabilidade.

## 📈 Loterias Suportadas

| Loteria | Nº de Dezenas | Faixa | Custo/Aposta |
|---------|---------------|-------|--------------|
| Mega-Sena | 6 | 1-60 | R$ 5,00 |
| Lotofácil | 15 | 1-25 | R$ 2,50 |
| Lotomania | 20 | 0-99 | R$ 2,50 |
| Quina | 5 | 1-80 | R$ 2,00 |
| Loteca | 14 | 1-14 | R$ 1,50 |
| Timemania | 10 | 1-80 | R$ 2,00 |
| Dia de Sorte | 7 | 1-31 | R$ 2,00 |

## 📝 Licença

Projeto para fins educacionais.
