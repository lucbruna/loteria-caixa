from collections import Counter

import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler

try:
    import xgboost as xgb
except Exception:
    # XGBoostLibraryNotFound (DLL ausente no bundle) herda de XGBoostError,
    # nao de ImportError - capturamos Exception para degradar com graca.
    xgb = None

try:
    import lightgbm as lgb
except Exception:
    lgb = None


def _config_keys(config):
    min_num = config.get("min_num", 1)
    max_num = config.get("max_num", 60)
    qtd_sorteados = config.get("pick_count", 6)
    return min_num, max_num, qtd_sorteados


def _dezenas_int(concurso):
    """Converte o campo listaDezenas (strings, ex: "05") para set de ints."""
    return {int(d) for d in concurso.get("listaDezenas", [])}


class RegressaoLogistica:
    def __init__(self, C=1.0, penalty='l2', max_iter=1000):  # noqa: N803
        self.C = C
        self.penalty = penalty
        self.max_iter = max_iter

    def analisar(self, resultados, config):
        min_num, max_num, qtd_sorteados = _config_keys(config)
        total_numeros = max_num - min_num + 1
        n_concursos = len(resultados)

        if n_concursos < 20:
            return {"erro": "Dados insuficientes para regressao logistica", "min_concursos": 20}

        matriz_features, y_binario = [], []
        for i in range(1, n_concursos):
            concurso_atual = _dezenas_int(resultados[i])
            for n in range(min_num, max_num + 1):
                matriz_features.append(self._extrair_features(resultados, i, n, total_numeros, qtd_sorteados))
                y_binario.append(1 if n in concurso_atual else 0)

        x = np.array(matriz_features, dtype=float)
        y = np.array(y_binario)
        if len(np.unique(y)) < 2:
            return {"erro": "Classe unica nos dados"}

        x_scaled = StandardScaler().fit_transform(x)
        # Nota: penalty foi deprecado no sklearn 1.8 (removido na 1.10).
        # solver='liblinear' ja aplica L2 por padrao, equivalente ao antigo penalty='l2'.
        modelo = LogisticRegression(C=self.C, max_iter=self.max_iter, solver='liblinear', random_state=42)
        modelo.fit(x_scaled, y)

        probabilities = modelo.predict_proba(x_scaled)[:, 1]
        prob_by_num = {}
        for idx, n in enumerate(range(min_num, max_num + 1)):
            prob_by_num[n] = float(np.mean(probabilities[idx::total_numeros]))

        top_nums = sorted(prob_by_num.items(), key=lambda x: -x[1])

        tscv = TimeSeriesSplit(n_splits=min(5, n_concursos - 1))
        scores = cross_val_score(modelo, x_scaled, y, cv=tscv, scoring='accuracy')
        ac_cv = float(np.mean(scores)) if len(scores) > 0 else 0.0

        return {
            "classe": "Regressao Logistica",
            "regularizacao": f"L{self.penalty[1]} (C={self.C})",
            "acuracia_treino": round(accuracy_score(y, modelo.predict(x_scaled)), 4),
            "acuracia_cross_val": round(ac_cv, 4),
            "top10_mais_probaveis": [{"numero": n, "probabilidade": round(p, 4)} for n, p in top_nums[:10]],
            "top10_menos_probaveis": [{"numero": n, "probabilidade": round(p, 4)} for n, p in top_nums[-10:]],
            "numeros_recomendados": [n for n, _ in top_nums[:qtd_sorteados * 2]],
            "probabilidades": {str(k): round(v, 4) for k, v in top_nums},
        }

    def _extrair_features(self, resultados, idx, numero, total_numeros, qtd_sorteados):
        n_appear, n_absent, atraso = 0, 0, 0
        for concurso in resultados[:idx + 1]:
            if numero in _dezenas_int(concurso):
                n_appear += 1
                atraso = 0
            else:
                n_absent += 1
                atraso += 1
        frec = n_appear / max(1, n_appear + n_absent)
        return [frec, atraso / max(1, qtd_sorteados), n_appear / max(1, idx + 1), n_appear, n_absent]


class ArimaReal:
    def __init__(self, ordem=(2, 1, 2)):
        self.ordem = ordem

    def analisar(self, resultados, config):
        from statsmodels.tsa.arima.model import ARIMA
        min_num, max_num, qtd_sorteados = _config_keys(config)
        total_numeros = max_num - min_num + 1
        n_concursos = len(resultados)

        if n_concursos < 30:
            return {"erro": "Dados insuficientes para ARIMA (min 30 concursos)", "min_concursos": 30}

        resultados_arima = {}

        for n in range(min_num, max_num + 1):
            serie = np.array([1 if n in _dezenas_int(c) else 0 for c in resultados], dtype=float)
            try:
                model = ARIMA(serie, order=self.ordem).fit()
                forecast = model.forecast(steps=5)
                media_prevista = float(np.mean(forecast))
                resultados_arima[n] = media_prevista
            except Exception:
                media_hist = float(np.mean(serie))
                resultados_arima[n] = media_hist

        esperado = n_concursos * qtd_sorteados / total_numeros

        top_sorted = sorted(resultados_arima.items(), key=lambda x: -x[1])
        quentes_arima = top_sorted[:10]
        frios_arima = top_sorted[-10:]

        numeros_recomendados = [n for n, _ in top_sorted[:qtd_sorteados * 2]]

        return {
            "classe": "ARIMA Real (statsmodels)",
            "ordem": self.ordem,
            "concursos_analisados": n_concursos,
            "frequencia_esperada": round(esperado, 2),
            "numeros_recomendados": numeros_recomendados,
            "top10_quentes_forecast": [{"numero": n, "previsao": round(p, 4)} for n, p in quentes_arima],
            "top10_frios_forecast": [{"numero": n, "previsao": round(p, 4)} for n, p in frios_arima],
            "probabilidades": {
                str(k): round(float(v), 4)
                for k, v in sorted(resultados_arima.items(), key=lambda x: -x[1])
            },
        }


