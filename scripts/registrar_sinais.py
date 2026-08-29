"""Roda diariamente (GitHub Actions ou local): registra sinais em CSV e, se
TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID estiverem configurados, envia um resumo.

Apenas informativo — nunca executa ordem nenhuma.
"""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from radar import alerts, data, forecast  # noqa: E402
from radar.config import WATCHLIST  # noqa: E402

CSV_PATH = ROOT / "data" / "sinais_historico.csv"


def registrar() -> pd.DataFrame:
    precos = data.fetch_history(WATCHLIST, period="6mo")
    sinais = alerts.evaluate_signals(precos).reset_index()
    sinais.insert(0, "data", date.today().isoformat())

    momentum = forecast.momentum_scores(precos)[["score_momentum", "leitura"]]
    sinais = sinais.merge(momentum, on="ticker", how="left")

    CSV_PATH.parent.mkdir(exist_ok=True)
    if CSV_PATH.exists():
        historico = pd.read_csv(CSV_PATH)
        historico = historico[historico["data"] != sinais["data"].iloc[0]]
        sinais = pd.concat([historico, sinais], ignore_index=True)
    sinais.to_csv(CSV_PATH, index=False)
    return sinais[sinais["data"] == date.today().isoformat()]


def enviar_telegram(hoje: pd.DataFrame) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram não configurado (TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID) — pulando envio.")
        return

    relevantes = hoje[hoje["sinais"].str.contains("RSI", na=False)]
    linhas = [f"📊 Radar {date.today():%d/%m} — sinais do dia\n"]
    if relevantes.empty:
        linhas.append("Nenhum ativo em zona de RSI extremo hoje. ✅")
    else:
        for _, row in relevantes.iterrows():
            linhas.append(f"• {row['ticker']}: {row['sinais']} (momentum {row['score_momentum']})")
    linhas.append("\n⚠️ Informativo/educacional — não é recomendação de investimento.")

    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": "\n".join(linhas)},
        timeout=30,
    )
    print("Telegram:", resp.status_code, resp.text[:200])


if __name__ == "__main__":
    hoje = registrar()
    print(f"{len(hoje)} sinais registrados em {CSV_PATH}")
    print(hoje[["ticker", "sinais", "score_momentum"]].to_string(index=False))
    enviar_telegram(hoje)
