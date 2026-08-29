# 📊 Crypto & Stocks Radar

Painel analítico pessoal para acompanhar **criptomoedas, ações (B3/EUA) e índices** em um único notebook interativo: preços em tempo real, correlação e risco entre ativos, simulador de carteira e sinais técnicos.

> ⚠️ **Aviso importante:** ferramenta pessoal para fins educacionais e de análise. Ela **não executa ordens**, não se conecta a nenhuma corretora e **não constitui recomendação de investimento**. As decisões financeiras são de responsabilidade de quem usa o notebook.

## O que tem aqui

- **Monitor de preços em tempo real** — cotação atual, variação % e gráfico interativo (Plotly) com médias móveis, por ativo escolhido em um dropdown.
- **Correlação & risco** — heatmap de correlação entre retornos diários e volatilidade anualizada por ativo (útil pra enxergar diversificação de verdade).
- **Simulador de carteira** — sliders de peso (%) por ativo, mostrando retorno total, retorno anualizado, volatilidade, Sharpe simplificado e máximo drawdown com base em dados históricos reais. Nenhuma ordem é enviada — é só cálculo.
- **Alertas & sinais técnicos** — RSI (sobrecompra/sobrevenda) e cruzamento de médias móveis (20 vs 50 dias) por ativo, numa tabela destacada.

Os dados vêm do **Yahoo Finance** via [`yfinance`](https://github.com/ranaroussi/yfinance) — cobre cripto (`BTC-USD`, `ETH-USD`, ...), ações da B3 (`PETR4.SA`, `VALE3.SA`, ...), ações dos EUA (`AAPL`, ...) e índices (`^BVSP`, `^GSPC`), sem precisar de API key.

## Estrutura

```
crypto-stocks-radar/
├── crypto_stocks_radar.ipynb   # notebook principal (interativo)
├── radar/
│   ├── data.py                 # coleta de cotações e histórico
│   ├── indicators.py           # retornos, volatilidade, correlação, SMA, RSI
│   ├── portfolio.py            # simulador de carteira
│   └── alerts.py                # sinais técnicos
├── requirements.txt
└── README.md
```

## Como rodar

```bash
pip install -r requirements.txt
jupyter notebook crypto_stocks_radar.ipynb
```

Edite as listas `CRYPTO`, `ACOES_BR` e `INDICES` no notebook pra personalizar sua watchlist.

## Ideias de evolução

- Notificação via Telegram/e-mail quando um sinal disparar.
- Execução agendada (cron local ou GitHub Actions com `nbconvert --execute`) salvando o histórico de sinais em CSV, pra dar pra ver evolução ao longo do tempo.
- Mais classes de ativo (FIIs, ETFs, renda fixa via índices).
- Versão como app Streamlit pra rodar fora do Jupyter.
- Backtesting de uma estratégia simples de rebalanceamento periódico.

---
*Projeto pessoal de análise de mercado — não é recomendação de investimento.*
