# app.py (Versão Corrigida e Estruturada)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

# --- 1. DEFINIÇÕES DE FUNÇÕES ---
# Colocamos todas as definições de funções aqui no início.

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """
    Carrega os dados do CSV, trata erros e converte tipos de dados.
    """
    if not os.path.exists(path):
        st.error(f"Arquivo de dados não encontrado em '{path}'. Verifique o caminho no seu arquivo .env e se o script de transformação foi executado.")
        return pd.DataFrame()
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
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar ou processar o arquivo CSV: {e}")
        return pd.DataFrame()

def calculate_score_and_details(row: pd.Series) -> tuple[float, list[str]]:
    """
    Função centralizada que calcula o Score e retorna as justificativas.
    """
    # ... (seu código de cálculo de score continua aqui, sem alterações) ...
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


# --- Funções auxiliares: CSS e carregamento de scores ---
from pathlib import Path

def apply_external_css():
    css_path = Path(__file__).resolve().parent / 'styles' / 'styles.css'
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception:
        pass

def load_scores_df() -> pd.DataFrame:
    scores_path = Path(__file__).resolve().parent.parent / 'data' / 'scores.csv'
    if not scores_path.exists():
        st.warning(f"scores.csv não encontrado em {scores_path}")
        return pd.DataFrame()
    try:
        return pd.read_csv(scores_path)
    except Exception as e:
        st.error(f"Erro ao carregar scores.csv: {e}")
        return pd.DataFrame()

def build_score_details_from_row(row: pd.Series) -> list[str]:
    details = []
    mapping = [
        ('score_dy_12m', 'DY 12m'),
        ('score_dy_5anos', 'DY 5 Anos'),
        ('score_payout', 'Payout'),
        ('score_roe', 'ROE'),
        ('score_pl', 'P/L'),
        ('score_pvp', 'P/VP'),
        ('score_divida_marketcap', 'Dívida/Market Cap'),
        ('score_divida_ebitda', 'Dívida/EBITDA'),
        ('score_crescimento', 'Crescimento 5A'),
        ('score_sentimento', 'Sentimento'),
    ]
    for col, label in mapping:
        if col in row.index and pd.notna(row[col]):
            val = row[col]
            sign = '+' if val > 0 else ''
            details.append(f"{label}: **{sign}{val:.1f}**")
    return details