class XGBoostReal:
    def __init__(self, n_estimators=200, max_depth=4, learning_rate=0.1):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate

    def analisar(self, resultados, config):
        if xgb is None:
            return {"erro": "xgboost nao instalado"}
        min_num, max_num, qtd_sorteados = _config_keys(config)
        total_numeros = max_num - min_num + 1
        n_concursos = len(resultados)

        if n_concursos < 20:
            return {"erro": "Dados insuficientes para XGBoost", "min_concursos": 20}

        matriz_features, y_binario = [], []
        for i in range(1, n_concursos):
            concurso_atual = _dezenas_int(resultados[i])
            for n in range(min_num, max_num + 1):
                matriz_features.append(self._extrair_features(resultados, i, n, total_numeros, qtd_sorteados))
                y_binario.append(1 if n in concurso_atual else 0)

        x = np.array(matriz_features, dtype=float)
        y = np.array(y_binario)
        if len(np.unique(y)) < 2:
            return {"erro": "Classe unica"}

        modelo = xgb.XGBClassifier(
            n_estimators=self.n_estimators, max_depth=self.max_depth,
            learning_rate=self.learning_rate, subsample=0.8, colsample_bytree=0.8,
            random_state=42, eval_metric='logloss'
        )
        modelo.fit(x, y)

        prob = modelo.predict_proba(x)[:, 1]
        prob_by_num = {}
        for idx, n in enumerate(range(min_num, max_num + 1)):
            prob_by_num[n] = float(np.mean(prob[idx::total_numeros]))

        importancia = modelo.feature_importances_
        top_feats = sorted([(i, float(v)) for i, v in enumerate(importancia)], key=lambda x: -x[1])[:15]

        top_nums = sorted(prob_by_num.items(), key=lambda x: -x[1])

        tscv = TimeSeriesSplit(n_splits=min(5, n_concursos - 1))
        scores = cross_val_score(modelo, x, y, cv=tscv, scoring='accuracy')
        ac_cv = float(np.mean(scores)) if len(scores) > 0 else 0.0

        return {
            "classe": "XGBoost Real",
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "learning_rate": self.learning_rate,
            "acuracia_treino": round(accuracy_score(y, modelo.predict(x)), 4),
            "acuracia_cross_val": round(ac_cv, 4),
            "top10_mais_probaveis": [{"numero": n, "probabilidade": round(p, 4)} for n, p in top_nums[:10]],
            "top10_menos_probaveis": [{"numero": n, "probabilidade": round(p, 4)} for n, p in top_nums[-10:]],
            "numeros_recomendados": [n for n, _ in top_nums[:qtd_sorteados * 2]],
            "top_features": [{"feature_idx": i, "importancia": round(v, 4)} for i, v in top_feats],
        }

    def _extrair_features(self, resultados, idx, numero, total_numeros, qtd_sorteados):
        n_appear, n_absent, atraso = 0, 0, 0
        for concurso in resultados[:idx + 1]:
            if numero in _dezenas_int(concurso):
                n_appear += 1
                atraso = 0
            else:
                n_absent += 1
                atraso += 1
        frec = n_appear / max(1, n_appear + n_absent)
        return [frec, atraso / max(1, qtd_sorteados), n_appear / max(1, idx + 1), n_appear, n_absent]


