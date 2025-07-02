# app.py (Versão com Filtro de Perfil da Ação)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Investidor Inteligente - Análise de Ações", layout="wide", page_icon="📈")

# --- FUNÇÕES CORE ---
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """
    Carrega os dados do CSV e força a conversão de todas as colunas numéricas.
    """
    try:
        df = pd.read_csv(path, index_col=0)

        numeric_cols = [
            'Preço Atual', 'P/L', 'P/VP', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)',
            'Payout Ratio (%)', 'Crescimento Preço (%)', 'ROE (%)', 'Dívida Total',
            'Market Cap', 'Dívida/EBITDA', 'Sentimento Gauge', 'Strong Buy', 'Buy',
            'Hold', 'Sell', 'Strong Sell'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        for col in ["Data Últ. Div.", "Data Ex-Div."]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        df['Ticker'] = df.index.str.replace('.SA', '')
        return df
    except FileNotFoundError:
        st.error(f"Arquivo '{path}' não encontrado. Por favor, execute o script 'transform.py' primeiro.")
        return pd.DataFrame()

def calculate_score_and_details(row: pd.Series) -> tuple[float, list[str]]:
    """
    Função centralizada que calcula o Score e retorna as justificativas.
    """
    score = 0
    details = []

    # Critério: Dividend Yield (12 meses)
    dy_12m = row['DY (Taxa 12m, %)']
    if dy_12m > 5: score += 20; details.append(f"DY 12m ({dy_12m:.1f}%) > 5%: **+20**")
    elif dy_12m > 3.5: score += 15; details.append(f"DY 12m ({dy_12m:.1f}%) > 3.5%: **+15**")
    elif dy_12m > 2: score += 10; details.append(f"DY 12m ({dy_12m:.1f}%) > 2%: **+10**")
    elif dy_12m < 2 and dy_12m > 0: score -= 5; details.append(f"DY 12m ({dy_12m:.1f}%) < 2%: **-5**")

    # Critério: Dividend Yield (Média 5 anos)
    dy_5y = row['DY 5 Anos Média (%)']
    if dy_5y > 8: score += 25; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 8%: **+25**")
    elif dy_5y > 6: score += 20; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 6%: **+20**")
    elif dy_5y > 4: score += 10; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 4%: **+10**")

    # Critério: Payout Ratio
    payout = row['Payout Ratio (%)']
    if 30 <= payout <= 60: score += 10; details.append(f"Payout ({payout:.0f}%) entre 30-60%: **+10**")
    elif 60 < payout <= 80: score += 5; details.append(f"Payout ({payout:.0f}%) entre 60-80%: **+5**")
    elif (payout > 0 and payout < 20) or payout > 80: score -= 5; details.append(f"Payout ({payout:.0f}%) fora de 20-80%: **-5**")
    
    # Critério: ROE (Return on Equity)
    roe = row['ROE (%)']
    setor = row.get('Setor (brapi)', '').lower()
    if 'finance' in setor:
        if roe > 15: score += 25; details.append(f"ROE (Financeiro) ({roe:.1f}%) > 15%: **+25**")
        elif roe > 12: score += 20; details.append(f"ROE (Financeiro) ({roe:.1f}%) > 12%: **+20**")
        elif roe > 8: score += 10; details.append(f"ROE (Financeiro) ({roe:.1f}%) > 8%: **+10**")
    else:
        if roe > 12: score += 15; details.append(f"ROE ({roe:.1f}%) > 12%: **+15**")
        elif roe > 8: score += 5; details.append(f"ROE ({roe:.1f}%) > 8%: **+5**")

    # Critério: P/L e P/VP
    pl = row['P/L']
    if 0 < pl < 12: score += 15; details.append(f"P/L ({pl:.2f}) < 12: **+15**")
    elif 12 <= pl < 18: score += 10; details.append(f"P/L ({pl:.2f}) < 18: **+10**")
    elif pl > 25: score -= 5; details.append(f"P/L ({pl:.2f}) > 25: **-5**")

    pvp = row['P/VP']
    if 0 < pvp < 0.66: score += 20; details.append(f"P/VP ({pvp:.2f}) < 0.66: **+20**")
    elif 0.66 <= pvp < 1.5: score += 10; details.append(f"P/VP ({pvp:.2f}) < 1.5: **+10**")
    elif 1.5 <= pvp < 2.5: score += 5; details.append(f"P/VP ({pvp:.2f}) < 2.5: **+5**")
    elif pvp > 4: score -= 5; details.append(f"P/VP ({pvp:.2f}) > 4: **-5**")

    # Critérios de Dívida (Apenas para não-financeiros)
    if 'finance' not in setor:
        if row['Market Cap'] > 0:
            debt_mc = row['Dívida Total'] / row['Market Cap']
            if debt_mc < 0.5: score += 10; details.append(f"Dívida/Market Cap ({debt_mc:.2f}) < 0.5: **+10**")
            elif debt_mc < 1.0: score += 5; details.append(f"Dívida/Market Cap ({debt_mc:.2f}) < 1.0: **+5**")
            elif debt_mc > 2.0: score -= 5; details.append(f"Dívida/Market Cap ({debt_mc:.2f}) > 2.0: **-5**")
        div_ebitda = row['Dívida/EBITDA']
        if div_ebitda > 0:
            if div_ebitda < 1: score += 10; details.append(f"Dívida/EBITDA ({div_ebitda:.2f}) < 1: **+10**")
            elif div_ebitda < 2: score += 5; details.append(f"Dívida/EBITDA ({div_ebitda:.2f}) < 2: **+5**")
            elif div_ebitda > 6: score -= 5; details.append(f"Dívida/EBITDA ({div_ebitda:.2f}) > 6: **-5**")

    # Critério: Crescimento do Preço (5 Anos)
    growth = row['Crescimento Preço (%)']
    if growth > 15: score += 15; details.append(f"Crescimento 5A ({growth:.1f}%) > 15%: **+15**")
    elif growth > 10: score += 10; details.append(f"Crescimento 5A ({growth:.1f}%) > 10%: **+10**")
    elif growth > 5: score += 5; details.append(f"Crescimento 5A ({growth:.1f}%) > 5%: **+5**")
    elif growth < 0: score -= 5; details.append(f"Crescimento 5A ({growth:.1f}%) < 0%: **-5**")

    # Critério: Sentimento de Mercado
    sentiment_gauge = row['Sentimento Gauge']
    sentiment_score = 0
    if sentiment_gauge >= 50:
        sentiment_score = ((sentiment_gauge - 50) / 50) * 10
        details.append(f"Sentimento ({sentiment_gauge:.0f}/100) Positivo: **+{sentiment_score:.1f}**")
    else:
        sentiment_score = ((sentiment_gauge - 50) / 50) * 5
        details.append(f"Sentimento ({sentiment_gauge:.0f}/100) Negativo: **{sentiment_score:.1f}**")
    score += sentiment_score

    return max(0, min(200, score)), details

