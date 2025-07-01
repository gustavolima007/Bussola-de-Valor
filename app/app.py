import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
        colunas_percentual = ["DY (Taxa 12m, %)", "DY 5 Anos Média (%)", "ROE (%)", "Payout Ratio (%)", "Crescimento Preço (%)"]
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

# Cache para recomendações de mercado
@st.cache_data
def get_sentiment_cache(ticker):
    try:
        ticker_yf = yf.Ticker(f"{ticker}.SA")
        recommendations = ticker_yf.recommendations
        if not recommendations.empty and 'To Grade' in recommendations.columns:
            sentiment = (recommendations['To Grade'].value_counts().reindex(['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'], fill_value=0) * [2, 1, 0, -1, -2]).sum() / len(recommendations) if len(recommendations) > 0 else 0
            return max(0, min(10, (sentiment * 50 + 50) / 10))  # Normalizado de 0-10
        return 0
    except Exception:
        return 0

# Função para calcular o Score Total com cache de sentimento
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
    cagr = row['Crescimento Preço (%)']
    if cagr > 15: score += 15
    elif cagr > 10: score += 10
    elif cagr > 5: score += 5
    elif cagr < 0: score -= 5

    # Sentimento do Mercado (usando cache)
    sentiment_score = get_sentiment_cache(row['Ticker'])
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
colunas_ordenacao = ['Score Total', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'P/L', 'P/VP', 'ROE (%)', 'Payout Ratio (%)']
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
tab1, tab2, tab3, tab4 = st.tabs(["Ranking", "Ranking Detalhado", "Gráficos", "Detalhamento dos Scores"])

with tab1:
    st.header("Ranking")
    st.markdown("Tabela resumida com as principais métricas das ações ranqueadas.")
    cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1.5, 1])
    for i, col_name in enumerate(['Logo', 'Ticker', 'Empresa', 'Setor', 'Preço Atual', 'DY 12 Meses (%)', 'DY 5 Anos (%)', 'Market Cap (R$)', 'Score Total']):
        with cols[i]:
            st.markdown(f"**{col_name}**")
    for _, row in df_filtrado.iterrows():
        cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1.5, 1])
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

with tab2:
    st.header("Ranking Detalhado")
    st.markdown("Tabela detalhada com todos os indicadores das ações ranqueadas.")
    cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.5, 1, 1.5])
    for i, col_name in enumerate(['Logo', 'Ticker', 'Empresa', 'Setor', 'Tipo', 'Preço Atual', 'P/L', 'P/VP', 'ROE (%)', 
                                 'DY 12 Meses (%)', 'DY 5 Anos (%)', 'Último Dividendo (R$)', 'Data Últ. Div.', 'Data Ex-Div.', 
                                 'Payout Ratio (%)', 'Dívida Total', 'Dívida/EBITDA', 'Market Cap (R$)']):
        with cols[i]:
            st.markdown(f"**{col_name}**")
    for _, row in df_filtrado.iterrows():
        cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.5, 1, 1.5])
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

