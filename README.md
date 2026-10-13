# Loteria Federal Analytica (Evoluído)

Projeto reconstruído com foco em **transparência, auditoria e métricas reais**. Não promete "acertar sempre" – promete **medir com honestidade** o que funciona e o que não funciona.

## Objetivo
Tornar a análise de Loteria Federal mais inteligente, mensurável e auditável. Identificar o que realmente agrega vs o que só parece agregar.

## Dados
- Fonte: [guilhermeasn/loteria.json](https://github.com/guilhermeasn/loteria.json) (histórico oficial/compilado da Caixa)
- Formato Federal: 5 prêmios por concurso (1º ao 5º), cada um com bilhete de 6 dígitos
- Total: 5.901 concursos (conc 1–5919) | 29.505 prêmios

## Metodologia (correta)
- **Time-split estrito**: separar treino/teste por ordem temporal (nunca misturar). Ex: 80% passado → treina, 20% futuro → testa
- **Sem look-ahead**: predição p/ concurso T só usa dados < T
- **Limpeza**: remover `000000` (anomalias)
- **Métricas reais**: taxa de acerto exato sobre prêmios REAIS no holdout
- **Rolling/validado**: evitar cherry-picking
- **Transparente**: sempre mostrar hits/falhas

## Arquitetura
```
loteria-federal-analytica/
├── data/           # bruto + processado
├── src/
│   ├── ingest/     # processamento
│   ├── analysis/   # estatísticas
│   ├── features/    # engenharia (gap, posição, etc)
│   ├── models/      # preditores + scoring
│   ├── validate/   # backtesting rigoroso
│   └── metrics/    # métricas honestas
├── cli/            # ferramentas CLI
├── reports/        # auditorias geradas
└── docs/
```

## Resultados atuais (backtest honesto)
| Estratégia | Top-K | Acerto em holdout | Observação |
|---|---|---|---|
| Frequência histórica (puro) | top10 | **0,000%** | Superestima se usar todo histórico |
| Recência + Frequência (ponderado) | top10 | **~0,017%** | Ligeiramente melhor, mas ainda ~1 acerto / 5900 prêmios |

**Esses números são reais** com time-split. Qualquer valor muito acima disso provavelmente tem viés.

## Como rodar
```bash
# Auditoria completa (recomendado)
python3 loteria-federal-analytica/cli/run_audit.py

# Predições honestas p/ próximo concurso
python3 loteria-federal-analytica/cli/predict.py

# Gerar relatório predições vs reais (audit mode)
python3 loteria-federal-analytica/cli/audit_report.py

# Passo a passo
python3 loteria-federal-analytica/src/ingest/process_federal.py
python3 loteria-federal-analytica/src/analysis/basic_stats.py
python3 loteria-federal-analytica/src/features/pos_patterns.py
python3 loteria-federal-analytica/src/features/gap.py
python3 loteria-federal-analytica/src/features/sums_ranges.py
python3 loteria-federal-analytica/src/validate/backtest.py
python3 loteria-federal-analytica/src/validate/rolling_backtest.py
python3 loteria-federal-analytica/src/models/intelligent_fast.py
```

## Limitações importantes
- **Acerto exato é raro**: bilhetes são 6 dígitos (000000–999999). Probabilidade teórica muito baixa.
- **Aleatoriedade domina**: Federal é sorteio. Métodos estatísticos podem capturar pequenos vieses, mas ganhos práticos são limitados.
- **Não há garantia**: este projeto NÃO vende "palpites infalíveis". Foco é **análise + auditoria**.
- **Resultados passados não predizem futuro com certeza**: backtest mostra performance esperada sob condições históricas.

## Diferenças vs versão antiga
- ✅ Código-fonte organizado e auditável
- ✅ Backtesting com time-split (sem look-ahead)
- ✅ Métricas explícitas e reproduzíveis
- ✅ Limpeza de dados documentada
- ✅ Auditoria completa escrita
- ✅ Foco em "medir" ao invés de "prometer"

## Próximos passos
- [ ] CLI unificada (`cli/audit.py`, `cli/predict.py`)
- [ ] Mais features (soma, par/impar, faixas, co-ocorrência)
- [ ] Rolling window backtest
- [ ] Relatório automático com gráfico textual
- [ ] Explicabilidade por sugestão
- [ ] Testes básicos

## Auditoria
Ver `auditoria_completa.md` para análise detalhada de pontos fracos, o que não aparece e recomendações.
