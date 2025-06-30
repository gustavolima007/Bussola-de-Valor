import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Configuração da página
st.set_page_config(page_title="Investidor Inteligente - Filosofias de Investimento", layout="wide", page_icon="📈")

# CSS para responsividade
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
</style>
""", unsafe_allow_html=True)

# Título e descrição
st.title("Investidor Inteligente - Filosofias de Investimento")
st.markdown("""
Bem-vindo ao **Investidor Inteligente**, um aplicativo para ranquear ações e fundos com base nas filosofias de **Luiz Barsi**, **Décio Bazin**, **Warren Buffett**, **Peter Lynch** e **Benjamin Graham**. 
Priorizamos empresas com **Dividend Yield** consistente, fundamentos sólidos e valor intrínseco. Use os filtros abaixo para personalizar o ranking, explorar gráficos interativos e conhecer as regras de investimento!
""")

# Carregar dados do CSV
try:
    df = pd.read_csv(r"E:\finance-manager\data\relatorio_analise_b3.csv", index_col=0)
except FileNotFoundError:
    st.error("Arquivo 'relatorio_analise_b3.csv' não encontrado. Execute o script de coleta de dados primeiro.")
    st.stop()

# Adicionar coluna Ticker e remover .SA
df['Ticker'] = df.index.str.replace('.SA', '')

# Mapeamento de setores para português brasileiro com primeira letra maiúscula
setores_traducao = {
    'Finance': 'Financeiro',
    'Utilities': 'Serviços públicos',
    'Communications': 'Comunicações',
    'Industrial Services': 'Serviços industriais',
}
df['Setor (brapi)'] = df['Setor (brapi)'].map(setores_traducao).fillna(df['Setor (brapi)']).str.capitalize()

# Mapeamento de Tipo para português com primeira letra maiúscula
tipo_traducao = {
    'stock': 'Ações',
    'fund': 'Fundos'
}
df['Tipo'] = df['Tipo'].map(tipo_traducao).fillna(df['Tipo']).str.capitalize()

# Função para converter valores monetários (ex.: "R$ 98.50 Bi" -> 98500000000.0)
def parse_currency(value):
    if isinstance(value, str):
        try:
            cleaned_value = value.replace('R$', '').replace('Bi', '').strip()
            multiplier = 1_000_000_000 if 'Bi' in value else 1
            return float(cleaned_value) * multiplier
        except:
            return 0.0
    return float(value) if pd.notna(value) else 0.0

# Função para converter percentuais (ex.: "6.50%" -> 6.50)
def parse_percent(value):
    if isinstance(value, str) and '%' in value:
        try:
            return float(value.replace('%', ''))
        except:
            return 0.0
    return float(value) if pd.notna(value) else 0.0

# Converter colunas para numérico
colunas_percentual = ["DY (Taxa 12m, %)", "DY 5 Anos Média (%)", "ROE (%)", "Payout Ratio (%)", "Crescimento Preço (%)"]
for col in colunas_percentual:
    if col in df.columns:
        df[col] = df[col].apply(parse_percent)

colunas_numericas = ["Preço Atual", "P/L", "P/VP", "Market Cap (R$)", "Último Dividendo (R$)", "Dívida Total"]
for col in colunas_numericas:
    if col in df.columns:
        df[col] = df[col].apply(parse_currency)

if "Dívida/EBITDA" in df.columns:
    df["Dívida/EBITDA"] = pd.to_numeric(df["Dívida/EBITDA"], errors='coerce').fillna(0)

# Converter colunas de data
colunas_data = ["Data Últ. Div.", "Data Ex-Div."]
for col in colunas_data:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], format='%d-%m-%Y', errors='coerce')

# Função para calcular os scores com base nas filosofias
def calcular_scores(row):
    # Score Bazin & Barsi
    score_barsi = 0
    detalhes_barsi = []
    if row['DY 5 Anos Média (%)'] > 8: score_barsi += 40; detalhes_barsi.append("DY 5 Anos > 8%: +40")
    elif row['DY 5 Anos Média (%)'] > 6: score_barsi += 30; detalhes_barsi.append("DY 5 Anos > 6%: +30")
    elif row['DY 5 Anos Média (%)'] > 4: score_barsi += 10; detalhes_barsi.append("DY 5 Anos > 4%: +10")
    if row['DY (Taxa 12m, %)'] > 5: score_barsi += 15; detalhes_barsi.append("DY 12m > 5%: +15")
    elif row['DY (Taxa 12m, %)'] > 3.5: score_barsi += 10; detalhes_barsi.append("DY 12m > 3.5%: +10")
    elif row['DY (Taxa 12m, %)'] > 2: score_barsi += 5; detalhes_barsi.append("DY 12m > 2%: +5")
    elif row['DY (Taxa 12m, %)'] < 2: score_barsi -= 5; detalhes_barsi.append("DY 12m < 2%: -5")
    if 30 <= row['Payout Ratio (%)'] <= 60: score_barsi += 15; detalhes_barsi.append("Payout 30-60%: +15")
    elif 60 < row['Payout Ratio (%)'] <= 80: score_barsi += 5; detalhes_barsi.append("Payout 60-80%: +5")
    elif row['Payout Ratio (%)'] > 80 or row['Payout Ratio (%)'] < 20: score_barsi -= 10; detalhes_barsi.append("Payout <20% ou >80%: -10")
    if row['ROE (%)'] > 12: score_barsi += 15; detalhes_barsi.append("ROE > 12%: +15")
    elif row['ROE (%)'] > 8: score_barsi += 5; detalhes_barsi.append("ROE > 8%: +5")
    if row['P/L'] > 0 and row['P/L'] < 12: score_barsi += 15; detalhes_barsi.append("P/L < 12: +15")
    elif row['P/L'] < 18: score_barsi += 5; detalhes_barsi.append("P/L < 18: +5")
    elif row['P/L'] > 25: score_barsi -= 5; detalhes_barsi.append("P/L > 25: -5")
    if row['P/VP'] > 0 and row['P/VP'] < 1.5: score_barsi += 10; detalhes_barsi.append("P/VP < 1.5: +10")
    elif row['P/VP'] < 2.5: score_barsi += 5; detalhes_barsi.append("P/VP < 2.5: +5")
    elif row['P/VP'] > 4: score_barsi -= 5; detalhes_barsi.append("P/VP > 4: -5")
    if 'Financeiro' not in str(row['Setor (brapi)']).lower():
        if row['Dívida Total'] > 0 and row['Market Cap (R$)'] > 0:
            debt_ratio = row['Dívida Total'] / row['Market Cap (R$)']
            if debt_ratio < 0.5: score_barsi += 15; detalhes_barsi.append("Dívida/Market Cap < 0.5: +15")
            elif debt_ratio < 1.0: score_barsi += 5; detalhes_barsi.append("Dívida/Market Cap < 1.0: +5")
            elif debt_ratio > 2.0: score_barsi -= 5; detalhes_barsi.append("Dívida/Market Cap > 2.0: -5")
        if row['Dívida/EBITDA'] > 0 and row['Dívida/EBITDA'] < 2: score_barsi += 10; detalhes_barsi.append("Dívida/EBITDA < 2: +10")
        elif row['Dívida/EBITDA'] < 4: score_barsi += 5; detalhes_barsi.append("Dívida/EBITDA < 4: +5")
        elif row['Dívida/EBITDA'] > 6: score_barsi -= 5; detalhes_barsi.append("Dívida/EBITDA > 6: -5")

    # Score Buffett
    score_buffett = 0
    detalhes_buffett = []
    if row['P/L'] < 15: score_buffett += 15; detalhes_buffett.append("P/L < 15: +15")
    if row['P/VP'] < 1.5: score_buffett += 10; detalhes_buffett.append("P/VP < 1.5: +10")
    if row['Market Cap (R$)'] > 10_000_000_000: score_buffett += 5; detalhes_buffett.append("Market Cap > 10B: +5")  # Proxy para moat
    score_buffett = min(score_buffett, 30)

    # Score Lynch
    score_lynch = 0
    detalhes_lynch = []
    if row['Crescimento Preço (%)'] > 15: score_lynch += 10; detalhes_lynch.append("Crescimento Preço > 15%: +10")
    peg = row['P/L'] / (row['Crescimento Preço (%)'] / 100) if row['Crescimento Preço (%)'] > 0 else 999
    if peg < 1: score_lynch += 10; detalhes_lynch.append("PEG < 1: +10")
    score_lynch = min(score_lynch, 20)

    # Score Graham
    score_graham = 0
    detalhes_graham = []
    if row['P/VP'] < 0.66: score_graham += 20; detalhes_graham.append("P/VP < 0.66: +20")
    if row['Dívida/EBITDA'] < 1 and 'Financeiro' not in str(row['Setor (brapi)']).lower(): score_graham += 10; detalhes_graham.append("Dívida/EBITDA < 1: +10")
    score_graham = min(score_graham, 30)

    # Sentimento do Mercado (corrigido para lidar com KeyError)
    ticker_yf = yf.Ticker(f"{row['Ticker']}.SA")
    recommendations = ticker_yf.recommendations
    sentiment_score = 0
    if not recommendations.empty:
        if 'To Grade' in recommendations.columns:
            sentiment_score = (recommendations['To Grade'].value_counts().reindex(['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'], fill_value=0) * [2, 1, 0, -1, -2]).sum() / len(recommendations) if len(recommendations) > 0 else 0
        else:
            sentiment_score = 0  # Valor padrão se a coluna não existir
    sentiment_gauge = sentiment_score * 50 + 50  # 0-100

    return score_barsi, detalhes_barsi, score_buffett, detalhes_buffett, score_lynch, detalhes_lynch, score_graham, detalhes_graham, sentiment_gauge

# Aplicar os scores
df[['Score Barsi', 'Detalhes Barsi', 'Score Buffett', 'Detalhes Buffett', 'Score Lynch', 'Detalhes Lynch', 'Score Graham', 'Detalhes Graham', 'Sentimento Gauge']] = df.apply(calcular_scores, axis=1, result_type='expand')

# Filtros interativos
st.sidebar.header("Filtros")
setores_disponiveis = sorted(df['Setor (brapi)'].unique().tolist())
setor_filtro = st.sidebar.multiselect("Selecione Setores", setores_disponiveis, default=setores_disponiveis)
dy_min = st.sidebar.slider("DY 12 Meses Mínimo (%)", 0.0, 20.0, 3.5, step=0.1)
score_min = st.sidebar.slider("Score Mínimo (Barsi)", 0, 135, 70, step=1)

# Filtro de ordenação
st.sidebar.header("Ordenação")
colunas_ordenacao = ['Score Barsi', 'Score Buffett', 'Score Lynch', 'Score Graham', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'P/L', 'P/VP', 'ROE (%)', 'Payout Ratio (%)']
coluna_ordenacao = st.sidebar.selectbox("Ordenar por", colunas_ordenacao)
ordem = st.sidebar.radio("Ordem", ["Decrescente (⬇)", "Crescente (⬆)"], index=0)
ascending = True if ordem == "Crescente (⬆)" else False

# Aplicar filtros
df_filtrado = df[
    (df['Setor (brapi)'].isin(setor_filtro)) & 
    (df['DY (Taxa 12m, %)'] >= dy_min) & 
    (df['Score Barsi'] >= score_min)
].sort_values(by=coluna_ordenacao, ascending=ascending)

# Abas para organização
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Ranking", "Ranking Detalhado", "Gráficos", "Filosofias de Investimento", "Detalhamento dos Scores"])

with tab1:
    st.header("Ranking")
    st.markdown("Tabela resumida com as principais métricas das ações ranqueadas com base nos critérios de Barsi e Bazin.")
    cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1.5, 1])
    for i, col_name in enumerate(['Logo', 'Ticker', 'Empresa', 'Setor', 'Preço Atual', 'DY 12 Meses (%)', 'DY 5 Anos (%)', 'Market Cap (R$)', 'Score Barsi']):
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
            st.write(f"{row['Score Barsi']:.0f}")

with tab2:
    st.header("Ranking Detalhado")
    st.markdown("Tabela detalhada com todos os indicadores das ações ranqueadas.")
    cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.5, 1, 1.5, 1, 1, 1, 1])
    for i, col_name in enumerate(['Logo', 'Ticker', 'Empresa', 'Setor', 'Tipo', 'Preço Atual', 'P/L', 'P/VP', 'ROE (%)', 
                                 'DY 12 Meses (%)', 'DY 5 Anos (%)', 'Último Dividendo (R$)', 'Data Últ. Div.', 'Data Ex-Div.', 
                                 'Payout Ratio (%)', 'Dívida Total', 'Dívida/EBITDA', 'Market Cap (R$)', 'Score Barsi', 
                                 'Score Buffett', 'Score Lynch', 'Score Graham']):
        with cols[i]:
            st.markdown(f"**{col_name}**")
    for _, row in df_filtrado.iterrows():
        cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.5, 1, 1.5, 1, 1, 1, 1])
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
            st.write(f"{row['Score Barsi']:.0f}")
        with cols[19]:
            st.write(f"{row['Score Buffett']:.0f}")
        with cols[20]:
            st.write(f"{row['Score Lynch']:.0f}")
        with cols[21]:
            st.write(f"{row['Score Graham']:.0f}")

with tab3:
    st.header("Gráficos Interativos")
    st.markdown("Explore visualizações detalhadas das ações ranqueadas.")
    
    # Seletor de ação para análise individual e mapa de dividendos
    acao_selecionada = st.selectbox("Selecione uma ação para análise individual e mapa de dividendos", df_filtrado['Ticker'].tolist())
    df_acao = df_filtrado[df_filtrado['Ticker'] == acao_selecionada].iloc[0]
    ticker_yf = yf.Ticker(f"{acao_selecionada}.SA")

    # Gráfico 1: Evolução do Score
    st.subheader("Evolução do Score (Barsi)")
    fig1 = px.line(
        df_filtrado,
        x=df_filtrado.index,
        y='Score Barsi',
        color='Setor (brapi)',
        title="Evolução do Score Barsi",
        labels={'index': 'Ações', 'Score Barsi': 'Score'}
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico 2: Análise Individual de Ação
    st.subheader(f"Análise Individual de {acao_selecionada}")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=['Atual'], y=[df_acao['DY (Taxa 12m, %)']], mode='lines+markers', name='DY 12m (%)'))
    fig2.add_trace(go.Scatter(x=['Atual'], y=[df_acao['P/L']], mode='lines+markers', name='P/L'))
    fig2.add_trace(go.Scatter(x=['Atual'], y=[df_acao['ROE (%)']], mode='lines+markers', name='ROE (%)'))
    fig2.update_layout(
        title=f"Métricas de {acao_selecionada}",
        xaxis_title="Período",
        yaxis_title="Valor",
        legend_title="Métricas"
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Gráfico 3: Candlestick Simulado
    st.subheader("Candlestick Simulado (Baseado em Preço Atual)")
    fig3 = go.Figure(data=[go.Candlestick(
        x=df_filtrado['Ticker'],
        open=[df_acao['Preço Atual']] * len(df_filtrado),
        high=[df_acao['Preço Atual'] * 1.05] * len(df_filtrado),
        low=[df_acao['Preço Atual'] * 0.95] * len(df_filtrado),
        close=[df_acao['Preço Atual']] * len(df_filtrado)
    )])
    fig3.update_layout(title="Candlestick Simulado", xaxis_title="Ações", yaxis_title="Preço (R$)")
    st.plotly_chart(fig3, use_container_width=True)
    
    # Gráfico 4: Correlação P/L vs. DY 12m
    st.subheader("Correlação P/L vs. DY 12m")
    fig4 = px.scatter(
        df_filtrado,
        x='P/L',
        y='DY (Taxa 12m, %)',
        color='Setor (brapi)',
        trendline="ols",
        title="Correlação entre P/L e DY 12m",
        labels={'P/L': 'Preço/Lucro', 'DY (Taxa 12m, %)': 'DY 12 Meses (%)'}
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    # Gráfico 5: DY 12 Meses por Empresa
    st.subheader("DY 12 Meses por Empresa")
    fig5 = px.bar(
        df_filtrado,
        x='Empresa',
        y='DY (Taxa 12m, %)',
        color='Setor (brapi)',
        title="DY 12 Meses por Empresa",
        text='DY (Taxa 12m, %)'
    )
    fig5.update_traces(textposition='auto')
    st.plotly_chart(fig5, use_container_width=True)
    
    # Gráfico 6: Último Dividendo por Empresa
    st.subheader("Último Dividendo por Empresa")
    fig6 = px.bar(
        df_filtrado,
        x='Empresa',
        y='Último Dividendo (R$)',
        color='Setor (brapi)',
        title="Último Dividendo por Empresa",
        text='Último Dividendo (R$)'
    )
    fig6.update_traces(textposition='auto')
    st.plotly_chart(fig6, use_container_width=True)
    
    # Gráfico 7: Mapa de Dividendos Passado e Futuros
    st.subheader("Mapa de Dividendos Passado e Futuros")
    df_acao_div = df_filtrado[df_filtrado['Ticker'] == acao_selecionada]
    ultima_data_div = df_acao['Data Últ. Div.']
    ultimo_dividendo = df_acao['Último Dividendo (R$)']
    dy_12m = df_acao['DY (Taxa 12m, %)']
    preco_atual = df_acao['Preço Atual']
    
    # Passado: Baseado em Data Últ. Div. e Último Dividendo
    datas_passado = [ultima_data_div] if pd.notna(ultima_data_div) else []
    valores_passado = [ultimo_dividendo] if pd.notna(ultimo_dividendo) else []
    
    # Futuro: Estimativa baseada em DY 12m e frequência anual simplificada
    if pd.notna(ultima_data_div) and pd.notna(dy_12m) and pd.notna(preco_atual) and preco_atual > 0:
        dividendo_estimado = (dy_12m / 100) * preco_atual
        datas_futuro = [ultima_data_div + relativedelta(months=6), ultima_data_div + relativedelta(months=12)]
        valores_futuro = [dividendo_estimado] * 2  # Simulação de dois próximos dividendos
    else:
        datas_futuro = []
        valores_futuro = []
    
    fig7 = go.Figure()
    if datas_passado and valores_passado:
        fig7.add_trace(go.Scatter(x=datas_passado, y=valores_passado, mode='lines+markers', name='Dividendos Passados'))
    if datas_futuro and valores_futuro:
        fig7.add_trace(go.Scatter(x=datas_futuro, y=valores_futuro, mode='markers', name='Dividendos Futuros (Estimados)'))
    
    fig7.update_layout(
        title=f"Mapa de Dividendos de {acao_selecionada}",
        xaxis_title="Data",
        yaxis_title="Valor do Dividendo (R$)",
        legend_title="Tipo",
        xaxis=dict(range=[(ultima_data_div - relativedelta(months=6)).date() if pd.notna(ultima_data_div) else datetime(2024, 1, 1).date(), 
                          (ultima_data_div + relativedelta(months=18)).date() if pd.notna(ultima_data_div) else datetime(2026, 1, 1).date()])
    )
    st.plotly_chart(fig7, use_container_width=True)
    
    # Gráfico 8: Velocímetro de Sentimento de Mercado
    st.subheader("Velocímetro de Sentimento de Mercado")
    fig8 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=df_acao['Sentimento Gauge'],
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 100]},
               'steps': [
                   {'range': [0, 20], 'color': 'red'},
                   {'range': [20, 40], 'color': 'orange'},
                   {'range': [40, 60], 'color': 'yellow'},
                   {'range': [60, 80], 'color': 'lightgreen'},
                   {'range': [80, 100], 'color': 'green'}
               ],
               'bar': {'color': "gray"}}
    ))
    st.plotly_chart(fig8, use_container_width=True)

with tab4:
    st.header("Filosofias de Investimento")
    st.markdown("""