with tab3:
    st.header("Gráficos Interativos")
    st.markdown("Explore visualizações detalhadas das ações ranqueadas.")
    
    acao_selecionada = st.selectbox("Selecione uma ação para análise detalhada", df_filtrado['Ticker'].tolist())
    df_acao = df_filtrado[df_filtrado['Ticker'] == acao_selecionada].iloc[0]
    ticker_yf = yf.Ticker(f"{acao_selecionada}.SA")

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
    sentiment = get_sentiment_cache(acao_selecionada)
    fig6 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sentiment * 10,  # Convertido de 0-10 para 0-100 para o gauge
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
            if row['DY (Taxa 12m, %)'] > 5: detalhes.append("DY 12m > 5%: +20")
            elif row['DY (Taxa 12m, %)'] > 3.5: detalhes.append("DY 12m > 3.5%: +15")
            elif row['DY (Taxa 12m, %)'] > 2: detalhes.append("DY 12m > 2%: +10")
            elif row['DY (Taxa 12m, %)'] < 2: detalhes.append("DY 12m < 2%: -5")
            if row['DY 5 Anos Média (%)'] > 8: detalhes.append("DY 5y > 8%: +25")
            elif row['DY 5 Anos Média (%)'] > 6: detalhes.append("DY 5y > 6%: +20")
            elif row['DY 5 Anos Média (%)'] > 4: detalhes.append("DY 5y > 4%: +10")
            if 30 <= row['Payout Ratio (%)'] <= 60: detalhes.append("Payout 30-60%: +10")
            elif 60 < row['Payout Ratio (%)'] <= 80: detalhes.append("Payout 60-80%: +5")
            elif row['Payout Ratio (%)'] < 20 or row['Payout Ratio (%)'] > 80: detalhes.append("Payout <20% ou >80%: -5")
            if row['Setor (brapi)'].lower() == 'financeiro':
                if row['ROE (%)'] > 15: detalhes.append("ROE > 15% (Financeiro): +25")
                elif row['ROE (%)'] > 12: detalhes.append("ROE > 12% (Financeiro): +20")
                elif row['ROE (%)'] > 8: detalhes.append("ROE > 8% (Financeiro): +10")
            else:
                if row['ROE (%)'] > 12: detalhes.append("ROE > 12%: +15")
                elif row['ROE (%)'] > 8: detalhes.append("ROE > 8%: +5")
            if row['P/L'] > 0 and row['P/L'] < 12: detalhes.append("P/L < 12: +15")
            elif row['P/L'] < 18: detalhes.append("P/L < 18: +10")
            elif row['P/L'] > 25: detalhes.append("P/L > 25: -5")
            if row['P/VP'] < 0.66: detalhes.append("P/VP < 0.66: +20")
            elif row['P/VP'] < 1.5: detalhes.append("P/VP < 1.5: +10")
            elif row['P/VP'] < 2.5: detalhes.append("P/VP < 2.5: +5")
            elif row['P/VP'] > 4: detalhes.append("P/VP > 4: -5")
            if row['Setor (brapi)'].lower() != 'financeiro':
                debt_mc = row['Dívida Total'] / row['Market Cap (R$)'] if row['Market Cap (R$)'] > 0 else 0
                if debt_mc < 0.5: detalhes.append("Dívida/Market Cap < 0.5: +10")
                elif debt_mc < 1.0: detalhes.append("Dívida/Market Cap < 1.0: +5")
                elif debt_mc > 2.0: detalhes.append("Dívida/Market Cap > 2.0: -5")
                if row['Dívida/EBITDA'] < 1: detalhes.append("Dívida/EBITDA < 1: +10")
                elif row['Dívida/EBITDA'] < 2: detalhes.append("Dívida/EBITDA < 2: +5")
                elif row['Dívida/EBITDA'] > 6: detalhes.append("Dívida/EBITDA > 6: -5")
            if row['Crescimento Preço (%)'] > 15: detalhes.append("Crescimento Preço > 15%: +15")
            elif row['Crescimento Preço (%)'] > 10: detalhes.append("Crescimento Preço > 10%: +10")
            elif row['Crescimento Preço (%)'] > 5: detalhes.append("Crescimento Preço > 5%: +5")
            elif row['Crescimento Preço (%)'] < 0: detalhes.append("Crescimento Preço < 0%: -5")
            sentiment_score = get_sentiment_cache(row['Ticker'])
            if sentiment_score > 0: detalhes.append(f"Sentimento > 50: +{sentiment_score}")
            elif sentiment_score < 0: detalhes.append(f"Sentimento < 50: {sentiment_score}")
            for detalhe in detalhes:
                st.write(detalhe)

# Rodapé estilizado
st.markdown("""
---
<div style="text-align: center; font-size: 0.9rem; color: #666;">
    **Desenvolvido por Gustavo Lima** | Baseado nas melhores práticas de Luiz Barsi, Décio Bazin, Warren Buffett, Peter Lynch e Benjamin Graham | © 2025
</div>
""", unsafe_allow_html=True)