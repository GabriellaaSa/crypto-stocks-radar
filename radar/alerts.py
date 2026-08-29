"""Sinais técnicos simples (RSI + cruzamento de médias). Apenas informativo — sem execução automática."""
from __future__ import annotations

import pandas as pd

from .indicators import rsi, sma


def evaluate_signals(
    prices: pd.DataFrame,
    rsi_window: int = 14,
    sma_short: int = 20,
    sma_long: int = 50,
    rsi_oversold: float = 30,
    rsi_overbought: float = 70,
) -> pd.DataFrame:
    rows = []
    min_len = sma_long + 1

    for ticker in prices.columns:
        series = prices[ticker].dropna()
        if len(series) < min_len:
            continue

        rsi_value = rsi(series, rsi_window).iloc[-1]
        sma_short_value = sma(series, sma_short).iloc[-1]
        sma_long_value = sma(series, sma_long).iloc[-1]
        last_price = series.iloc[-1]

        flags = []
        if pd.notna(rsi_value):
            if rsi_value < rsi_oversold:
                flags.append(f"RSI sobrevendido ({rsi_value:.1f})")
            elif rsi_value > rsi_overbought:
                flags.append(f"RSI sobrecomprado ({rsi_value:.1f})")

        if pd.notna(sma_short_value) and pd.notna(sma_long_value):
            if sma_short_value > sma_long_value:
                flags.append("Tendência de alta (SMA curta > SMA longa)")
            elif sma_short_value < sma_long_value:
                flags.append("Tendência de baixa (SMA curta < SMA longa)")

        rows.append(
            {
                "ticker": ticker,
                "preco": last_price,
                "rsi": rsi_value,
                "sma_curta": sma_short_value,
                "sma_longa": sma_long_value,
                "sinais": "; ".join(flags) if flags else "Sem sinal relevante",
            }
        )

    return pd.DataFrame(rows).set_index("ticker")