# --- CARREGAMENTO E PROCESSAMENTO DOS DADOS ---
df = load_data(r"E:\Github\finance-manager\data\relatorio_analise_b3.csv")

if not df.empty:
    # Garante que a coluna 'Perfil da Ação' exista, mesmo que o CSV seja antigo
    if 'Perfil da Ação' not in df.columns:
        df['Perfil da Ação'] = 'N/A'
        
    score_results = df.apply(calculate_score_and_details, axis=1)
    df['Score Total'] = score_results.apply(lambda x: x[0])
    df['Score Details'] = score_results.apply(lambda x: x[1])

    # --- UI: TÍTULO E SIDEBAR ---
    st.title("📈 Investidor Inteligente")
    st.markdown("Plataforma de análise e ranking de ações baseada nos princípios de **Barsi, Bazin, Buffett, Lynch e Graham**.")

    st.sidebar.header("Filtros de Análise")
    setores_disponiveis = sorted(df['Setor (brapi)'].dropna().unique().tolist())
    setor_filtro = st.sidebar.multiselect("Setores", setores_disponiveis, default=setores_disponiveis)
    
    # ### MUDANÇA 1: Adiciona o filtro de Perfil da Ação ###
    perfis_disponiveis = sorted(df['Perfil da Ação'].dropna().unique().tolist())
    perfil_filtro = st.sidebar.multiselect("Perfil da Ação", perfis_disponiveis, default=perfis_disponiveis)
    
    score_min_val = int(df['Score Total'].min())
    score_range = st.sidebar.slider("Faixa de Score", min_value=0, max_value=200, value=(100, 200))
    
    dy_min = st.sidebar.slider("DY 12 Meses Mínimo (%)", 0.0, 30.0, 3.5, 0.1)
    dy_5y_min = st.sidebar.slider("DY 5 Anos Mínimo (%)", 0.0, 20.0, 4.0, 0.1)

    # --- FILTRAGEM E ORDENAÇÃO ---
    df_filtrado = df[
        (df['Setor (brapi)'].isin(setor_filtro)) &
        (df['Perfil da Ação'].isin(perfil_filtro)) & # Adiciona o novo filtro à lógica
        (df['Score Total'].between(score_range[0], score_range[1])) &
        (df['DY (Taxa 12m, %)'] >= dy_min) &
        (df['DY 5 Anos Média (%)'] >= dy_5y_min)
    ].copy()
    
    st.sidebar.header("Ordenação")
    col_ordem = st.sidebar.selectbox("Ordenar por", ['Score Total', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'P/L', 'P/VP'], index=0)
    asc = st.sidebar.radio("Ordem", ["Crescente", "Decrescente"], index=1) == "Crescente"
    df_filtrado.sort_values(by=col_ordem, ascending=asc, inplace=True)

    # --- UI: ABAS DE EXIBIÇÃO ---
    tab1, tab2, tab3 = st.tabs(["📊 Ranking Geral", "🔍 Análise Detalhada", "📜 Critérios do Score"])

    with tab1:
        st.header(f"Ranking de Ações ({len(df_filtrado)} encontradas)")
        # ### MUDANÇA 2: Adiciona a coluna 'Perfil da Ação' ao DataFrame de exibição ###
        df_display = df_filtrado[['Logo', 'Ticker', 'Empresa', 'Setor (brapi)', 'Perfil da Ação', 'Preço Atual', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'P/L', 'P/VP', 'Score Total']]
        st.dataframe(df_display, column_config={
            "Logo": st.column_config.ImageColumn("Logo"), "Ticker": st.column_config.TextColumn("Ticker"),
            "Empresa": st.column_config.TextColumn("Empresa"), "Setor (brapi)": st.column_config.TextColumn("Setor"),
            "Perfil da Ação": st.column_config.TextColumn("Perfil"), # Configuração para a nova coluna
            "Preço Atual": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
            "DY (Taxa 12m, %)": st.column_config.NumberColumn("DY 12m", format="%.2f%%"),
            "DY 5 Anos Média (%)": st.column_config.NumberColumn("DY 5 Anos", format="%.2f%%"),
            "P/L": st.column_config.NumberColumn("P/L", format="%.2f"), "P/VP": st.column_config.NumberColumn("P/VP", format="%.2f"),
            "Score Total": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=200)},
            use_container_width=True, hide_index=True)

    with tab2:
        st.header("Análise Detalhada e Composição do Score")
        if not df_filtrado.empty:
            ticker_selecionado = st.selectbox("Selecione a Ação", df_filtrado['Ticker'].tolist(),
                format_func=lambda t: f"{t} - {df_filtrado.loc[df_filtrado['Ticker'] == t, 'Empresa'].iloc[0]}")
            if ticker_selecionado:
                acao = df_filtrado[df_filtrado['Ticker'] == ticker_selecionado].iloc[0]
                # ### MUDANÇA 3: Adiciona a métrica de 'Perfil da Ação' ###
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Preço Atual", f"R$ {acao['Preço Atual']:.2f}")
                c2.metric("P/L", f"{acao['P/L']:.2f}")
                c3.metric("P/VP", f"{acao['P/VP']:.2f}")
                c4.metric("DY 12m", f"{acao['DY (Taxa 12m, %)']:.2f}%")
                c5.metric("Perfil", acao['Perfil da Ação'])

                c1, c2 = st.columns([1, 1])
                with c1:
                    st.subheader("Composição do Score")
                    st.metric("Score Total", f"{acao['Score Total']:.0f} / 200")
                    for detail in acao['Score Details']:
                        st.markdown(f"- {detail}")
                with c2:
                    st.subheader("Sentimento dos Analistas")
                    recommendation_cols = ['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']
                    if all(col in acao.index for col in recommendation_cols):
                        rec_data = acao[recommendation_cols]
                        if rec_data.sum() > 0:
                            rec_df = pd.DataFrame(rec_data).reset_index()
                            rec_df.columns = ['Recomendação', 'Contagem']
                            fig_bar = px.bar(rec_df, x='Contagem', y='Recomendação', orientation='h',
                                             title='Distribuição das Recomendações', text='Contagem',
                                             color='Recomendação',
                                             color_discrete_map={
                                                 'Strong Buy': 'green', 'Buy': 'lightgreen', 'Hold': 'gold',
                                                 'Sell': 'orange', 'Strong Sell': 'red'
                                             })
                            fig_bar.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
                            st.plotly_chart(fig_bar, use_container_width=True)
                        else:
                            st.info("Não há recomendações de analistas disponíveis para este ativo.")
                    else:
                        st.warning("Dados de recomendação não encontrados. Execute a versão mais recente do `transform.py` para gerar o arquivo de dados completo.")
        else:
            st.info("Nenhuma ação encontrada com os filtros atuais.")

    with tab3:
        st.header("Critérios de Investimento")
        st.markdown("""
        ### Filosofia de Investimento
        Baseado nas estratégias de Luiz Barsi, Décio Bazin, Warren Buffett, Peter Lynch e Benjamin Graham, o **Investidor Inteligente** prioriza empresas com fundamentos sólidos, dividendos consistentes e valor intrínseco. A pontuação (0-200) reflete os seguintes critérios:

        - **Dividend Yield (12 meses)**: Avalia o retorno anual por dividendos em relação ao preço atual. Níveis altos indicam renda passiva atrativa.
          - > 5%: **+20**
          - 3.5% a 5%: **+15**
          - 2% a 3.5%: **+10**
          - < 2%: **-5**
        - **Dividend Yield (5 anos média)**: Analisa a consistência histórica de dividendos.
          - > 8%: **+25**
          - 6% a 8%: **+20**
          - 4% a 6%: **+10**
        - **Payout Ratio**: Mede a proporção de lucros distribuída como dividendos, buscando equilíbrio.
          - 30% a 60%: **+10**
          - 60% a 80%: **+5**
          - < 20% ou > 80%: **-5**
        - **ROE (Return on Equity)**: Avalia a eficiência no uso do capital próprio, com ajustes para o setor financeiro.
          - Financeiro: > 15%: **+25**, 12% a 15%: **+20**, 8% a 12%: **+10**
          - Outros: > 12%: **+15**, 8% a 12%: **+5**
        - **P/L (Price to Earnings)**: Indica se a ação está sub ou sobrevalorizada.
          - < 12: **+15**
          - 12 a 18: **+10**
          - > 25: **-5**
        - **P/VP (Price to Book Value)**: Reflete o valor em relação ao patrimônio líquido.
          - < 0.66: **+20**
          - 0.66 a 1.5: **+10**
          - 1.5 a 2.5: **+5**
          - > 4: **-5**
        - **Dívida/Market Cap** (exceto Financeiro): Avalia o endividamento relativo.
          - < 0.5: **+10**
          - 0.5 a 1.0: **+5**
          - > 2.0: **-5**
        - **Dívida/EBITDA** (exceto Financeiro): Mede a capacidade de pagamento da dívida.
          - < 1: **+10**
          - 1 a 2: **+5**
          - > 6: **-5**
        - **Crescimento Preço (%)**: Avalia o crescimento histórico do preço ao longo de 5 anos.
          - > 15%: **+15**
          - 10% a 15%: **+10**
          - 5% a 10%: **+5**
          - < 0%: **-5**
        - **Sentimento do Mercado**: Baseado em recomendações de analistas (0-100, normalizado para 0-10).
          - > 50: **+ (0 a 10)** (proporcional ao sentimento)
          - < 50: **- (0 a -5)** (proporcional ao sentimento)

        Esses critérios buscam empresas com valuation atrativo, estabilidade financeira e potencial de crescimento, ideais para uma carteira de longo prazo com foco em dividendos.
        """)
else:
    st.warning("Não foi possível carregar os dados. Execute o script `transform.py` e atualize a página.")
