"""Projeções estatísticas de preço — Monte Carlo (GBM) e score de momentum.

⚠️ São projeções baseadas exclusivamente no comportamento passado dos preços.
Mercado não é obrigado a repetir o passado: use como mapa de cenários, nunca
como previsão garantida ou recomendação de investimento.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .indicators import rsi, sma


def monte_carlo_paths(
    series: pd.Series,
    horizon_days: int = 30,
    n_sims: int = 2000,
    lookback_days: int = 252,
    seed: int | None = 42,
) -> pd.DataFrame:
    """Simula `n_sims` trajetórias de preço via Movimento Browniano Geométrico.

    Drift e volatilidade são estimados dos últimos `lookback_days` retornos diários.
    Retorna DataFrame (horizon_days x n_sims) começando no último preço observado.
    """
    clean = series.dropna()
    log_returns = np.log(clean / clean.shift(1)).dropna().tail(lookback_days)
    mu, sigma = log_returns.mean(), log_returns.std()

    rng = np.random.default_rng(seed)
    shocks = rng.normal(mu, sigma, size=(horizon_days, n_sims))
    paths = clean.iloc[-1] * np.exp(np.cumsum(shocks, axis=0))

    future_index = pd.bdate_range(start=clean.index[-1], periods=horizon_days + 1)[1:]
    return pd.DataFrame(paths, index=future_index)


def forecast_summary(series: pd.Series, horizon_days: int = 30, n_sims: int = 2000) -> dict:
    """Resume a simulação: bandas de percentil e probabilidade de alta no horizonte."""
    paths = monte_carlo_paths(series, horizon_days=horizon_days, n_sims=n_sims)
    last_price = series.dropna().iloc[-1]
    final = paths.iloc[-1]

    return {
        "paths": paths,
        "last_price": last_price,
        "bands": paths.quantile([0.05, 0.25, 0.50, 0.75, 0.95], axis=1).T,
        "prob_alta": float((final > last_price).mean()),
        "mediana_final": float(final.median()),
        "pessimista_p5": float(final.quantile(0.05)),
        "otimista_p95": float(final.quantile(0.95)),
    }


def momentum_scores(prices: pd.DataFrame) -> pd.DataFrame:
    """Score de momentum (-100 a +100) combinando tendência, RSI e retornos recentes.

    Componentes (cada um vale um terço do score):
    - tendência: preço vs. SMA 50 e SMA 20 vs. SMA 50;
    - RSI 14 centrado em 50;
    - retornos de 1 e 3 meses.
    """
    rows = []
    for ticker in prices.columns:
        serie = prices[ticker].dropna()
        if len(serie) < 70:
            continue

        sma20, sma50 = sma(serie, 20).iloc[-1], sma(serie, 50).iloc[-1]
        preco = serie.iloc[-1]
        trend = (50 if preco > sma50 else -50) + (50 if sma20 > sma50 else -50)

        rsi_val = rsi(serie).iloc[-1]
        rsi_score = np.clip((rsi_val - 50) * 4, -100, 100) if pd.notna(rsi_val) else 0

        ret_1m = serie.iloc[-1] / serie.iloc[-21] - 1
        ret_3m = serie.iloc[-1] / serie.iloc[-63] - 1
        ret_score = np.clip((ret_1m * 100 * 5 + ret_3m * 100 * 2) / 2, -100, 100)

        score = (trend + rsi_score + ret_score) / 3
        rows.append(
            {
                "ticker": ticker,
                "score_momentum": round(float(score), 1),
                "retorno_1m": ret_1m,
                "retorno_3m": ret_3m,
                "rsi": rsi_val,
                "leitura": (
                    "Momentum forte de alta" if score > 40
                    else "Viés de alta" if score > 10
                    else "Momentum forte de baixa" if score < -40
                    else "Viés de baixa" if score < -10
                    else "Neutro / lateral"
                ),
            }
        )

    return (
        pd.DataFrame(rows)
        .set_index("ticker")
        .sort_values("score_momentum", ascending=False)
    )
