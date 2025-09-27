# app/components/filters.py
import streamlit as st
import pandas as pd

def render_sidebar_filters(df: pd.DataFrame, indices_scores: dict, all_data: dict) -> tuple[pd.DataFrame, str | None]:
    """
    Renderiza todos os filtros e ordenação na sidebar e retorna o DataFrame filtrado.
    """
    st.sidebar.header("🔎 Filtros de Análise")

    # --- Lógica de Perfis ---
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
    perfis_recomendados = [p for p in perfis_disponiveis if p in ['Small Cap 2B–10B', 'Mid Cap 10B–50B', 'Blue Cap > 50B']]
    tickers_disponiveis = sorted(df['Ticker'].dropna().unique().tolist())
    ticker_foco_opt = ["— Todos —"] + tickers_disponiveis

    # --- Inicialização do Session State ---
    if 'filters_initialized' not in st.session_state:
        st.session_state.perfil_filtro = perfis_default
        st.session_state.score_range = (200, 1000)
        st.session_state.subsetor_score_min = 200
        st.session_state.dy_min = 6.0
        st.session_state.dy_5y_min = 6.0
        st.session_state.ticker_foco = "— Todos —"
        st.session_state.filters_initialized = True

    # --- Callbacks dos Botões ---
    def clear_filters():
        st.session_state.perfil_filtro = perfis_disponiveis
        st.session_state.score_range = (0, 1000)
        st.session_state.subsetor_score_min = 0
        st.session_state.dy_min = 0.0
        st.session_state.dy_5y_min = 0.0
        st.session_state.ticker_foco = "— Todos —"

    def recommend_filters():
        st.session_state.perfil_filtro = perfis_recomendados
        st.session_state.score_range = (200, 1000)
        st.session_state.subsetor_score_min = 200
        st.session_state.dy_min = 6.0
        st.session_state.dy_5y_min = 6.0
        st.session_state.ticker_foco = "— Todos —"

    # --- Renderização dos Widgets ---
    perfil_filtro = st.sidebar.multiselect("Perfil da Ação (Reais)", perfis_disponiveis, key='perfil_filtro')
    ticker_foco_val = st.sidebar.selectbox("Ticker em Foco (opcional)", ticker_foco_opt, key='ticker_foco')
    score_range = st.sidebar.slider("Faixa de Score", 0, 1000, value=(st.session_state.get('score_range', (0, 1000)) if isinstance(st.session_state.get('score_range', (0, 1000)), tuple) else (0, 1000)), key='score_range')
    subsetor_score_min = st.sidebar.slider("Pontuação Mínima do Setor", 0, 1000, key='subsetor_score_min')
    dy_min = st.sidebar.slider("DY 12 Meses Mínimo (%)", 0.0, 20.0, key='dy_min', step=0.1)
    dy_5y_min = st.sidebar.slider("DY 5 Anos Mínimo (%)", 0.0, 20.0, key='dy_5y_min', step=0.1)

    col1, col2 = st.sidebar.columns(2)
    col1.button("Limpar Filtros", on_click=clear_filters)
    col2.button("Filtros Recomendados", on_click=recommend_filters)

    # --- Lógica de Filtragem ---
    df_filtrado = df[
        (df['Perfil da Ação'].isin(perfil_filtro)) &
        (df['Pontuação'].between(score_range[0], score_range[1])) &
        (df['DY (Taxa 12m, %)'] >= dy_min) &
        (df['DY 5 Anos Média (%)'] >= dy_5y_min) &
        (df['pontuacao_final'].fillna(0) >= subsetor_score_min)
    ].copy()

    ticker_foco = None if ticker_foco_val == "— Todos —" else ticker_foco_val
    if ticker_foco:
        df_filtrado = df_filtrado[df_filtrado['Ticker'] == ticker_foco]

    df_filtrado = df_filtrado.sort_values(by='Pontuação', ascending=False)

    # --- Índices ---
    st.sidebar.header("📈 Índices")
    overall_score = df['Pontuação'].mean()
    st.sidebar.metric(label="Pontuação Geral do Mercado", value=f"{overall_score:.2f}", help="Média da pontuação de todas as ações (Máx: 1000)")

    sector_scores = all_data.get('avaliacao_setor', pd.DataFrame())
    if not sector_scores.empty and 'pontuacao_final' in sector_scores.columns:
        avg_sector_score = sector_scores['pontuacao_final'].mean()
        st.sidebar.metric(label="Pontuação Média dos Setores", value=f"{avg_sector_score:.2f}", help="Média da pontuação de todos os setores (Máx: 1000)")

    index_labels = {
        "iShares Ibovespa": "Ibovespa (BOVA11)",
        "Small Caps": "Small Caps (SMAL11)",
        "Financeiro (ETF)": "Financeiro (FIND11)",
        "Materiais Básicos (ETF)": "Materiais (MATB11)",
        "Dividendos": "Dividendos (DIVO11)"
    }

    for index_name, data in indices_scores.items():
        label = index_labels.get(index_name, index_name)
        score = data.get('score', float('nan'))
        delta = data.get('delta', float('nan'))
        
        if pd.notna(score):
            st.sidebar.metric(label=label, value=f"{score:.2f}", delta=f"{delta:.2f}% (1Y)" if pd.notna(delta) else None)

    return df_filtrado, ticker_foco