import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta  # Adicionado de volta

# Configuração da página
st.set_page_config(page_title="Investidor Inteligente - Análise de Investimentos", layout="wide", page_icon="📈")

# CSS para responsividade e estilo
st.markdown("""
<style>
    .main .block-container {
        padding: 1rem;
    }
    .stMarkdown, .stText {
        font-size: 0.9rem;
    }
    @media (max-width: 600px) {
        .stMarkdown, .stText {
            font-size: 0.8rem;
        }
        .stColumn > div {
            padding: 0.5rem;
        }
        img {
            width: 40px !important;
        }
    }
    .stSidebar .stButton {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Título e descrição
st.title("Investidor Inteligente - Análise de Investimentos")
st.markdown("""
Bem-vindo ao **Investidor Inteligente**, um aplicativo para ranquear ações e fundos com base em fundamentos sólidos, dividendos consistentes e valor intrínseco, combinando o melhor das filosofias de Luiz Barsi, Décio Bazin, Warren Buffett, Peter Lynch e Benjamin Graham. Use os filtros abaixo para personalizar o ranking e explore gráficos interativos!
""")

# Carregar dados do CSV com cache
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(r"E:\finance-manager\data\relatorio_analise_b3.csv", index_col=0)
        colunas_percentual = ["DY (Taxa 12m, %)", "DY 5 Anos Média (%)", "ROE (%)", "Payout Ratio (%)", "Crescimento Preço (%)", "Sentimento Gauge"]
        for col in colunas_percentual:
            df[col] = df[col].apply(lambda x: float(str(x).replace('%', '')) if '%' in str(x) else float(str(x)) if str(x) != 'N/A' else 0.0)
        colunas_numericas = ["Preço Atual", "P/L", "P/VP", "Market Cap (R$)", "Último Dividendo (R$)", "Dívida Total"]
        for col in colunas_numericas:
            df[col] = df[col].apply(lambda x: float(str(x).replace('R$', '').replace(' Bi', '').strip()) * 1_000_000_000 if isinstance(x, str) and 'Bi' in x else float(str(x).replace('R$', '').strip()) if isinstance(x, str) else float(x) if pd.notna(x) else 0.0)
        df["Dívida/EBITDA"] = pd.to_numeric(df["Dívida/EBITDA"], errors='coerce').fillna(0)
        colunas_data = ["Data Últ. Div.", "Data Ex-Div."]
        for col in colunas_data:
            df[col] = pd.to_datetime(df[col], format='%d-%m-%Y', errors='coerce')
        df['Ticker'] = df.index.str.replace('.SA', '')
        return df
    except FileNotFoundError:
        st.error("Arquivo 'relatorio_analise_b3.csv' não encontrado. Execute o script de coleta de dados primeiro.")
        st.stop()

df = load_data()

# Mapeamento de setores e tipos
setores_traducao = {'Finance': 'Financeiro', 'Utilities': 'Serviços públicos', 'Communications': 'Comunicações', 'Industrial Services': 'Serviços industriais'}
df['Setor (brapi)'] = df['Setor (brapi)'].map(setores_traducao).fillna(df['Setor (brapi)']).str.capitalize()
tipo_traducao = {'stock': 'Ações', 'fund': 'Fundos'}
df['Tipo'] = df['Tipo'].map(tipo_traducao).fillna(df['Tipo']).str.capitalize()

# Função para calcular o Score Total usando dados do CSV
def calculate_total_score(row):
    score = 0
    setor = row['Setor (brapi)'].lower()

    # Dividend Yield (12 meses e 5 anos)
    dy_12m = row['DY (Taxa 12m, %)']
    if dy_12m > 5: score += 20
    elif dy_12m > 3.5: score += 15
    elif dy_12m > 2: score += 10
    elif dy_12m < 2: score -= 5

    dy_5y = row['DY 5 Anos Média (%)']
    if dy_5y > 8: score += 25
    elif dy_5y > 6: score += 20
    elif dy_5y > 4: score += 10

    # Payout Ratio
    payout = row['Payout Ratio (%)']
    if 30 <= payout <= 60: score += 10
    elif 60 < payout <= 80: score += 5
    elif payout < 20 or payout > 80: score -= 5

    # ROE (ajuste para Financeiro)
    roe = row['ROE (%)']
    if setor == 'financeiro':
        if roe > 15: score += 25
        elif roe > 12: score += 20
        elif roe > 8: score += 10
    else:
        if roe > 12: score += 15
        elif roe > 8: score += 5

    # P/L e P/VP
    pl = row['P/L']
    if pl > 0 and pl < 12: score += 15
    elif pl < 18: score += 10
    elif pl > 25: score -= 5

    pvp = row['P/VP']
    if pvp < 0.66: score += 20
    elif pvp < 1.5: score += 10
    elif pvp < 2.5: score += 5
    elif pvp > 4: score -= 5

    # Dívida (exceto Financeiro)
    if setor != 'financeiro':
        debt_mc = row['Dívida Total'] / row['Market Cap (R$)'] if row['Market Cap (R$)'] > 0 else 0
        if debt_mc < 0.5: score += 10
        elif debt_mc < 1.0: score += 5
        elif debt_mc > 2.0: score -= 5

        div_ebitda = row['Dívida/EBITDA']
        if div_ebitda < 1: score += 10
        elif div_ebitda < 2: score += 5
        elif div_ebitda > 6: score -= 5

    # Crescimento
    growth_price = row['Crescimento Preço (%)']
    if growth_price > 15: score += 15
    elif growth_price > 10: score += 10
    elif growth_price > 5: score += 5
    elif growth_price < 0: score -= 5

    # Sentimento do Mercado (usando dados do CSV)
    sentiment_gauge = row['Sentimento Gauge'] if 'Sentimento Gauge' in row else 50
    sentiment_score = max(0, min(10, sentiment_gauge / 10))  # Normalizado de 0-10
    score += sentiment_score

    return max(0, min(200, score))

df['Score Total'] = df.apply(calculate_total_score, axis=1)

# Filtros interativos no sidebar
st.sidebar.header("Filtros")
setores_disponiveis = sorted(df['Setor (brapi)'].unique().tolist())
setor_filtro = st.sidebar.multiselect("Selecione Setores", setores_disponiveis, default=setores_disponiveis)
dy_12m_min = st.sidebar.slider("DY 12 Meses Mínimo (%)", 0.0, 20.0, 3.5, step=0.1)
dy_5y_min = st.sidebar.slider("DY 5 Anos Mínimo (%)", 0.0, 20.0, 6.0, step=0.1)  # Padrão 6%
score_min = st.sidebar.slider("Score Mínimo", 0, 200, 100, step=1)

# Ordenação
st.sidebar.header("Ordenação")
colunas_ordenacao = ['Score Total', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'P/L', 'P/VP', 'ROE (%)', 'Payout Ratio (%)', 'Sentimento Gauge']
coluna_ordenacao = st.sidebar.selectbox("Ordenar por", colunas_ordenacao)
ordem = st.sidebar.radio("Ordem", ["Decrescente (⬇)", "Crescente (⬆)"], index=0)
ascending = True if ordem == "Crescente (⬆)" else False

# Aplicar filtros
df_filtrado = df[
    (df['Setor (brapi)'].isin(setor_filtro)) &
    (df['DY (Taxa 12m, %)'] >= dy_12m_min) &
    (df['DY 5 Anos Média (%)'] >= dy_5y_min) &
    (df['Score Total'] >= score_min)
].sort_values(by=coluna_ordenacao, ascending=ascending)

# Abas para organização
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Ranking", "Ranking Detalhado", "Gráficos", "Detalhamento dos Scores", "Critérios de Investimento"])

with tab1:
    st.header("Ranking")
    st.markdown("Tabela resumida com as principais métricas das ações ranqueadas.")
    cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1.5, 1, 1])
    for i, col_name in enumerate(['Logo', 'Ticker', 'Empresa', 'Setor', 'Preço Atual', 'DY 12 Meses (%)', 'DY 5 Anos (%)', 'Market Cap (R$)', 'Score Total', 'Sentimento Gauge']):
        with cols[i]:
            st.markdown(f"**{col_name}**")
    for _, row in df_filtrado.iterrows():
        cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1.5, 1, 1])
        with cols[0]:
            if row['Logo'] != 'N/A' and isinstance(row['Logo'], str):
                try:
                    st.image(row['Logo'], width=50)
                except:
                    st.write("Logo N/A")
            else:
                st.write("Logo N/A")
        with cols[1]:
            st.write(row['Ticker'])
        with cols[2]:
            st.write(row['Empresa'])
        with cols[3]:
            st.write(row['Setor (brapi)'])
        with cols[4]:
            st.write(f"R$ {row['Preço Atual']:.2f}")
        with cols[5]:
            st.write(f"{row['DY (Taxa 12m, %)']:.2f}%")
        with cols[6]:
            st.write(f"{row['DY 5 Anos Média (%)']:.2f}%")
        with cols[7]:
            st.write(f"R$ {row['Market Cap (R$)'] / 1_000_000_000:.2f} Bi")
        with cols[8]:
            st.write(f"{row['Score Total']:.0f}")
        with cols[9]:
            st.write(f"{row['Sentimento Gauge']:.0f}%")

with tab2:
    st.header("Ranking Detalhado")
    st.markdown("Tabela detalhada com todos os indicadores das ações ranqueadas.")
    cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.5, 1, 1.5, 1])
    for i, col_name in enumerate(['Logo', 'Ticker', 'Empresa', 'Setor', 'Tipo', 'Preço Atual', 'P/L', 'P/VP', 'ROE (%)', 
                                 'DY 12 Meses (%)', 'DY 5 Anos (%)', 'Último Dividendo (R$)', 'Data Últ. Div.', 'Data Ex-Div.', 
                                 'Payout Ratio (%)', 'Dívida Total', 'Dívida/EBITDA', 'Market Cap (R$)', 'Sentimento Gauge']):
        with cols[i]:
            st.markdown(f"**{col_name}**")
    for _, row in df_filtrado.iterrows():
        cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.5, 1, 1.5, 1])
        with cols[0]:
            if row['Logo'] != 'N/A' and isinstance(row['Logo'], str):
                try:
                    st.image(row['Logo'], width=50)
                except:
                    st.write("Logo N/A")
            else:
                st.write("Logo N/A")
        with cols[1]:
            st.write(row['Ticker'])
        with cols[2]:
            st.write(row['Empresa'])
        with cols[3]:
            st.write(row['Setor (brapi)'])
        with cols[4]:
            st.write(row['Tipo'])
        with cols[5]:
            st.write(f"R$ {row['Preço Atual']:.2f}")
        with cols[6]:
            st.write(f"{row['P/L']:.2f}")
        with cols[7]:
            st.write(f"{row['P/VP']:.2f}")
        with cols[8]:
            st.write(f"{row['ROE (%)']:.2f}%")
        with cols[9]:
            st.write(f"{row['DY (Taxa 12m, %)']:.2f}%")
        with cols[10]:
            st.write(f"{row['DY 5 Anos Média (%)']:.2f}%")
        with cols[11]:
            st.write(f"R$ {row['Último Dividendo (R$)']:.2f}")
        with cols[12]:
            st.write(row['Data Últ. Div.'].strftime('%d/%m/%Y') if pd.notna(row['Data Últ. Div.']) else "N/A")
        with cols[13]:
            st.write(row['Data Ex-Div.'].strftime('%d/%m/%Y') if pd.notna(row['Data Ex-Div.']) else "N/A")
        with cols[14]:
            st.write(f"{row['Payout Ratio (%)']:.2f}%")
        with cols[15]:
            st.write(f"R$ {row['Dívida Total'] / 1_000_000_000:.2f} Bi" if pd.notna(row['Dívida Total']) else "N/A")
        with cols[16]:
            st.write(f"{row['Dívida/EBITDA']:.2f}" if pd.notna(row['Dívida/EBITDA']) else "N/A")
        with cols[17]:
            st.write(f"R$ {row['Market Cap (R$)'] / 1_000_000_000:.2f} Bi")
        with cols[18]:
            st.write(f"{row['Sentimento Gauge']:.0f}%")

with tab3:
    st.header("Gráficos Interativos")
    st.markdown("Explore visualizações detalhadas das ações ranqueadas.")
    
    acao_selecionada = st.selectbox("Selecione uma ação para análise detalhada", df_filtrado['Ticker'].tolist())
    df_acao = df_filtrado[df_filtrado['Ticker'] == acao_selecionada].iloc[0]

    # Gráfico 1: Score Total por Setor
    st.subheader("Score Total por Setor")
    fig1 = px.bar(
        df_filtrado,
        x='Setor (brapi)',
        y='Score Total',
        color='Setor (brapi)',
        title="Score Total por Setor",
        text='Score Total'
    )
    fig1.update_traces(textposition='auto')
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Análise Individual
    st.subheader(f"Análise de {acao_selecionada}")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=['Atual'], y=[df_acao['DY (Taxa 12m, %)']], mode='lines+markers', name='DY 12m (%)'))
    fig2.add_trace(go.Scatter(x=['Atual'], y=[df_acao['DY 5 Anos Média (%)']], mode='lines+markers', name='DY 5 Anos (%)'))
    fig2.add_trace(go.Scatter(x=['Atual'], y=[df_acao['ROE (%)']], mode='lines+markers', name='ROE (%)'))
    fig2.add_trace(go.Scatter(x=['Atual'], y=[df_acao['Sentimento Gauge']], mode='lines+markers', name='Sentimento (%)'))
    fig2.update_layout(title=f"Métricas de {acao_selecionada}", xaxis_title="Período", yaxis_title="Valor", legend_title="Métricas")
    st.plotly_chart(fig2, use_container_width=True)

    # Gráfico 3: Candlestick Simulado
    st.subheader("Candlestick Simulado")
    fig3 = go.Figure(data=[go.Candlestick(
        x=[acao_selecionada],
        open=[df_acao['Preço Atual']],
        high=[df_acao['Preço Atual'] * 1.05],
        low=[df_acao['Preço Atual'] * 0.95],
        close=[df_acao['Preço Atual']]
    )])
    fig3.update_layout(title="Candlestick Simulado", xaxis_title="Ação", yaxis_title="Preço (R$)")
    st.plotly_chart(fig3, use_container_width=True)

    # Gráfico 4: Correlação P/L vs. DY
    st.subheader("Correlação P/L vs. DY 12m")
    fig4 = px.scatter(
        df_filtrado,
        x='P/L',
        y='DY (Taxa 12m, %)',
        color='Setor (brapi)',
        trendline="ols",
        title="Correlação entre P/L e DY 12m"
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Gráfico 5: Mapa de Dividendos
    st.subheader("Mapa de Dividendos")
    ultima_data_div = df_acao['Data Últ. Div.']
    ultimo_dividendo = df_acao['Último Dividendo (R$)']
    dy_12m = df_acao['DY (Taxa 12m, %)']
    preco_atual = df_acao['Preço Atual']
    
    fig5 = go.Figure()
    if pd.notna(ultima_data_div) and pd.notna(ultimo_dividendo):
        fig5.add_trace(go.Scatter(x=[ultima_data_div], y=[ultimo_dividendo], mode='markers', name='Passado'))
    if pd.notna(ultima_data_div) and pd.notna(dy_12m) and pd.notna(preco_atual) and preco_atual > 0:
        dividendo_estimado = (dy_12m / 100) * preco_atual
        datas_futuro = [ultima_data_div + relativedelta(months=6), ultima_data_div + relativedelta(months=12)]
        fig5.add_trace(go.Scatter(x=datas_futuro, y=[dividendo_estimado] * 2, mode='markers', name='Futuro (Estimado)'))
    fig5.update_layout(title=f"Mapa de Dividendos de {acao_selecionada}", xaxis_title="Data", yaxis_title="Valor (R$)")
    st.plotly_chart(fig5, use_container_width=True)

    # Gráfico 6: Velocímetro de Sentimento
    st.subheader("Velocímetro de Sentimento")
    sentiment_gauge = df_acao['Sentimento Gauge'] if 'Sentimento Gauge' in df_acao else 50
    fig6 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sentiment_gauge,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 100]},
               'steps': [{'range': [0, 20], 'color': 'red'}, {'range': [20, 40], 'color': 'orange'},
                         {'range': [40, 60], 'color': 'yellow'}, {'range': [60, 80], 'color': 'lightgreen'},
                         {'range': [80, 100], 'color': 'green'}],
               'bar': {'color': "gray"}}
    ))
    st.plotly_chart(fig6, use_container_width=True)

with tab4:
    st.header("Detalhamento dos Scores")
    st.markdown("Clique no nome da empresa para ver como o Score Total foi calculado.")
    for _, row in df_filtrado.iterrows():
        with st.expander(f"{row['Ticker']} - {row['Empresa']}"):
            st.markdown(f"### Detalhamento do Score Total: {row['Score Total']:.0f}")
            detalhes = []
            # Dividend Yield 12 meses
            if row['DY (Taxa 12m, %)'] > 5: detalhes.append("Dividend Yield dos últimos 12 meses superior a 5%: **+20** - Indica um retorno atrativo por dividendos, alinhado à busca por renda passiva.")
            elif row['DY (Taxa 12m, %)'] > 3.5: detalhes.append("Dividend Yield dos últimos 12 meses entre 3.5% e 5%: **+15** - Oferece um retorno sólido, mas ainda abaixo do ideal.")
            elif row['DY (Taxa 12m, %)'] > 2: detalhes.append("Dividend Yield dos últimos 12 meses entre 2% e 3.5%: **+10** - Retorno moderado, aceitável para diversificação.")
            elif row['DY (Taxa 12m, %)'] < 2: detalhes.append("Dividend Yield dos últimos 12 meses inferior a 2%: **-5** - Sugere baixa atratividade para renda passiva.")
            # Dividend Yield 5 anos
            if row['DY 5 Anos Média (%)'] > 8: detalhes.append("Média de Dividend Yield nos últimos 5 anos superior a 8%: **+25** - Demonstra consistência e alta geração de renda.")
            elif row['DY 5 Anos Média (%)'] > 6: detalhes.append("Média de Dividend Yield nos últimos 5 anos entre 6% e 8%: **+20** - Consistência sólida para investimentos de longo prazo.")
            elif row['DY 5 Anos Média (%)'] > 4: detalhes.append("Média de Dividend Yield nos últimos 5 anos entre 4% e 6%: **+10** - Nível razoável de retorno histórico.")
            # Payout Ratio
            if 30 <= row['Payout Ratio (%)'] <= 60: detalhes.append("Payout Ratio entre 30% e 60%: **+10** - Indica equilíbrio entre dividendos e reinvestimento na empresa.")
            elif 60 < row['Payout Ratio (%)'] <= 80: detalhes.append("Payout Ratio entre 60% e 80%: **+5** - Aceitável, mas com menor margem para crescimento.")
            elif row['Payout Ratio (%)'] < 20 or row['Payout Ratio (%)'] > 80: detalhes.append("Payout Ratio fora da faixa 20%-80%: **-5** - Pode indicar risco de sustentabilidade ou baixa distribuição.")
            # ROE
            if row['Setor (brapi)'].lower() == 'financeiro':
                if row['ROE (%)'] > 15: detalhes.append("ROE superior a 15% (setor financeiro): **+25** - Alta eficiência no uso do capital próprio.")
                elif row['ROE (%)'] > 12: detalhes.append("ROE entre 12% e 15% (setor financeiro): **+20** - Bom retorno para o setor.")
                elif row['ROE (%)'] > 8: detalhes.append("ROE entre 8% e 12% (setor financeiro): **+10** - Retorno aceitável.")
            else:
                if row['ROE (%)'] > 12: detalhes.append("ROE superior a 12% (outros setores): **+15** - Excelente retorno sobre equity.")
                elif row['ROE (%)'] > 8: detalhes.append("ROE entre 8% e 12% (outros setores): **+5** - Retorno razoável.")
            # P/L
            if row['P/L'] > 0 and row['P/L'] < 12: detalhes.append("P/L inferior a 12: **+15** - Ação potencialmente subvalorizada.")
            elif row['P/L'] < 18: detalhes.append("P/L entre 12 e 18: **+10** - Valor justo com margem de segurança.")
            elif row['P/L'] > 25: detalhes.append("P/L superior a 25: **-5** - Pode indicar sobrevalorização.")
            # P/VP
            if row['P/VP'] < 0.66: detalhes.append("P/VP inferior a 0.66: **+20** - Ação significativamente subvalorizada.")
            elif row['P/VP'] < 1.5: detalhes.append("P/VP entre 0.66 e 1.5: **+10** - Valor justo com desconto.")
            elif row['P/VP'] < 2.5: detalhes.append("P/VP entre 1.5 e 2.5: **+5** - Valor razoável.")
            elif row['P/VP'] > 4: detalhes.append("P/VP superior a 4: **-5** - Possível sobrevalorização.")
            # Dívida (exceto Financeiro)
            if row['Setor (brapi)'].lower() != 'financeiro':
                debt_mc = row['Dívida Total'] / row['Market Cap (R$)'] if row['Market Cap (R$)'] > 0 else 0
                if debt_mc < 0.5: detalhes.append("Dívida/Market Cap inferior a 0.5: **+10** - Baixo endividamento relativo.")
                elif debt_mc < 1.0: detalhes.append("Dívida/Market Cap entre 0.5 e 1.0: **+5** - Endividamento moderado.")
                elif debt_mc > 2.0: detalhes.append("Dívida/Market Cap superior a 2.0: **-5** - Alto risco de endividamento.")
                if row['Dívida/EBITDA'] < 1: detalhes.append("Dívida/EBITDA inferior a 1: **+10** - Excelente capacidade de pagamento.")
                elif row['Dívida/EBITDA'] < 2: detalhes.append("Dívida/EBITDA entre 1 e 2: **+5** - Capacidade de pagamento razoável.")
                elif row['Dívida/EBITDA'] > 6: detalhes.append("Dívida/EBITDA superior a 6: **-5** - Alto risco de liquidez.")
            # Crescimento
            if row['Crescimento Preço (%)'] > 15: detalhes.append("Crescimento Preço superior a 15%: **+15** - Crescimento robusto ao longo de 5 anos.")
            elif row['Crescimento Preço (%)'] > 10: detalhes.append("Crescimento Preço entre 10% e 15%: **+10** - Crescimento sólido.")
            elif row['Crescimento Preço (%)'] > 5: detalhes.append("Crescimento Preço entre 5% e 10%: **+5** - Crescimento moderado.")
            elif row['Crescimento Preço (%)'] < 0: detalhes.append("Crescimento Preço inferior a 0%: **-5** - Declínio no valor ao longo do tempo.")
            # Sentimento
            sentiment_score = row['Sentimento Gauge'] / 10 if 'Sentimento Gauge' in row else 5
            if sentiment_score > 5: detalhes.append(f"Sentimento do mercado superior a 50: **+{sentiment_score}** - Indicador de confiança dos analistas.")
            elif sentiment_score < 5: detalhes.append(f"Sentimento do mercado inferior a 50: **{sentiment_score}** - Cautela sugerida por analistas.")
            for detalhe in detalhes:
                st.write(detalhe)

with tab5:
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

# Rodapé estilizado
st.markdown("""
---
<div style="text-align: center; font-size: 0.9rem; color: #666;">
    **Desenvolvido por Gustavo Lima** | Baseado nas melhores práticas de Luiz Barsi, Décio Bazin, Warren Buffett, Peter Lynch e Benjamin Graham | © 2025
</div>
""", unsafe_allow_html=True)