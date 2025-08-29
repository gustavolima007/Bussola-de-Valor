import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# Lista de ações brasileiras
tickers = {
    "VALE3": "VALE3.SA",
    "PETR4": "PETR4.SA",
    "TAEE4": "TAEE4.SA"
}

# Função para classificar os indicadores
def classificar(valor, lim_baixo, lim_alto):
    valor = float(valor)  # Garante que seja escalar
    if valor < lim_baixo:
        return "🔻 Baixo"
    elif valor > lim_alto:
        return "🔺 Alto"
    else:
        return "⚖️ Médio"

# Função para analisar os indicadores
def analisar_indicadores(df):
    close = df['Close'].dropna()
    volume = df['Volume'].dropna()

    # Garantir que 'close' seja uma Series 1D
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    # Calcular indicadores
    rsi = ta.momentum.RSIIndicator(close=close).rsi()
    macd = ta.trend.MACD(close=close).macd_diff()
    vol_mean = float(volume.mean())

    # Últimos valores convertidos para escalares
    rsi_val = float(rsi.iloc[-1])
    macd_val = float(macd.iloc[-1])
    vol_val = float(volume.iloc[-1])

    # Classificações
    rsi_status = classificar(rsi_val, 30, 70)
    macd_status = classificar(macd_val, -0.5, 0.5)
    vol_status = classificar(vol_val, vol_mean * 0.8, vol_mean * 1.2)

    return {
        "RSI": (rsi_val, rsi_status),
        "MACD Dif": (macd_val, macd_status),
        "Volume": (vol_val, vol_status)
    }

# Streamlit UI
st.set_page_config(page_title="Indicadores Técnicos", layout="wide")
st.title("📊 Indicadores Técnicos Simplificados")
st.subheader("VALE3, PETR4, TAEE4 — com classificação de força")

periodo = st.selectbox("Selecione o período", ["3mo", "6mo", "1y"], index=1)

for nome, ticker in tickers.items():
    df = yf.download(ticker, period=periodo)

    if not df.empty:
        try:
            indicadores = analisar_indicadores(df)
            st.markdown(f"### {nome}")
            for nome_indicador, (valor, status) in indicadores.items():
                st.write(f"**{nome_indicador}:** {valor:.2f} → {status}")
            st.markdown("---")
        except Exception as e:
            st.error(f"Erro ao analisar {nome}: {e}")
    else:
        st.error(f"Não foi possível obter dados para {nome}.")