# --- 2. EXECUÇÃO PRINCIPAL ---
# Esta função 'main' conterá a lógica principal da sua aplicação.
def main():
    # --- CONFIGURAÇÃO DA PÁGINA ---
    st.set_page_config(page_title="Investidor Inteligente - Análise de Ações", layout="wide", page_icon="📈")
    # Aplica CSS externo
    apply_external_css()

    # --- CARREGAMENTO DOS DADOS ---
    load_dotenv()
    data_path = os.getenv('B3_REPORT_PATH')

    # Carrega dados base (se .env não definido, tenta indicadores.csv como fallback)
    if data_path:
        df = load_data(data_path)
    else:
        st.info("Usando fontes em data/ por falta de B3_REPORT_PATH.")
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent / 'data'
        try:
            indic = pd.read_csv(base / 'indicadores.csv')
            dy = pd.read_csv(base / 'dividend_yield.csv')
            indic['ticker_base'] = indic['ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
            dy['ticker_base'] = dy['ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
            df = indic.merge(dy[['ticker_base','DY12M','DY5anos']], on='ticker_base', how='left')
            # Renomeia mínimas para compatibilidade de exibição
            df.rename(columns={
                'empresa':'Empresa','setor_brapi':'Setor (brapi)','logo':'Logo','perfil_acao':'Perfil da Ação',
                'market_cap':'Market Cap','preco_atual':'Preço Atual','p_l':'P/L','p_vp':'P/VP',
                'payout_ratio':'Payout Ratio (%)','crescimento_preco':'Crescimento Preço (%)','roe':'ROE (%)',
                'divida_total':'Dívida Total','divida_ebitda':'Dívida/EBITDA','sentimento_gauge':'Sentimento Gauge',
                'DY12M':'DY (Taxa 12m, %)','DY5anos':'DY 5 Anos Média (%)'
            }, inplace=True)
            # Define Ticker (sem .SA)
            df['Ticker'] = df['ticker_base']
        except Exception as e:
            st.error(f"Falha ao montar dados base de ../data: {e}")
            df = pd.DataFrame()

    # Se o dataframe estiver vazio (devido a um erro no carregamento), interrompa.
    if df.empty:
        st.warning("O DataFrame está vazio. A aplicação não pode continuar.")
        st.stop()

    # --- MERGE SCORE EXTERNO ---
    scores_df = load_scores_df()
    if not scores_df.empty:
        # Esperado: scores_df tem 'ticker_base' e colunas score_*
        merge_left = 'Ticker' if 'Ticker' in df.columns else df.index.name
        if merge_left is None:
            # Se vier com índice como ticker .SA, cria Ticker
            if 'Ticker' not in df.columns and df.index.size > 0:
                df['Ticker'] = df.index.astype(str).str.replace('.SA','', regex=False)
            merge_left = 'Ticker'
        df = df.merge(scores_df, left_on=merge_left, right_on='ticker_base', how='left')
        # Score Total e Detalhes
        if 'score_total' in df.columns:
            df['Score Total'] = pd.to_numeric(df['score_total'], errors='coerce').fillna(0)
        else:
            df['Score Total'] = 0
        df['Score Details'] = df.apply(build_score_details_from_row, axis=1)
    else:
        # Fallback: mantém cálculo interno, se necessário
        score_results = df.apply(calculate_score_and_details, axis=1)
        df['Score Total'] = score_results.apply(lambda x: x[0])
        df['Score Details'] = score_results.apply(lambda x: x[1])

    # ... (todo o resto do seu código da UI do Streamlit vai aqui, sem alterações) ...
    # --- UI: TÍTULO E SIDEBAR ---
    st.title("📈 Investidor Inteligente")
    st.markdown("Plataforma de análise e ranking de ações baseada nos princípios de **Barsi, Bazin, Buffett, Lynch e Graham**.")
    st.sidebar.header("Filtros de Análise")
    setores_disponiveis = sorted(df['Setor (brapi)'].dropna().unique().tolist())
    setor_filtro = st.sidebar.multiselect("Setores", setores_disponiveis, default=setores_disponiveis)

    # Ordena Perfil da Ação do menor para o maior porte
    perfil_ordem = {
        'Penny Stock': 0,
        'Micro Cap': 1,
        'Small Cap': 2,
        'Mid Cap': 3,
        'Blue Chip': 4,
    }
    perfis_raw = [p for p in df['Perfil da Ação'].dropna().unique().tolist()]
    perfis_disponiveis = sorted(perfis_raw, key=lambda x: (perfil_ordem.get(x, 999), x))
    perfil_filtro = st.sidebar.multiselect("Perfil da Ação", perfis_disponiveis, default=perfis_disponiveis)

    score_range = st.sidebar.slider("Faixa de Score", min_value=0, max_value=200, value=(100, 200))
    dy_min = st.sidebar.slider("DY 12 Meses Mínimo (%)", 0.0, 30.0, 3.5, 0.1)
    dy_5y_min = st.sidebar.slider("DY 5 Anos Mínimo (%)", 0.0, 20.0, 4.0, 0.1)

    # --- FILTRAGEM E ORDENAÇÃO ---
    df_filtrado = df[
        (df['Setor (brapi)'].isin(setor_filtro)) &
        (df['Perfil da Ação'].isin(perfil_filtro)) &
        (df['Score Total'].between(score_range[0], score_range[1])) &
        (df['DY (Taxa 12m, %)'] >= dy_min) &
        (df['DY 5 Anos Média (%)'] >= dy_5y_min)
    ].copy()
    st.sidebar.header("Ordenação")
    col_ordem = st.sidebar.selectbox("Ordenar por", ['Score Total', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'P/L', 'P/VP'], index=0)
    asc = st.sidebar.radio("Ordem", ["Crescente", "Decrescente"], index=1) == "Crescente"
    df_filtrado.sort_values(by=col_ordem, ascending=asc, inplace=True)

    # --- UI: ABAS DE EXIBIÇÃO ---
    # ... (todo o código das suas abas, que já estava correto) ...
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Ranking Geral", "📈 Ranking Detalhado", "🔍 Análise Individual", "📜 Guia do Investidor"])

    with tab1:
        st.header(f"Ranking Geral ({len(df_filtrado)} ações encontradas)")
        df_display = df_filtrado[['Logo', 'Ticker', 'Empresa', 'Setor (brapi)', 'Perfil da Ação', 'Score Total']]
        st.dataframe(df_display, column_config={
            "Logo": st.column_config.ImageColumn("Logo"), "Ticker": st.column_config.TextColumn("Ticker"),
            "Empresa": st.column_config.TextColumn("Empresa"), "Setor (brapi)": st.column_config.TextColumn("Setor"),
            "Perfil da Ação": st.column_config.TextColumn("Perfil"),
            "Score Total": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=200)},
            use_container_width=True, hide_index=True)

    with tab2:
        st.header(f"Ranking Detalhado ({len(df_filtrado)} ações encontradas)")
        cols_detalhado = [
            'Logo', 'Ticker', 'Empresa', 'Setor (brapi)', 'Perfil da Ação', 'Preço Atual',
            'P/L', 'P/VP', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'Payout Ratio (%)',
            'ROE (%)', 'Dívida/EBITDA', 'Crescimento Preço (%)', 'Sentimento Gauge', 'Score Total'
        ]
        df_display_detalhado = df_filtrado[cols_detalhado]
        st.dataframe(df_display_detalhado, column_config={
            "Logo": st.column_config.ImageColumn("Logo"), "Ticker": st.column_config.TextColumn("Ticker"),
            "Empresa": st.column_config.TextColumn("Empresa"), "Setor (brapi)": st.column_config.TextColumn("Setor"),
            "Perfil da Ação": st.column_config.TextColumn("Perfil"),
            "Preço Atual": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
            "P/L": st.column_config.NumberColumn("P/L", format="%.2f"),
            "P/VP": st.column_config.NumberColumn("P/VP", format="%.2f"),
            "DY (Taxa 12m, %)": st.column_config.NumberColumn("DY 12m", format="%.2f%%"),
            "DY 5 Anos Média (%)": st.column_config.NumberColumn("DY 5 Anos", format="%.2f%%"),
            "Payout Ratio (%)": st.column_config.NumberColumn("Payout", format="%.1f%%"),
            "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
            "Dívida/EBITDA": st.column_config.NumberColumn("Dív/EBITDA", format="%.2f"),
            "Crescimento Preço (%)": st.column_config.NumberColumn("Cresc. 5A", format="%.1f%%"),
            "Sentimento Gauge": st.column_config.NumberColumn("Sentimento", format="%d/100"),
            "Score Total": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=200)},
            use_container_width=True, hide_index=True)

    with tab3:
        st.header("Análise Individual e Composição do Score")
        if not df_filtrado.empty:
            ticker_selecionado = st.selectbox("Selecione a Ação", df_filtrado['Ticker'].tolist(),
                format_func=lambda t: f"{t} - {df_filtrado.loc[df_filtrado['Ticker'] == t, 'Empresa'].iloc[0]}")
            if ticker_selecionado:
                acao = df_filtrado[df_filtrado['Ticker'] == ticker_selecionado].iloc[0]
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
                                             title='Distribuição das Recomendações', text='Contagem', color='Recomendação',
                                             color_discrete_map={'Strong Buy': 'green', 'Buy': 'lightgreen', 'Hold': 'gold', 'Sell': 'orange', 'Strong Sell': 'red'})
                            fig_bar.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
                            st.plotly_chart(fig_bar, use_container_width=True)
                        else:
                            st.info("Não há recomendações de analistas disponíveis para este ativo.")
                    else:
                        st.warning("Dados de recomendação não encontrados. Execute a versão mais recente do `transform.py`.")
        else:
            st.info("Nenhuma ação encontrada com os filtros atuais.")

    with tab4:
        st.header("Guia do Investidor Inteligente")
        # ... (seu código do Guia do Investidor, que já estava correto) ...
        st.markdown("---")
        st.subheader("Critérios de Pontuação (Score)")
        st.markdown("""
        A pontuação de cada ação é calculada somando-se os pontos de diversos critérios fundamentalistas, totalizando um máximo de 200 pontos.
        """)

        with st.expander("1. Dividend Yield (DY) - Até 45 pontos"):
            st.markdown("""
            - **O que é?** O retorno em dividendos que a ação pagou, dividido pelo seu preço. A média de 5 anos mostra a consistência.
            - **Por que analisar?** É o principal indicador para quem busca renda passiva. Um DY alto e consistente, como defendido por Luiz Barsi, indica uma "vaca leiteira".
            - **Cálculo do Score:**
                - **DY 12 meses:** > 5% (**+20**), 3.5%-5% (**+15**), 2%-3.5% (**+10**), < 2% (**-5**)
                - **DY Média 5 Anos:** > 8% (**+25**), 6%-8% (**+20**), 4%-6% (**+10**)
            """)
        
        with st.expander("2. Valuation (P/L e P/VP) - Até 35 pontos"):
            st.markdown("""
            - **O que são?** P/L (Preço/Lucro) e P/VP (Preço/Valor Patrimonial) são os principais indicadores de valuation de Benjamin Graham para saber se uma ação está "barata".
            - **Por que analisar?** Comprar ativos abaixo do seu valor intrínseco é o pilar do *Value Investing*, criando uma margem de segurança contra a volatilidade do mercado.
            - **Cálculo do Score:**
                - **P/L:** < 12 (**+15**), 12-18 (**+10**), > 25 (**-5**)
                - **P/VP:** < 0.66 (**+20**), 0.66-1.5 (**+10**), 1.5-2.5 (**+5**), > 4 (**-5**)
            """)

        with st.expander("3. Rentabilidade e Gestão (ROE e Payout) - Até 35 pontos"):
            st.markdown("""
            - **O que são?** ROE (Return on Equity) mede a eficiência da empresa em gerar lucro. Payout é a fatia do lucro distribuída como dividendos.
            - **Por que analisar?** Um ROE alto (pilar de Warren Buffett) indica boa gestão e vantagens competitivas. Um Payout equilibrado mostra que a empresa remunera o acionista sem deixar de reinvestir em seu crescimento.
            - **Cálculo do Score:**
                - **ROE (Financeiro):** > 15% (**+25**), 12%-15% (**+20**), 8%-12% (**+10**)
                - **ROE (Outros Setores):** > 12% (**+15**), 8%-12% (**+5**)
                - **Payout:** 30%-60% (**+10**), 60%-80% (**+5**), fora de 20%-80% (**-5**)
            """)

        with st.expander("4. Saúde Financeira (Endividamento) - Até 20 pontos"):
            st.markdown("""
            - **O que é?** Mede a dívida da empresa em relação à sua geração de caixa (EBITDA) e ao seu valor de mercado. *Não se aplica ao setor financeiro.*
            - **Por que analisar?** Empresas com dívidas controladas são mais resilientes a crises e têm maior flexibilidade para crescer e pagar dividendos. Um endividamento baixo é um forte sinal de segurança.
            - **Cálculo do Score:**
                - **Dívida/Market Cap:** < 0.5 (**+10**), 0.5-1.0 (**+5**), > 2.0 (**-5**)
                - **Dívida/EBITDA:** < 1 (**+10**), 1-2 (**+5**), > 6 (**-5**)
            """)

        with st.expander("5. Crescimento e Sentimento - Até 25 pontos"):
            st.markdown("""
            - **O que são?** O crescimento do preço da ação nos últimos 5 anos e a recomendação consolidada de analistas de mercado.
            - **Por que analisar?** Mostra o histórico de valorização do ativo e a percepção atual do mercado sobre seu futuro, adicionando uma camada de análise de momento.
            - **Cálculo do Score:**
                - **Crescimento Preço 5 Anos:** > 15% (**+15**), 10%-15% (**+10**), 5%-10% (**+5**), < 0% (**-5**)
                - **Sentimento do Mercado:** Pontuação de **-5 a +10**, proporcional à nota de 0 a 100.
            """)

        st.markdown("---")
        st.subheader("Guia de Perfil da Ação")
        st.markdown("""
        A classificação por perfil ajuda a entender o porte, o risco e o potencial de cada empresa.
        """)
        with st.expander("Como o Perfil é Calculado?"):
            st.markdown("""
            A classificação é feita com base no **Valor de Mercado (Market Cap)** da empresa e no seu **Preço por Ação** (do menor para o maior porte):
            - **Penny Stock:** Se o Preço da Ação for **menor que R$ 1,00**.
            - **Micro Cap:** Se o Valor de Mercado for **menor que R$ 2 bilhões**.
            - **Small Cap:** Se o Valor de Mercado estiver **entre R$ 2 bilhões e R$ 10 bilhões**.
            - **Mid Cap:** Se o Valor de Mercado estiver **entre R$ 10 bilhões e R$ 50 bilhões**.
            - **Blue Chip:** Se o Valor de Mercado for **maior que R$ 50 bilhões**.
            """)
        
        st.markdown("---")
        st.subheader("Análise Setorial (Foco em Dividendos)")
        st.markdown("""
        Certos setores são conhecidos por sua resiliência e previsibilidade de receita, tornando-os favoritos para carteiras de dividendos.
        """)
        with st.expander("Bancos & Seguros"):
            st.markdown("""
            - **Vantagens:** Essenciais para a economia, lucratividade elevada, pagadores de dividendos consistentes e regulamentação forte que cria barreiras de entrada.
            - **Desvantagens:** Sensíveis a crises econômicas e mudanças na taxa de juros. A concorrência de fintechs pode pressionar as margens.
            """)
        with st.expander("Energia Elétrica"):
            st.markdown("""
            - **Vantagens:** Setor perene com demanda constante e previsível. Contratos de concessão longos garantem receita estável por décadas, ideal para dividendos.
            - **Desvantagens:** Forte regulação governamental, risco de interferência política e necessidade de grandes investimentos em infraestrutura.
            """)
        with st.expander("Saneamento"):
            st.markdown("""
            - **Vantagens:** Serviço essencial com demanda inelástica (as pessoas sempre precisarão de água e esgoto). Possui características de monopólio natural e alta previsibilidade de receita.
            - **Desvantagens:** Regulação intensa, alta necessidade de capital para expansão e sensibilidade a questões políticas e tarifárias.
            """)
        with st.expander("Telecomunicações"):
            st.markdown("""
            - **Vantagens:** Serviço considerado essencial na era digital. Receitas recorrentes através de assinaturas e grande barreira de entrada devido ao alto custo da infraestrutura.
            - **Desvantagens:** Setor altamente competitivo, necessidade constante de investimentos em novas tecnologias (como 5G) e sujeito a forte regulação.
            """)

# Esta linha garante que o código principal só será executado quando
# você rodar o script diretamente (ex: 'streamlit run app.py').
if __name__ == "__main__":
    main()