"""Simulador de carteira hipotética — apenas cálculo histórico, nenhuma ordem é enviada."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .indicators import TRADING_DAYS_PER_YEAR


def simulate_portfolio(prices: pd.DataFrame, weights: dict[str, float]) -> dict:
    """Simula uma carteira com pesos fixos (rebalanceamento buy-and-hold normalizado).

    `weights` deve somar 1.0 (é normalizado automaticamente caso não some).
    """
    tickers = list(weights.keys())
    total_weight = sum(weights.values()) or 1.0
    norm_weights = {t: w / total_weight for t, w in weights.items()}

    subset = prices[tickers].dropna()
    normalized = subset / subset.iloc[0]
    weighted = normalized.mul(pd.Series(norm_weights), axis=1)
    portfolio_value = weighted.sum(axis=1)

    returns = portfolio_value.pct_change().dropna()
    total_return = portfolio_value.iloc[-1] / portfolio_value.iloc[0] - 1
    n_days = len(returns)
    annual_return = (1 + total_return) ** (TRADING_DAYS_PER_YEAR / n_days) - 1 if n_days else np.nan
    annual_vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    sharpe_ratio = annual_return / annual_vol if annual_vol else np.nan
    drawdown = portfolio_value / portfolio_value.cummax() - 1
    max_drawdown = drawdown.min()

    return {
        "portfolio_value": portfolio_value,
        "drawdown": drawdown,
        "weights": norm_weights,
        "total_return": total_return,
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
    }