class LightGBMReal:
    def __init__(self, n_estimators=200, max_depth=4, learning_rate=0.1):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate

    def analisar(self, resultados, config):
        if lgb is None:
            return {"erro": "lightgbm nao instalado"}
        min_num, max_num, qtd_sorteados = _config_keys(config)
        total_numeros = max_num - min_num + 1
        n_concursos = len(resultados)

        if n_concursos < 20:
            return {"erro": "Dados insuficientes para LightGBM", "min_concursos": 20}

        matriz_features, y_binario = [], []
        for i in range(1, n_concursos):
            concurso_atual = _dezenas_int(resultados[i])
            for n in range(min_num, max_num + 1):
                matriz_features.append(self._extrair_features(resultados, i, n, total_numeros, qtd_sorteados))
                y_binario.append(1 if n in concurso_atual else 0)

        x = np.array(matriz_features, dtype=float)
        y = np.array(y_binario)
        if len(np.unique(y)) < 2:
            return {"erro": "Classe unica"}

        modelo = lgb.LGBMClassifier(
            n_estimators=self.n_estimators, max_depth=self.max_depth,
            learning_rate=self.learning_rate, subsample=0.8, colsample_bytree=0.8,
            random_state=42, verbose=-1
        )
        modelo.fit(x, y)

        prob = modelo.predict_proba(x)[:, 1]
        prob_by_num = {}
        for idx, n in enumerate(range(min_num, max_num + 1)):
            prob_by_num[n] = float(np.mean(prob[idx::total_numeros]))

        importancia = modelo.feature_importances_
        top_feats = sorted([(i, float(v)) for i, v in enumerate(importancia)], key=lambda x: -x[1])[:15]

        top_nums = sorted(prob_by_num.items(), key=lambda x: -x[1])

        tscv = TimeSeriesSplit(n_splits=min(5, n_concursos - 1))
        scores = cross_val_score(modelo, x, y, cv=tscv, scoring='accuracy')
        ac_cv = float(np.mean(scores)) if len(scores) > 0 else 0.0

        return {
            "classe": "LightGBM Real",
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "learning_rate": self.learning_rate,
            "acuracia_treino": round(accuracy_score(y, modelo.predict(x)), 4),
            "acuracia_cross_val": round(ac_cv, 4),
            "top10_mais_probaveis": [{"numero": n, "probabilidade": round(p, 4)} for n, p in top_nums[:10]],
            "top10_menos_probaveis": [{"numero": n, "probabilidade": round(p, 4)} for n, p in top_nums[-10:]],
            "numeros_recomendados": [n for n, _ in top_nums[:qtd_sorteados * 2]],
            "top_features": [{"feature_idx": i, "importancia": round(v, 4)} for i, v in top_feats],
        }

    def _extrair_features(self, resultados, idx, numero, total_numeros, qtd_sorteados):
        n_appear, n_absent, atraso = 0, 0, 0
        for concurso in resultados[:idx + 1]:
            if numero in _dezenas_int(concurso):
                n_appear += 1
                atraso = 0
            else:
                n_absent += 1
                atraso += 1
        frec = n_appear / max(1, n_appear + n_absent)
        return [frec, atraso / max(1, qtd_sorteados), n_appear / max(1, idx + 1), n_appear, n_absent]


class DistribuicaoPoisson:
    def __init__(self):
        pass

    def analisar(self, resultados, config):
        min_num, max_num, qtd_sorteados = _config_keys(config)
        total_numeros = max_num - min_num + 1
        if not resultados:
            return {"erro": "Sem dados"}

        frequencias = Counter()
        for concurso in resultados:
            for n in _dezenas_int(concurso):
                frequencias[n] += 1

        n_concursos = len(resultados)
        esperado = n_concursos * qtd_sorteados / total_numeros

        prob_poisson, prob_geometrica = {}, {}
        for n in range(min_num, max_num + 1):
            lam = max(0.1, frequencias.get(n, 0))
            prob_poisson[n] = float(stats.poisson.pmf(min(1, max(0, round(lam / esperado * qtd_sorteados))), lam))
            p_geom = lam / (n_concursos + 1)
            prob_geometrica[n] = float(stats.geom.pmf(1, p_geom) if 0 < p_geom < 1 else 1 / total_numeros)

        normalizado = {
            k: float((prob_poisson.get(k, 0) + prob_geometrica.get(k, 0)) / 2)
            for k in range(min_num, max_num + 1)
        }
        soma = sum(normalizado.values()) or 1
        normalizado = {k: v / soma for k, v in normalizado.items()}

        top_poisson = sorted(normalizado.items(), key=lambda x: -x[1])

        return {
            "classe": "Distribuicao Poisson + Geometrica",
            "lambda_geral": round(esperado, 3),
            "convergiu": abs(esperado - n_concursos * qtd_sorteados / total_numeros) < 1,
            "top10_poisson": [{"numero": n, "prob": round(p, 4)} for n, p in top_poisson[:10]],
            "top10_poisson_frio": [{"numero": n, "prob": round(p, 4)} for n, p in top_poisson[-10:]],
            "numeros_recomendados": [n for n, _ in top_poisson[:qtd_sorteados * 2]],
            "probabilidades_combinadas": {
                str(k): round(v, 6) for k, v in sorted(normalizado.items(), key=lambda x: -x[1])
            },
        }


def executar_analise_completa(resultados, config):
    return {
        "regressao_logistica": RegressaoLogistica(C=1.0, penalty='l2').analisar(resultados, config),
        "arima_real": ArimaReal(ordem=(2, 1, 2)).analisar(resultados, config),
        "distribuicao_poisson": DistribuicaoPoisson().analisar(resultados, config),
        "xgboost_real": XGBoostReal().analisar(resultados, config),
        "lightgbm_real": LightGBMReal().analisar(resultados, config),
    }
