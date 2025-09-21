# streamlit_app.py
# Requisitos:
#   pip install streamlit yfinance ta pandas numpy

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from ta.volume import (
    OnBalanceVolumeIndicator,
    ChaikinMoneyFlowIndicator,
    AccDistIndexIndicator,
)

# ------------------ Função para calcular MFI manualmente ------------------
def money_flow_index(high, low, close, volume, window: int = 14) -> pd.Series:
    tp = (high + low + close) / 3
    mf = tp * volume

    positive_mf = pd.Series(0.0, index=tp.index)
    negative_mf = pd.Series(0.0, index=tp.index)

    positive_mf[1:] = np.where(tp[1:] > tp.shift(1)[1:], mf[1:], 0.0)
    negative_mf[1:] = np.where(tp[1:] < tp.shift(1)[1:], mf[1:], 0.0)

    pos_mf_sum = positive_mf.rolling(window=window, min_periods=window).sum()
    neg_mf_sum = negative_mf.rolling(window=window, min_periods=window).sum()

    mfi = 100 - (100 / (1 + (pos_mf_sum / neg_mf_sum.replace(0, np.nan))))
    return mfi

# ------------------ Configuração da página ------------------
st.set_page_config(page_title="Fluxo, Liquidez e Convicção (OBV, CMF, ADI, MFI)", layout="wide")
st.title("📊 Fluxo, Liquidez e Convicção — OBV • CMF • ADI • MFI")

# ------------------ Tickers ------------------
TICKERS = {
    "TAEE4": "TAEE4.SA",
    "VALE3": "VALE3.SA",
    "PETR4": "PETR4.SA",
}

with st.sidebar:
    st.header("⚙️ Parâmetros")
    janela_cmf = st.number_input("Janela CMF (dias)", min_value=10, max_value=60, value=20, step=1)
    janela_mfi = st.number_input("Janela MFI (dias)", min_value=10, max_value=60, value=14, step=1)
    janela_tend = st.number_input("Olhar tendência (Δ períodos) p/ OBV/ADI", min_value=5, max_value=60, value=20, step=1)
    ativos_escolhidos = st.multiselect("Ativos", list(TICKERS.keys()), default=list(TICKERS.keys()))
    mostrar_graficos = st.checkbox("Mostrar gráficos por indicador", value=True)
    st.caption("Dica: CMF > 0 indica fluxo comprador; MFI < 20 sobrevendido, > 80 sobrecomprado.")

# ------------------ Download blindado ------------------
@st.cache_data(show_spinner=False, ttl=60 * 60)
def baixar_df(symbol: str) -> pd.DataFrame:
    df = yf.download(symbol, period="1y", interval="1d", auto_adjust=True, progress=False)

    # Garante que as colunas existam
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in df.columns:
            df[col] = np.nan

    return df.dropna(subset=["High", "Low", "Close", "Volume"])

# ------------------ Cálculo dos indicadores ------------------
def calcular_indicadores(df: pd.DataFrame, win_cmf=20, win_mfi=14) -> pd.DataFrame:
    out = df.copy()
    out["OBV"] = OnBalanceVolumeIndicator(close=out["Close"], volume=out["Volume"]).on_balance_volume()
    out["CMF"] = ChaikinMoneyFlowIndicator(
        high=out["High"], low=out["Low"], close=out["Close"], volume=out["Volume"], window=win_cmf
    ).chaikin_money_flow()
    out["ADI"] = AccDistIndexIndicator(
        high=out["High"], low=out["Low"], close=out["Close"], volume=out["Volume"]
    ).acc_dist_index()
    out["MFI"] = money_flow_index(out["High"], out["Low"], out["Close"], out["Volume"], window=win_mfi)
    return out

# ------------------ Classificadores ------------------
def classificar_cmf(val: float) -> str:
    if pd.isna(val): return "—"
    if val > 0.05: return "🏦 Influxo"
    if val < -0.05: return "🪙 Saída"
    return "💰 Neutro"

