# 📊 Crypto & Stocks Radar

Painel analítico pessoal para acompanhar **criptomoedas, ações (B3/EUA), FIIs, ETFs, câmbio e índices**: preços em tempo real, correlação e risco, simulador de carteira, backtest de estratégias, sinais técnicos com histórico diário automático e projeção estatística de cenários.

> ⚠️ **Aviso importante:** ferramenta pessoal para fins educacionais e de análise. Ela **não executa ordens**, não se conecta a nenhuma corretora e **não constitui recomendação de investimento**. As decisões financeiras são de responsabilidade de quem usa.

## O que tem aqui

| Módulo | O que faz |
|---|---|
| 💹 **Monitor** | Cotação atual, variação % e gráfico interativo com médias móveis (SMA 20/50) |
| 🔗 **Correlação & Risco** | Heatmap de correlação entre retornos diários + volatilidade anualizada por ativo |
| 💼 **Carteira** | Simulador com pesos por ativo: retorno, Sharpe, drawdown históricos (só cálculo, nada é executado) |
| 🔁 **Backtest** | Buy & hold vs. rebalanceamento periódico, com custo de transação simulado |
| 🚨 **Sinais** | RSI (sobrecompra/sobrevenda) + cruzamento de médias, com histórico diário em CSV |
| 🔮 **Projeção** | Monte Carlo (milhares de cenários futuros com bandas de probabilidade) + score de momentum (-100 a +100) |

Os dados vêm do **Yahoo Finance** via [`yfinance`](https://github.com/ranaroussi/yfinance) — sem precisar de API key. A watchlist padrão (cripto, ações B3, FIIs/ETFs, dólar, índices) fica em [`radar/config.py`](radar/config.py).

## Duas formas de usar

**Notebook interativo** (análise profunda, célula a célula):

```bash
pip install -r requirements.txt
jupyter notebook crypto_stocks_radar.ipynb
```

**App web** (Streamlit, com abas e filtros):

```bash
streamlit run app.py
```

## Automação diária (GitHub Actions)

O workflow [`sinais-diarios.yml`](.github/workflows/sinais-diarios.yml) roda todo dia às **18h (Brasília)**:

1. Calcula os sinais técnicos e o score de momentum de toda a watchlist;
2. Salva no histórico [`data/sinais_historico.csv`](data/sinais_historico.csv) (commit automático) — com o tempo vira uma série temporal dos alertas;
3. **Opcional:** manda um resumo no seu Telegram.

### Ativar o alerta no Telegram

1. Crie um bot com o [@BotFather](https://t.me/BotFather) e copie o token;
2. Descubra seu chat id (mande uma mensagem pro bot e acesse `https://api.telegram.org/bot<TOKEN>/getUpdates`);
3. No repositório do GitHub: *Settings → Secrets and variables → Actions* e crie os secrets `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`.

Sem os secrets, o workflow só registra o CSV (também funciona).

## Estrutura

```
crypto-stocks-radar/
├── crypto_stocks_radar.ipynb   # notebook principal (interativo)
├── app.py                      # app Streamlit (6 abas)
├── radar/
│   ├── config.py               # watchlist compartilhada
│   ├── data.py                 # coleta de cotações e histórico
│   ├── indicators.py           # retornos, volatilidade, correlação, SMA, RSI
│   ├── portfolio.py            # simulador de carteira
│   ├── backtest.py             # buy & hold vs. rebalanceamento
│   ├── alerts.py               # sinais técnicos
│   └── forecast.py             # Monte Carlo + score de momentum
├── scripts/registrar_sinais.py # roda diariamente via Actions
├── .github/workflows/sinais-diarios.yml
├── data/sinais_historico.csv   # histórico de sinais (auto-atualizado)
└── requirements.txt
```

## Sobre a aba Projeção 🔮

- **Monte Carlo (GBM):** estima drift e volatilidade do último ano de retornos e simula 2.000 trajetórias futuras de preço, gerando bandas de percentil (5%–95% e 25%–75%), mediana projetada e probabilidade do preço terminar acima do nível atual no horizonte escolhido (30/60/90 dias úteis).
- **Score de momentum:** consolida tendência (preço vs. SMA 50, SMA 20 vs. SMA 50), RSI e retornos de 1/3 meses num único número por ativo, de -100 (baixa forte) a +100 (alta forte).

Ambos assumem que o futuro se parece estatisticamente com o passado — o que o mercado **não garante**. Use como mapa de cenários, nunca como certeza.

---
*Projeto pessoal de análise de mercado — não é recomendação de investimento.*
