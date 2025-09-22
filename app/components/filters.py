# app/components/filters.py
import streamlit as st
import pandas as pd

def render_sidebar_filters(df: pd.DataFrame, indices_scores: dict) -> tuple[pd.DataFrame, str | None]:
    """
    Renderiza todos os filtros e ordenação na sidebar e retorna o DataFrame filtrado.
    """
    st.sidebar.header("🔎 Filtros de Análise")

    # --- Filtros Principais ---
    # Normaliza os rótulos do perfil para os nomes desejados no UI
    rename_map = {
        'Penny Stock': 'Penny Stock < 1R$',
        'Micro Cap': 'Micro Cap  < 2B',
        'Small Cap': 'Small Cap 2B–10B',
        'Mid Cap': 'Mid Cap 10B–50B',
        'Blue Chip': 'Blue Cap > 50B',
    }
    if 'Perfil da Ação' in df.columns:
        df['Perfil da Ação'] = df['Perfil da Ação'].replace(rename_map)
    perfil_ordem = {
        'Penny Stock < 1R$': 0,
        'Micro Cap  < 2B': 1,
        'Small Cap 2B–10B': 2,
        'Mid Cap 10B–50B': 3,
        'Blue Cap > 50B': 4
    }
    perfis_raw = [p for p in df['Perfil da Ação'].dropna().unique().tolist()]
    perfis_disponiveis = sorted(perfis_raw, key=lambda x: (perfil_ordem.get(x, 999), x))
    perfis_default = [p for p in perfis_disponiveis if p not in ['Penny Stock < 1R$', 'Micro Cap  < 2B']]
    perfil_filtro = st.sidebar.multiselect("Perfil da Ação (Reais)", perfis_disponiveis, default=perfis_default)

    tickers_disponiveis = sorted(df['Ticker'].dropna().unique().tolist())
    ticker_foco_opt = ["— Todos —"] + tickers_disponiveis
    ticker_foco = st.sidebar.selectbox("Ticker em Foco (opcional)", ticker_foco_opt, index=0)
    ticker_foco = None if ticker_foco == "— Todos —" else ticker_foco

    # --- Filtros de Indicadores ---
    score_range = st.sidebar.slider("Faixa de Score", 0, 200, (100, 200))
    subsetor_score_min = st.sidebar.slider("Pontuação Mínima do Setor", 0, 100, 60)
    dy_min = st.sidebar.slider("DY 12 Meses Mínimo (%)", 0.0, 30.0, 6.0, 0.1)
    dy_5y_min = st.sidebar.slider("DY 5 Anos Mínimo (%)", 0.0, 20.0, 6.0, 0.1)

    # --- Lógica de Filtragem ---
    df_filtrado = df[
        (df['Perfil da Ação'].isin(perfil_filtro)) &
        (df['Score Total'].between(score_range[0], score_range[1])) &
        (df['DY (Taxa 12m, %)'] >= dy_min) &
        (df['DY 5 Anos Média (%)'] >= dy_5y_min) &
        (df['pontuacao_subsetor'].fillna(0) >= subsetor_score_min)
    ].copy()

    if ticker_foco:
        df_filtrado = df_filtrado[df_filtrado['Ticker'] == ticker_foco]

    # Ordenação padrão por Score Total
    df_filtrado = df_filtrado.sort_values(by='Score Total', ascending=False)

    # --- Índices ---
    st.sidebar.header("📈 Índices")
    
    index_labels = {
        "iShares Ibovespa": "iShares Ibovespa BOVA11",
        "Small Caps": "Small Caps SMAL11",
        "Financeiro (ETF)": "Financeiro FIND11",
        "Materiais Básicos (ETF)": "Materiais Básicos MATB11",
        "Dividendos": "Dividendos DIVO11"
    }

    for index_name, data in indices_scores.items():
        label = index_labels.get(index_name, index_name)
        score = data.get('score', float('nan'))
        delta = data.get('delta', float('nan'))
        
        if pd.notna(score):
            st.sidebar.metric(label=label, value=f"{score:.2f}", delta=f"{delta:.2f}% (1Y)" if pd.notna(delta) else None)

    return df_filtrado, ticker_foco