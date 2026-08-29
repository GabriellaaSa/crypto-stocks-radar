"""Backtest simples: buy-and-hold vs. rebalanceamento periódico, com custo de transação.

Tudo aqui é simulação histórica — nenhuma ordem real é enviada.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .indicators import TRADING_DAYS_PER_YEAR


def _metrics(portfolio_value: pd.Series) -> dict:
    returns = portfolio_value.pct_change().dropna()
    total_return = portfolio_value.iloc[-1] / portfolio_value.iloc[0] - 1
    n_days = len(returns)
    annual_return = (1 + total_return) ** (TRADING_DAYS_PER_YEAR / n_days) - 1 if n_days else np.nan
    annual_vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    drawdown = portfolio_value / portfolio_value.cummax() - 1
    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe_ratio": annual_return / annual_vol if annual_vol else np.nan,
        "max_drawdown": drawdown.min(),
    }


def backtest_buy_and_hold(prices: pd.DataFrame, weights: dict[str, float]) -> dict:
    """Compra na primeira data conforme os pesos e nunca mais mexe."""
    subset = prices[list(weights)].dropna()
    total = sum(weights.values()) or 1.0
    units = {t: (w / total) / subset[t].iloc[0] for t, w in weights.items()}
    value = sum(subset[t] * u for t, u in units.items())
    return {"portfolio_value": value, "metrics": _metrics(value), "total_costs": 0.0}


def backtest_rebalance(
    prices: pd.DataFrame,
    weights: dict[str, float],
    freq: str = "ME",
    cost_bps: float = 10.0,
) -> dict:
    """Rebalanceia para os pesos-alvo a cada período (`freq`, padrão mensal).

    `cost_bps` é o custo de transação em pontos-base sobre o valor negociado
    (10 bps = 0,10% por trade, ida). O custo é debitado do valor da carteira.
    """
    subset = prices[list(weights)].dropna()
    total = sum(weights.values()) or 1.0
    target = {t: w / total for t, w in weights.items()}
    cost_rate = cost_bps / 10_000

    rebalance_dates = set(subset.resample(freq).last().index[:-1])

    units = {t: target[t] / subset[t].iloc[0] for t in target}
    values, total_costs = [], 0.0

    for date, row in subset.iterrows():
        value = sum(row[t] * u for t, u in units.items())

        if date in rebalance_dates:
            traded = sum(abs(target[t] * value - row[t] * units[t]) for t in target)
            cost = traded * cost_rate
            total_costs += cost
            value -= cost
            units = {t: target[t] * value / row[t] for t in target}

        values.append(value)

    value_series = pd.Series(values, index=subset.index)
    return {"portfolio_value": value_series, "metrics": _metrics(value_series), "total_costs": total_costs}


def compare_strategies(
    prices: pd.DataFrame,
    weights: dict[str, float],
    freq: str = "ME",
    cost_bps: float = 10.0,
) -> pd.DataFrame:
    """Tabela comparativa buy-and-hold vs. rebalanceamento periódico."""
    bh = backtest_buy_and_hold(prices, weights)
    rb = backtest_rebalance(prices, weights, freq=freq, cost_bps=cost_bps)
    df = pd.DataFrame(
        {"Buy & Hold": bh["metrics"], f"Rebalanceada ({freq}, {cost_bps:.0f} bps)": rb["metrics"]}
    )
    df.loc["total_costs"] = [bh["total_costs"], rb["total_costs"]]
    return df