### Descrições das Filosofias
- **Luiz Barsi**: Investidor brasileiro renomado por sua estratégia de "comprar para guardar", focando em empresas com dividendos altos e consistentes, baixo P/L e P/VP, e ROE elevado, com horizonte de longo prazo.
- **Décio Bazin**: Economista e investidor que enfatiza empresas com Dividend Yield elevado e pagamentos regulares de dividendos, como sinal de saúde financeira e retorno ao acionista.
- **Warren Buffett**: Um dos maiores investidores do mundo, busca empresas com "moat" (vantagem competitiva sustentável), P/L e P/VP baixos, e crescimento de longo prazo, valorizando o valor intrínseco.
- **Peter Lynch**: Defensor de investir em empresas que o investidor compreende, priorizando crescimento de vendas/lucros acima da média (PEG < 1) e preços razoáveis em relação ao crescimento.
- **Benjamin Graham**: Considerado o pai do value investing, foca em ações subvalorizadas (P/VP < 0.66) com baixa dívida (Dívida/EBITDA < 1) e estabilidade financeira.

### Critérios de Pontuação
- **Barsi & Bazin**:
  - **Dividend Yield Médio de 5 Anos**: > 8%: +40, > 6%: +30, > 4%: +10
  - **Dividend Yield 12 Meses**: > 5%: +15, > 3.5%: +10, > 2%: +5, < 2%: -5
  - **Payout Ratio**: 30-60%: +15, 60-80%: +5, <20% ou >80%: -10
  - **ROE**: > 12%: +15, > 8%: +5
  - **P/L**: < 12: +15, < 18: +5, > 25: -5
  - **P/VP**: < 1.5: +10, < 2.5: +5, > 4: -5
  - **Dívida/Market Cap** (exceto Financeiro): < 0.5: +15, < 1.0: +5, > 2.0: -5
  - **Dívida/EBITDA** (exceto Financeiro): < 2: +10, < 4: +5, > 6: -5
