"""Watchlist padrão compartilhada entre notebook, app Streamlit e scripts agendados."""

CRYPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
ACOES_BR = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA", "BBAS3.SA"]
FIIS_ETFS = ["MXRF11.SA", "HGLG11.SA", "IVVB11.SA", "BOVA11.SA"]
CAMBIO = ["USDBRL=X"]
INDICES = ["^BVSP", "^GSPC"]

WATCHLIST = CRYPTO + ACOES_BR + FIIS_ETFS + CAMBIO + INDICES

GRUPOS = {
    "Cripto": CRYPTO,
    "Ações BR": ACOES_BR,
    "FIIs / ETFs": FIIS_ETFS,
    "Câmbio": CAMBIO,
    "Índices": INDICES,
}
