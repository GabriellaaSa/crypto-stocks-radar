"""Crypto & Stocks Radar — app Streamlit.

Rodar com: streamlit run app.py
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from radar import alerts, backtest, data, forecast, indicators, portfolio
from radar.config import GRUPOS, WATCHLIST

st.set_page_config(page_title="Crypto & Stocks Radar", page_icon="📊", layout="wide")

st.title("📊 Crypto & Stocks Radar")
st.caption(
    "Painel pessoal de análise de cripto, ações e índices. "
    "⚠️ Educacional — não executa ordens e não é recomendação de investimento."
)


@st.cache_data(ttl=600, show_spinner="Baixando cotações...")
def carregar_historico(tickers: tuple[str, ...], period: str) -> pd.DataFrame:
    return data.fetch_history(list(tickers), period=period)


@st.cache_data(ttl=120, show_spinner="Buscando preços atuais...")
def carregar_cotacoes(tickers: tuple[str, ...]) -> pd.DataFrame:
    return data.fetch_quotes(list(tickers))


with st.sidebar:
    st.header("Watchlist")
    selecionados: list[str] = []
    for grupo, tickers in GRUPOS.items():
        escolha = st.multiselect(grupo, tickers, default=tickers)
        selecionados.extend(escolha)
    periodo = st.selectbox("Período de análise", ["6mo", "1y", "2y", "5y"], index=1)

if not selecionados:
    st.warning("Selecione pelo menos um ativo na barra lateral.")
    st.stop()

precos = carregar_historico(tuple(selecionados), periodo)
retornos = indicators.daily_returns(precos)

tab_monitor, tab_risco, tab_carteira, tab_backtest, tab_sinais, tab_previsao = st.tabs(
    ["💹 Monitor", "🔗 Correlação & Risco", "💼 Carteira", "🔁 Backtest", "🚨 Sinais", "🔮 Projeção"]
)

with tab_monitor:
    quotes = carregar_cotacoes(tuple(selecionados))
    st.dataframe(
        quotes.style.format(
            {"preco_atual": "{:,.2f}", "fechamento_anterior": "{:,.2f}", "variacao_%": "{:+.2f}%"},
            na_rep="—",
        ).background_gradient(subset=["variacao_%"], cmap="RdYlGn", vmin=-5, vmax=5),
        use_container_width=True,
    )

    ativo = st.selectbox("Gráfico detalhado", selecionados)
    serie = precos[ativo].dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=serie.index, y=serie, name=ativo, line=dict(width=2)))
    fig.add_trace(go.Scatter(x=serie.index, y=indicators.sma(serie, 20), name="SMA 20", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=serie.index, y=indicators.sma(serie, 50), name="SMA 50", line=dict(dash="dash")))
    fig.update_layout(template="plotly_white", height=450, title=f"{ativo} — preço e médias móveis")
    st.plotly_chart(fig, use_container_width=True)

with tab_risco:
    col1, col2 = st.columns(2)
    with col1:
        corr = indicators.correlation_matrix(retornos)
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                        title="Correlação entre retornos diários")
        fig.update_layout(height=520)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        vol = indicators.annualized_volatility(retornos).sort_values()
        fig = px.bar(vol, orientation="h", title="Volatilidade anualizada",
                     labels={"value": "Volatilidade", "index": "Ativo"})
        fig.update_layout(showlegend=False, height=520)
        st.plotly_chart(fig, use_container_width=True)

with tab_carteira:
    st.write("Defina os pesos (%) da carteira hipotética — só simulação histórica, nada é executado.")
    cols = st.columns(4)
    pesos = {}
    for i, ticker in enumerate(selecionados):
        with cols[i % 4]:
            pesos[ticker] = st.number_input(ticker, 0, 100, 0, step=5, key=f"peso_{ticker}")
    pesos = {t: p for t, p in pesos.items() if p > 0}

    if pesos:
        resultado = portfolio.simulate_portfolio(precos, pesos)
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Retorno total", f"{resultado['total_return']:+.1%}")
        m2.metric("Retorno anualizado", f"{resultado['annual_return']:+.1%}")
        m3.metric("Volatilidade", f"{resultado['annual_volatility']:.1%}")
        m4.metric("Sharpe (simplif.)", f"{resultado['sharpe_ratio']:.2f}")
        m5.metric("Máx. drawdown", f"{resultado['max_drawdown']:.1%}")

        fig = go.Figure(go.Scatter(x=resultado["portfolio_value"].index, y=resultado["portfolio_value"]))
        fig.update_layout(template="plotly_white", height=400, title="Evolução da carteira (base 1.0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Defina pelo menos um peso maior que zero.")

with tab_backtest:
    st.write("Compara **buy & hold** vs. **rebalanceamento periódico** para os pesos definidos na aba Carteira.")
    if not pesos:
        st.info("Defina os pesos na aba Carteira primeiro.")
    else:
        col1, col2 = st.columns(2)
        freq = col1.selectbox("Frequência de rebalanceamento", [("Mensal", "ME"), ("Trimestral", "QE")],
                              format_func=lambda x: x[0])[1]
        custo = col2.slider("Custo de transação (bps por trade)", 0, 100, 10)

        comparacao = backtest.compare_strategies(precos, pesos, freq=freq, cost_bps=custo)
        st.dataframe(comparacao.style.format("{:.2%}", na_rep="—"), use_container_width=True)

        bh = backtest.backtest_buy_and_hold(precos, pesos)["portfolio_value"]
        rb = backtest.backtest_rebalance(precos, pesos, freq=freq, cost_bps=custo)["portfolio_value"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bh.index, y=bh, name="Buy & Hold"))
        fig.add_trace(go.Scatter(x=rb.index, y=rb, name="Rebalanceada"))
        fig.update_layout(template="plotly_white", height=420, title="Buy & Hold vs. Rebalanceada (base 1.0)")
        st.plotly_chart(fig, use_container_width=True)

with tab_sinais:
    sinais = alerts.evaluate_signals(precos)
    st.dataframe(
        sinais.style.format({"preco": "{:,.2f}", "rsi": "{:.1f}", "sma_curta": "{:,.2f}", "sma_longa": "{:,.2f}"},
                            na_rep="—"),
        use_container_width=True,
    )
    st.caption("RSI < 30 = sobrevendido; RSI > 70 = sobrecomprado; tendência = SMA 20 vs. SMA 50. "
               "Pontos de atenção para investigar, não ordens de compra/venda.")

with tab_previsao:
    st.write(
        "**Projeção estatística** dos próximos passos: milhares de cenários simulados (Monte Carlo) "
        "a partir do comportamento histórico + score de momentum consolidando tendência, RSI e retornos recentes."
    )
    st.warning("Projeções assumem que o futuro se parece com o passado — o mercado não garante isso. "
               "Use como mapa de cenários, nunca como certeza.", icon="⚠️")

    st.subheader("Ranking de momentum")
    scores = forecast.momentum_scores(precos)
    st.dataframe(
        scores.style.format({"retorno_1m": "{:+.1%}", "retorno_3m": "{:+.1%}", "rsi": "{:.1f}"})
        .background_gradient(subset=["score_momentum"], cmap="RdYlGn", vmin=-100, vmax=100),
        use_container_width=True,
    )

    st.subheader("Cenários de preço (Monte Carlo)")
    col1, col2 = st.columns(2)
    ativo_prev = col1.selectbox("Ativo", selecionados, key="ativo_previsao")
    horizonte = col2.selectbox("Horizonte", [30, 60, 90], format_func=lambda d: f"{d} dias úteis")

    resumo = forecast.forecast_summary(precos[ativo_prev], horizon_days=horizonte)
    bands = resumo["bands"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Preço atual", f"{resumo['last_price']:,.2f}")
    c2.metric("Mediana projetada", f"{resumo['mediana_final']:,.2f}",
              f"{resumo['mediana_final'] / resumo['last_price'] - 1:+.1%}")
    c3.metric("Prob. de estar acima do preço atual", f"{resumo['prob_alta']:.0%}")
    c4.metric("Faixa 5%–95%", f"{resumo['pessimista_p5']:,.0f} – {resumo['otimista_p95']:,.0f}")

    historico_recente = precos[ativo_prev].dropna().tail(90)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=historico_recente.index, y=historico_recente, name="Histórico",
                             line=dict(color="#1f77b4", width=2)))
    fig.add_trace(go.Scatter(x=bands.index, y=bands[0.95], name="Otimista (p95)",
                             line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=bands.index, y=bands[0.05], name="Faixa 5%–95%",
                             fill="tonexty", fillcolor="rgba(31,119,180,0.15)", line=dict(width=0)))
    fig.add_trace(go.Scatter(x=bands.index, y=bands[0.75], name="p75", line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=bands.index, y=bands[0.25], name="Faixa 25%–75%",
                             fill="tonexty", fillcolor="rgba(31,119,180,0.30)", line=dict(width=0)))
    fig.add_trace(go.Scatter(x=bands.index, y=bands[0.50], name="Mediana",
                             line=dict(color="#ff7f0e", dash="dash")))
    fig.update_layout(template="plotly_white", height=480,
                      title=f"{ativo_prev} — cenários simulados para {horizonte} dias úteis")
    st.plotly_chart(fig, use_container_width=True)
