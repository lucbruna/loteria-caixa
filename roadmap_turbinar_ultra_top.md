# ROADMAP: Levar o projeto ao nível ULTRA-TOP

Baseado em análise estatística moderna p/ séries temporais + loterias. Foco: **menos viés, mais incerteza, auditável**.

## 1) VALIDAÇÃO CIENTÍFICA (CRÍTICO - PRIORIDADE MÁXIMA)

Criar base de validação imbatível.

- [ ] **Walk-Forward (expanding/rolling)** – `src/validate/walkforward.py`
  - Treina até T-1, testa T (simula "ao vivo")
  - Expanding window (mais dados) e Rolling window (adaptativo)
  - Métricas por bloco + agregadas

- [ ] **Purged Time Series CV + Embargo** – `src/validate/tscv_purged.py`
  - Evita leakage entre concursos próximos
  - Essencial p/ features que olham "últimos N"

- [ ] **Permutation Test (significância)** – `src/stats/significance.py`
  - Embaralha alvos → compara com modelo real
  - Responde: "vence acaso?" com p-valor

- [ ] **Bootstrap CI** – `src/stats/bootstrap_ci.py`
  - IC95% p/ taxa de acerto real
  - Mostra incerteza, não só média

- [ ] **Multiple Testing Correction** (FDR/BH) – `src/stats/multiple_tests.py`
  - Evita falsos positivos ao testar muitos modelos

**Impacto:** ★★★★★ | **Esforço:** Baixo

## 2) MODELAGEM ESTATÍSTICA CORRETA (DÁ INTELIGÊNCIA REAL)

Tratar como **multinomial** + modelar por posição.

- [ ] **Multinomial/Dirichlet-Multinomial** – `src/models/bayes_dm.py`
  - Modelo probabilístico correto p/ sorteio sem reposição
  - Suavização Bayesiana
  - Retorna distribuição posterior

- [ ] **Survival/Gaps (Weibull)** – `src/features/gap_survival.py`
  - `last_seen` → _time-to-reappear_
  - Hazard rate mais realista que `1/(gap+1)`

- [ ] **HMM por posição** – `src/models/hmm_position.py`
  - 5 modelos (pos1–pos5) separados
  - Captura regimes latentes
  - Usa `hmmlearn`

- [ ] **Bayes Hierárquico (PyMC/NumPyro)** – `src/models/hierarchical_bayes.py`
  - Comparte informação entre posições
  - Gera **intervalos de credibilidade** (HPD)
  - Calibrado por design

**Impacto:** ★★★★★ | **Esforço:** Médio

## 3) ML POR POSIÇÃO + SOTA LEVE (MELHOR CUSTO/BENEFÍCIO)

Focar em **prever "aparece nesta posição?"** ao invés de "acertar bilhete inteiro".

- [ ] **Dataset por posição** – `src/data/build_pos_dataset.py`
  - Features: freq, gap, co-ocorrência, par/impar, faixa, soma, distâncias, últimos N
  - Target binário: 1 se bilhete apareceu na pos P em T+1

- [ ] **LightGBM/CatBoost por posição** – `src/models/pos_lgbm.py`
  - Treino 5 modelos independentes
  - `groupby` por posição no walk-forward
  - Validação temporal estrita

- [ ] **TSFresh** (explorar features) – `src/features/tsfresh_gen.py`
  - Gera features temporais automáticas
  - Seleção com correlação + importância
  - Evita feature engineering cego

- [ ] **NeuralForecast (N-BEATS/N-HiTS)** – `src/models/neuralforecast_setup.py`
  - Ótimo baseline moderno
  - Reproduzível
  - Roda local com CPU

**Impacto:** ★★★★★ | **Esforço:** Baixo–Médio

## 4) CALIBRAÇÃO, CONFORMAL, EXPLICABILIDADE (DIFERENCIAL)

Tornar **honesto e explicável**.

- [ ] **Calibração de probabilidades** – `src/validate/calibration.py`
  - Isotonic Regression / Platt Scaling
  - Reliability Diagram
  - **Brier Score** (métrica chave)

- [ ] **Conformal Prediction (MAPIE)** – `src/models/conformal.py`
  - `TimeSeriesSplit` + conformal
  - Gera **prediction sets** com cobertura garantida (ex. 90%)
  - Em vez de "palpite único", mostra **conjunto plausível**

- [ ] **SHAP** – `src/explain/shap_analysis.py`
  - Explica por sugestão: "por que esse bilhete?"
  - Global + local (por concurso)
  - Salvar plots/texto p/ auditoria

