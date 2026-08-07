"""
Analise World-Class - Top 4 Tecnicas de Alto Impacto
1. Regressao Logistica Regularizada (L1/L2/ElasticNet)
2. ARIMA / Exponential Smoothing
3. Gradient Boosting (sklearn)
4. Ajuste de Distribuicao (Poisson, Geometrica, Binomial Negativa)
"""
import warnings
from collections import Counter

import numpy as np
from scipy import stats as sp_stats

warnings.filterwarnings("ignore")


class AnaliseWorldClass:
    """Top 4 tecnicas world-class para analise de loterias."""

    def __init__(self, min_num: int, max_num: int, pick_count: int):
        self.min_num = min_num
        self.max_num = max_num
        self.pick_count = pick_count
        self.pool_size = max_num - min_num + 1

    def _preparar_features(self, resultados: list[list[int]], janela: int = 10):
        """Cria features de series temporais a partir do historico."""
        n = len(resultados)
        if n < janela + 5:
            return None, None, None

        x, y = [], []

        for i in range(janela, n):
            janela_anterior = resultados[i - janela:i]
            features = []

            for num in range(self.min_num, self.max_num + 1):
                freq = sum(1 for d in janela_anterior if num in d)
                features.extend([
                    freq / janela,
                    (1 if num in resultados[i - 1] else 0),
                    (1 if num in resultados[i - 2] else 0) if i >= 2 else 0,
                    (1 if num in resultados[i - 3] else 0) if i >= 3 else 0,
                    sum(1 for d in janela_anterior[-3:] if num in d) / 3,
                    sum(1 for d in janela_anterior[-5:] if num in d) / 5,
                ])

            x.append(features)
            y.append([1 if num in resultados[i] else 0 for num in range(self.min_num, self.max_num + 1)])

        return np.array(x), np.array(y), list(range(self.min_num, self.max_num + 1))

    def regressao_logistica(self, resultados: list[list[int]], janela: int = 10):
        """Regressao Logistica Regularizada (L1/L2/ElasticNet)."""
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler

        x, y, numeros = self._preparar_features(resultados, janela)
        if x is None or len(x) < 20:
            return {
                "metodo": "regressao_logistica",
                "probabilidades": {},
                "top_numeros": [],
                "erro": "Dados insuficientes",
            }

        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)

        probabilidades = {}
        for i, num in enumerate(numeros):
            try:
                modelo = LogisticRegression(
                    penalty="elasticnet", solver="saga",
                    l1_ratio=0.5, C=1.0, max_iter=500, random_state=42
                )
                modelo.fit(x_scaled, y[:, i])
                prob = modelo.predict_proba(x_scaled[-1:])
                probabilidades[num] = float(prob[0][1])
            except Exception:
                probabilidades[num] = y[:, i].mean()

        total = sum(probabilidades.values()) or 1
        probabilidades = {k: v / total for k, v in probabilidades.items()}
        top = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15]

        return {
            "metodo": "regressao_logistica",
            "regularizacao": "elasticnet_l1r0.5",
            "probabilidades": {str(k): round(v, 6) for k, v in probabilidades.items()},
            "top_numeros": [{"numero": k, "probabilidade": round(v, 6)} for k, v in top],
            "janela": janela,
            "amostras_treino": len(x),
        }

    def arima_simplificado(self, resultados: list[list[int]], ordem: tuple = (2, 1, 1)):
        """ARIMA para cada numero - previsao de aparecimento."""
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        numeracao = list(range(self.min_num, self.max_num + 1))
        probabilidades = {}

        for num in numeracao:
            serie = np.array([1 if num in d else 0 for d in resultados], dtype=float)
            if serie.sum() < 3:
                probabilidades[num] = float(serie.mean())
                continue

            try:
                modelo = ARIMA(serie, order=ordem)
                ajuste = modelo.fit()
                pred = ajuste.forecast(steps=1)
                probabilidades[num] = float(np.clip(pred[0], 0, 1))
            except Exception:
                try:
                    if len(serie) >= 10:
                        ets = ExponentialSmoothing(
                            serie, trend="add", seasonal=None, damped_trend=True
                        ).fit(optimized=True)
                        pred_ets = ets.forecast(steps=1)
                        probabilidades[num] = float(np.clip(pred_ets[0], 0, 1))
                    else:
                        probabilidades[num] = float(serie.mean())
                except Exception:
                    probabilidades[num] = float(serie.mean())

            media_movel = serie[-5:].mean() if len(serie) >= 5 else serie.mean()
            if num in probabilidades:
                probabilidades[num] = 0.7 * probabilidades[num] + 0.3 * media_movel

        total = sum(probabilidades.values()) or 1
        probabilidades = {k: v / total for k, v in probabilidades.items()}
        top = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15]

        return {
            "metodo": "arima_exponential_smoothing",
            "ordem": list(ordem),
            "probabilidades": {str(k): round(v, 6) for k, v in probabilidades.items()},
            "top_numeros": [{"numero": k, "probabilidade": round(v, 6)} for k, v in top],
        }

    def gradient_boosting(self, resultados: list[list[int]], janela: int = 10):
        """Gradient Boosting Classifier para cada numero."""
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.preprocessing import StandardScaler

        x, y, numeros = self._preparar_features(resultados, janela)
        if x is None or len(x) < 30:
            return {
                "metodo": "gradient_boosting",
                "probabilidades": {},
                "top_numeros": [],
                "erro": "Dados insuficientes",
            }

        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)

        probabilidades = {}
        importancias = {}
        for i, num in enumerate(numeros):
            try:
                modelo = GradientBoostingClassifier(
                    n_estimators=100, max_depth=4, learning_rate=0.1,
                    subsample=0.8, random_state=42
                )
                modelo.fit(x_scaled, y[:, i])
                prob = modelo.predict_proba(x_scaled[-1:])
                probabilidades[num] = float(prob[0][1])
                importancias[num] = float(modelo.feature_importances_.max())
            except Exception:
                probabilidades[num] = y[:, i].mean()

        total = sum(probabilidades.values()) or 1
        probabilidades = {k: v / total for k, v in probabilidades.items()}
        top = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15]

        return {
            "metodo": "gradient_boosting",
            "probabilidades": {str(k): round(v, 6) for k, v in probabilidades.items()},
            "top_numeros": [{"numero": k, "probabilidade": round(v, 6)} for k, v in top],
            "n_estimators": 100,
            "janela": janela,
            "amostras_treino": len(x),
        }

    def ajuste_distribuicao(self, resultados: list[list[int]]):
        """Ajusta distribuicoes estatisticas (Poisson, Geometrica, Binomial Negativa)."""
        frequencias = Counter()
        for d in resultados:
            for n in d:
                frequencias[n] += 1

        total_sorteios = len(resultados)
        numeros = list(range(self.min_num, self.max_num + 1))
        freq_array = np.array([frequencias.get(n, 0) for n in numeros], dtype=float)

        media_freq = freq_array.mean()
        var_freq = freq_array.var()

        distribuicoes = {}

        try:
            lambda_poisson = media_freq
            poisson_pmf = [sp_stats.poisson.pmf(int(f), lambda_poisson) for f in freq_array]
            poisson_score = np.mean(poisson_pmf)
            distribuicoes["poisson"] = {
                "lambda": round(lambda_poisson, 4),
                "score": round(float(poisson_score), 6),
                "media_observada": round(media_freq, 4),
                "media_esperada": round(lambda_poisson, 4),
            }
        except Exception:
            pass

        try:
            if media_freq > 0:
                p_geom = 1 / (1 + media_freq)
                geom_pmf = [sp_stats.geom.pmf(max(1, f + 1), p_geom) for f in freq_array]
                geom_score = np.mean(geom_pmf)
                distribuicoes["geometrica"] = {
                    "p": round(p_geom, 6),
                    "media": round((1 - p_geom) / p_geom, 4),
                    "score": round(float(geom_score), 6),
                }
        except Exception:
            pass

        try:
            if var_freq > media_freq and media_freq > 0:
                p_nb = media_freq / var_freq
                r_nb = media_freq * p_nb / (1 - p_nb) if p_nb < 1 else 1
                r_nb = max(0.1, min(r_nb, 100))
                nb_pmf = [sp_stats.nbinom.pmf(max(0, int(f)), r_nb, p_nb) for f in freq_array]
                nb_score = np.mean(nb_pmf)
                distribuicoes["binomial_negativa"] = {
                    "r": round(r_nb, 4),
                    "p": round(p_nb, 6),
                    "media": round(r_nb * (1 - p_nb) / p_nb, 4),
                    "variancia": round(r_nb * (1 - p_nb) / (p_nb ** 2), 4),
                    "score": round(float(nb_score), 6),
                }
        except Exception:
            pass

        melhor = max(distribuicoes.items(), key=lambda x: x[1]["score"])[0] if distribuicoes else None

        probabilidades = {}
        for num in numeros:
            f = frequencias.get(num, 0)
            if melhor == "poisson":
                probabilidades[num] = sp_stats.poisson.pmf(f, media_freq)
            elif melhor == "geometrica":
                p_g = distribuicoes["geometrica"]["p"]
                probabilidades[num] = sp_stats.geom.pmf(max(1, f + 1), p_g)
            elif melhor == "binomial_negativa":
                p_nb = distribuicoes["binomial_negativa"]["p"]
                r_nb = distribuicoes["binomial_negativa"]["r"]
                probabilidades[num] = sp_stats.nbinom.pmf(max(0, f), r_nb, p_nb)
            else:
                probabilidades[num] = 1.0 / self.pool_size

        total_prob = sum(probabilidades.values()) or 1
        probabilidades = {k: v / total_prob for k, v in probabilidades.items()}
        top = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:15]

        return {
            "metodo": "ajuste_distribuicao",
            "distribuicoes_testadas": list(distribuicoes.keys()),
            "melhor_distribuicao": melhor,
            "detalhes_distribuicoes": distribuicoes,
            "probabilidades": {str(k): round(v, 6) for k, v in probabilidades.items()},
            "top_numeros": [{"numero": k, "probabilidade": round(v, 6)} for k, v in top],
            "total_sorteios": total_sorteios,
            "media_frequencia": round(media_freq, 4),
            "variancia_frequencia": round(var_freq, 4),
        }

    def ensemble_world_class(self, resultados: list[list[int]], janela: int = 10):
        """Ensemble das 4 tecnicas world-class."""
        print("  [1/4] Regressao Logistica Regularizada...")
        rl = self.regressao_logistica(resultados, janela)

        print("  [2/4] ARIMA + Exponential Smoothing...")
        arima = self.arima_simplificado(resultados)

        print("  [3/4] Gradient Boosting...")
        gb = self.gradient_boosting(resultados, janela)

        print("  [4/4] Ajuste de Distribuicao...")
        dist = self.ajuste_distribuicao(resultados)

        pesos = {"regressao_logistica": 0.30, "arima_exponential_smoothing": 0.25,
                 "gradient_boosting": 0.30, "ajuste_distribuicao": 0.15}

        todos_numeros = set(range(self.min_num, self.max_num + 1))
        probabilidade_final = {}

        for num in todos_numeros:
            soma = 0
            for resultado, peso in [(rl, pesos["regressao_logistica"]),
                                     (arima, pesos["arima_exponential_smoothing"]),
                                     (gb, pesos["gradient_boosting"]),
                                     (dist, pesos["ajuste_distribuicao"])]:
                probs = resultado.get("probabilidades", {})
                soma += float(probs.get(str(num), probs.get(num, 0))) * peso
            probabilidade_final[num] = soma

        total = sum(probabilidade_final.values()) or 1
        probabilidade_final = {k: v / total for k, v in probabilidade_final.items()}
        top_final = sorted(probabilidade_final.items(), key=lambda x: x[1], reverse=True)[:20]

        return {
            "metodo": "ensemble_world_class",
            "pesos": pesos,
            "sub_modelos": {
                "regressao_logistica": rl,
                "arima": arima,
                "gradient_boosting": gb,
                "distribuicao": dist,
            },
            "probabilidades_finais": {str(k): round(v, 6) for k, v in probabilidade_final.items()},
            "top_numeros": [{"numero": k, "probabilidade": round(v, 6)} for k, v in top_final],
            "top_20_numeros": [k for k, _ in top_final[:self.pick_count]],
        }
