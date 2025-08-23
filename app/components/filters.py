# app/components/filters.py
import streamlit as st
import pandas as pd

def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renderiza todos os filtros e ordenação na sidebar e retorna o DataFrame filtrado.
    """
    st.sidebar.header("🔎 Filtros de Análise")

    # --- Filtros Principais ---
    setores_disponiveis = sorted(df['Setor'].dropna().unique().tolist())
    setor_filtro = st.sidebar.multiselect("Setores", setores_disponiveis, default=setores_disponiveis)

    perfil_ordem = {'Penny Stock': 0, 'Micro Cap': 1, 'Small Cap': 2, 'Mid Cap': 3, 'Blue Chip': 4}
    perfis_raw = [p for p in df['Perfil da Ação'].dropna().unique().tolist()]
    perfis_disponiveis = sorted(perfis_raw, key=lambda x: (perfil_ordem.get(x, 999), x))
    perfil_filtro = st.sidebar.multiselect("Perfil da Ação", perfis_disponiveis, default=perfis_disponiveis)

    tickers_disponiveis = sorted(df['Ticker'].dropna().unique().tolist())
    ticker_foco_opt = ["— Todos —"] + tickers_disponiveis
    ticker_foco = st.sidebar.selectbox("Ticker em Foco (opcional)", ticker_foco_opt, index=0)
    ticker_foco = None if ticker_foco == "— Todos —" else ticker_foco

    # --- Filtros de Indicadores ---
    score_range = st.sidebar.slider("Faixa de Score", 0, 200, (100, 200))
    setor_score_min = st.sidebar.slider("Score Mínimo do Setor", 0, 100, 50)
    dy_min = st.sidebar.slider("DY 12 Meses Mínimo (%)", 0.0, 30.0, 0.0, 0.1)
    dy_5y_min = st.sidebar.slider("DY 5 Anos Mínimo (%)", 0.0, 20.0, 6.0, 0.1)

    # --- Lógica de Filtragem ---
    df_filtrado = df[
        (df['Setor'].isin(setor_filtro)) &
        (df['Perfil da Ação'].isin(perfil_filtro)) &
        (df['Score Total'].between(score_range[0], score_range[1])) &
        (df['DY (Taxa 12m, %)'] >= dy_min) &
        (df['DY 5 Anos Média (%)'] >= dy_5y_min) &
        (df['pontuacao'].fillna(0) >= setor_score_min)
    ].copy()

    if ticker_foco:
        df_filtrado = df_filtrado[df_filtrado['Ticker'] == ticker_foco]

    # --- Ordenação ---
    st.sidebar.header("📊 Ordenação")
    col_ordem = st.sidebar.selectbox(
        "Ordenar por",
        ['Score Total', 'DY 5 Anos Média (%)', 'DY (Taxa 12m, %)', 'Alvo', 'P/L', 'P/VP'],
        index=0
    )
    asc = st.sidebar.radio("Ordem", ["Decrescente", "Crescente"], index=0) == "Crescente"
    
    df_filtrado = df_filtrado.sort_values(by=col_ordem, ascending=asc)

    return df_filtrado