- **Buffett**:
  - P/L < 15: +15
  - P/VP < 1.5: +10
  - Market Cap > 10B: +5 (máximo 30)
- **Lynch**:
  - Crescimento Preço > 15%: +10
  - PEG < 1: +10 (máximo 20)
- **Graham**:
  - P/VP < 0.66: +20
  - Dívida/EBITDA < 1: +10 (máximo 30)
- **Sentimento**: Baseado em recomendações (0-100, verde > 80, vermelho < 20)
""")

with tab5:
    st.header("Detalhamento dos Scores")
    st.markdown("Clique no nome da empresa para ver como os scores foram calculados com base nas filosofias de investimento.")
    for _, row in df_filtrado.iterrows():
        with st.expander(f"{row['Ticker']} - {row['Empresa']}"):
            st.markdown(f"### Detalhamento dos Scores para {row['Ticker']} - {row['Empresa']}")
            st.markdown(f"**Score Barsi: {row['Score Barsi']}**")
            for detalhe in row['Detalhes Barsi']:
                st.write(f"- {detalhe}")
            st.markdown(f"**Score Buffett: {row['Score Buffett']}**")
            for detalhe in row['Detalhes Buffett']:
                st.write(f"- {detalhe}")
            st.markdown(f"**Score Lynch: {row['Score Lynch']}**")
            for detalhe in row['Detalhes Lynch']:
                st.write(f"- {detalhe}")
            st.markdown(f"**Score Graham: {row['Score Graham']}**")
            for detalhe in row['Detalhes Graham']:
                st.write(f"- {detalhe}")

# Rodapé com crédito
st.markdown("""
---
**Desenvolvido por Gustavo Lima.**
**Baseado nas filosofias de Luiz Barsi, Décio Bazin, Warren Buffett, Peter Lynch e Benjamin Graham.**
""")