def classificar_mfi(val: float) -> str:
    if pd.isna(val): return "—"
    if val < 20: return "📉 Sobrevendido"
    if val > 80: return "📈 Sobrecomprado"
    return "📊 Neutro"

def classificar_tendencia(series: pd.Series, lookback: int) -> str:
    if series is None or series.empty or len(series.dropna()) < lookback + 1: return "—"
    delta = series.iloc[-1] - series.iloc[-1 - lookback]
    if delta > 0: return "🐂 Alta"
    if delta < 0: return "🐻 Baixa"
    return "⚖️ Lateral"

# ------------------ Loop principal ------------------
tabelao = []

for nome, yf_ticker in {k: TICKERS[k] for k in ativos_escolhidos}.items():
    df = baixar_df(yf_ticker)
    if df.empty:
        st.error(f"Sem dados para {nome} ({yf_ticker}).")
        continue

    df_ind = calcular_indicadores(df, win_cmf=janela_cmf, win_mfi=janela_mfi)
    ult = df_ind.iloc[-1]

    # Resumos + classificações
    cmf_val = float(ult["CMF"]) if pd.notna(ult["CMF"]) else np.nan
    mfi_val = float(ult["MFI"]) if pd.notna(ult["MFI"]) else np.nan
    obv_tend = classificar_tendencia(df_ind["OBV"], janela_tend)
    adi_tend = classificar_tendencia(df_ind["ADI"], janela_tend)

    cmf_cls = classificar_cmf(cmf_val)
    mfi_cls = classificar_mfi(mfi_val)

    # Bloco visual por ativo
    st.subheader(f"📌 {nome}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CMF (fluxo, "+str(janela_cmf)+"d)", f"{cmf_val:,.3f}" if pd.notna(cmf_val) else "—")
    col2.metric("MFI (força, "+str(janela_mfi)+"d)", f"{mfi_val:,.1f}" if pd.notna(mfi_val) else "—")
    col3.metric("OBV — tendência", obv_tend)
    col4.metric("ADI — tendência", adi_tend)

    st.caption(f"**Classificações rápidas** → CMF: {cmf_cls} • MFI: {mfi_cls}")

    if mostrar_graficos:
        g1, g2 = st.columns(2)
        with g1:
            st.line_chart(df_ind[["CMF"]], height=220)
            st.caption("CMF (fluxo de dinheiro)")
            st.line_chart(df_ind[["MFI"]], height=220)
            st.caption("MFI (money flow index)")
        with g2:
            st.line_chart(df_ind[["OBV"]], height=220)
            st.caption("OBV (on-balance volume)")
            st.line_chart(df_ind[["ADI"]], height=220)
            st.caption("ADI (accumulation/distribution index)")

    # Adiciona ao consolidado
    tabelao.append({
        "Ativo": nome,
        "CMF": round(cmf_val, 3) if pd.notna(cmf_val) else np.nan,
        "CMF • Classificação": cmf_cls,
        "MFI": round(mfi_val, 1) if pd.notna(mfi_val) else np.nan,
        "MFI • Classificação": mfi_cls,
        f"OBV Δ{janela_tend}": float(df_ind["OBV"].iloc[-1] - df_ind["OBV"].iloc[-1 - janela_tend]) if len(df_ind) > janela_tend else np.nan,
        f"ADI Δ{janela_tend}": float(df_ind["ADI"].iloc[-1] - df_ind["ADI"].iloc[-1 - janela_tend]) if len(df_ind) > janela_tend else np.nan,
    })

st.divider()

# ------------------ Consolidado ------------------
if tabelao:
    st.subheader("📋 Consolidado — Fluxo/Liquidez por Ativo")
    df_consol = pd.DataFrame(tabelao)
    st.dataframe(df_consol, use_container_width=True)
else:
    st.info("Selecione ao menos um ativo na barra lateral.")