**Impacto:** ★★★★★ | **Esforço:** Baixo

## 5) DRIFT, MONITORAMENTO E AUDITABILIDADE (PRODUÇÃO-LIKE)

Detectar mudanças + manter rastreabilidade.

- [ ] **Concept/Data Drift** – `src/monitor/drift.py`
  - Usar [`evidently`](https://www.evidentlyai.com/) (leve) ou [`river`](https://riverml.xyz/)
  - Monitorar distribuição de features/score
  - Alertar se drift > threshold

- [ ] **Model Card** – `model_card.md`
  - Objetivo, dados, metodologia, métricas reais, limitações
  - Como foi validado
  - Disclaimer claro

- [ ] **Experiments Tracking** – `src/track/experiments.py`
  - Salvar config, métricas, hash de dados, seed
  - JSON + CSV p/ reprodutibilidade
  - `reports/experiments.json`

- [ ] **Predictions Audit DB** – `reports/audit_history.jsonl`
  - Log: `concurso, metodo, preds[], reais[], acertou, score, timestamp`
  - Permite auditoria retroativa infinita

- [ ] **Unified CLI** – `cli/app.py`
  - `audit` (roda tudo validado)
  - `predict --explain --calibrated --conformal`
  - `report` (gera PDF/MD consolidado)
  - `drift-check`

**Impacto:** ★★★★★ | **Esforço:** Baixo–Médio

## 6) IMPLEMENTAÇÃO IMEDIATA (PRÓXIMOS 2–3 PASSOS)

Fazer em ordem p/ ganhar muito com pouco.

### Passo A – Walk-Forward + Significância (hoje)
```bash
# criar
src/validate/walkforward.py
src/stats/significance.py
```
- Validar modelo atual com walk-forward real
- Rodar permutation test → ver se p < 0.05 ou não

### Passo B – Dataset por posição + LightGBM
```bash
src/data/build_pos_dataset.py
src/models/pos_lgbm.py
```
- Provavelmente supera heurístico atual
- Fácil de auditar com SHAP

### Passo C – Calibração + Conformal
```bash
src/validate/calibration.py
src/models/conformal.py
```
- Transforma "top10" em **"conjunto com 90% de cobertura"**
- Muito mais honesto e útil

### Passo D – SHAP + Drift
```bash
src/explain/shap_analysis.py
src/monitor/drift.py
```
- Explicabilidade completa
- Detecta quando modelo perde validade

## MÉTRICAS QUE REALMENTE IMPORTAM

Trocar "hits/topK" por estas:

| Métrica | Por quê | Ideal |
|---|---|---|
| **Brier Score** | Mede calibração (probabilidades reais) | ↓ menor melhor |
| **Log Loss** | Penaliza confiança errada | ↓ |
| **Calibration Error (ECE)** | Diferença entre previsto vs observado | ↓ < 0.05 |
| **Coverage (Conformal)** | % reais dentro do conjunto | ≈ alpha desejado (0.9) |
| **Average Set Size** | Quão prático é o conjunto | ↓ (menor conjunto com boa cobertura) |
| **Hit Rate @ calibrated threshold** | Mais realista que "top10 fixo" | Medir honestamente |
| **p-value (permutation)** | Significância estatística | < 0.05 forte evidência |
| **Win Rate vs Random** | Comparação direta com null | > 0 com IC95 excluindo 0 |

## ESTRUTURA FINAIS PROPOSTA

Adicionar pastas sem quebrar existente:

```text
src/
├── stats/        # bootstrap, permutation, multiple tests
├── data/         # build datasets
├── explain/      # shap
├── monitor/      # drift
├── track/        # experiments
└── validate/     # walkforward, tscv, calibration (expandir)

cli/
└── app.py        # unificado

reports/
├── experiments.json
├── audit_history.jsonl
└── drift_reports/
```

## RECOMENDAÇÃO FINAL

**Não adicione mais "pesos mágicos". Adicione _medição científica_.**

Ordem exata p/ turbinar AGORA:

1. `walkforward.py` + `significance.py` → **prova real**
2. `pos_lgbm.py` → **melhor preditor testado honestamente**
3. `calibration.py` + `conformal.py` → **probabilidades + conjuntos plausíveis**
4. `shap_analysis.py` → **explicabilidade total**
5. `drift.py` → **sustentabilidade a longo prazo**

**Com isso você transforma num projeto realmente _ultra-top_: auditável, reproduzível, estatisticamente fundamentado e honesto.** Difícil encontrar algo melhor nesse nicho.