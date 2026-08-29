"""Coleta de cotações via Yahoo Finance (yfinance) — cripto, ações B3/US e índices."""
from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_history(tickers: list[str], period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Baixa o histórico de fechamento ajustado para uma lista de tickers.

    Retorna um DataFrame com uma coluna por ticker.
    """
    raw = yf.download(
        tickers,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        group_by="column",
    )

    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        close = raw[["Close"]].rename(columns={"Close": tickers[0]})

    return close.dropna(how="all")


def fetch_quotes(tickers: list[str]) -> pd.DataFrame:
    """Retorna preço atual, fechamento anterior e variação % para cada ticker."""
    rows = []
    for ticker in tickers:
        info = yf.Ticker(ticker).fast_info
        last = info.get("lastPrice")
        prev = info.get("previousClose")
        change_pct = (last / prev - 1) * 100 if last and prev else None
        rows.append(
            {
                "ticker": ticker,
                "preco_atual": last,
                "fechamento_anterior": prev,
                "variacao_%": change_pct,
                "moeda": info.get("currency"),
            }
        )
    return pd.DataFrame(rows).set_index("ticker")
