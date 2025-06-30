import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from io import StringIO
import base64

# Configuração da página
st.set_page_config(page_title="Investidor Inteligente - Bazin & Barsi", layout="wide", page_icon="📈")

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
st.title("Investidor Inteligente - Bazin & Barsi")
st.markdown("""
Bem-vindo ao **Investidor Inteligente**, um aplicativo para ranquear ações com base nas filosofias de **Luiz Barsi** e **Décio Bazin**. 
Priorizamos empresas com **Dividend Yield (DY)** consistente e fundamentos sólidos.
Use os filtros abaixo para personalizar o ranking, explorar gráficos interativos e conhecer as regras de investimento!
""")

# Carregar dados do CSV
try:
    df = pd.read_csv(r"E:\Github\finance-manager\data\relatorio_analise_b3.csv", index_col=0)
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
df['Tipo'] = df['Tipo'].map(tipo_traducao).fillna(df['Tipo'].str.capitalize())

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
colunas_percentual = ["DY (Taxa 12m, %)", "DY 5 Anos Média (%)", "ROE (%)", "Payout Ratio (%)"]
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

# Função para calcular o score (Bazin & Barsi) e retornar detalhes
def calcular_score(row):
    score = 0
    detalhes = []
    
    # DY 5 Anos Média (%)
    dy_5_anos = row['DY 5 Anos Média (%)']
    if dy_5_anos > 8:
        score += 40
        detalhes.append("DY 5 Anos Média > 8%: +40")
    elif dy_5_anos > 6:
        score += 30
        detalhes.append("DY 5 Anos Média > 6%: +30")
    elif dy_5_anos > 4:
        score += 10
        detalhes.append("DY 5 Anos Média > 4%: +10")
    
    # DY 12 meses (%)
    dy_12m = row['DY (Taxa 12m, %)']
    if dy_12m > 5:
        score += 15
        detalhes.append("DY 12 Meses > 5%: +15")
    elif dy_12m > 3.5:
        score += 10
        detalhes.append("DY 12 Meses > 3.5%: +10")
    elif dy_12m > 2:
        score += 5
        detalhes.append("DY 12 Meses > 2%: +5")
    elif dy_12m < 2:
        score -= 5
        detalhes.append("DY 12 Meses < 2%: -5")
    
    # Payout Ratio (%)
    payout = row['Payout Ratio (%)']
    if 30 <= payout <= 60:
        score += 15
        detalhes.append("Payout Ratio 30-60%: +15")
    elif 60 < payout <= 80:
        score += 5
        detalhes.append("Payout Ratio 60-80%: +5")
    elif payout > 80 or payout < 20:
        score -= 10
        detalhes.append("Payout Ratio <20% ou >80%: -10")
    
    # ROE (%)
    roe = row['ROE (%)']
    if roe > 12:
        score += 15
        detalhes.append("ROE > 12%: +15")
    elif roe > 8:
        score += 5
        detalhes.append("ROE > 8%: +5")
    
    # P/L
    pl = row['P/L']
    if pl > 0 and pl < 12:
        score += 15
        detalhes.append("P/L < 12: +15")
    elif pl < 18:
        score += 5
        detalhes.append("P/L < 18: +5")
    elif pl > 25:
        score -= 5
        detalhes.append("P/L > 25: -5")
    
    # P/VP
    pvp = row['P/VP']
    if pvp > 0 and pvp < 1.5:
        score += 10
        detalhes.append("P/VP < 1.5: +10")
    elif pvp < 2.5:
        score += 5
        detalhes.append("P/VP < 2.5: +5")
    elif pvp > 4:
        score -= 5
        detalhes.append("P/VP > 4: -5")
    
    # Dívida Total e Dívida/EBITDA (exceto bancos)
    if 'Financeiro' not in str(row['Setor (brapi)']).lower():
        divida = row['Dívida Total']
        market_cap = row['Market Cap (R$)']
        if divida > 0 and market_cap > 0:
            debt_ratio = divida / market_cap
            if debt_ratio < 0.5:
                score += 15
                detalhes.append("Dívida/Market Cap < 0.5: +15")
            elif debt_ratio < 1.0:
                score += 5
                detalhes.append("Dívida/Market Cap < 1.0: +5")
            elif debt_ratio > 2.0:
                score -= 5
                detalhes.append("Dívida/Market Cap > 2.0: -5")
        
        # Dívida/EBITDA
        if 'Dívida/EBITDA' in row:
            divida_ebitda = row['Dívida/EBITDA']
            if divida_ebitda > 0 and divida_ebitda < 2:
                score += 10
                detalhes.append("Dívida/EBITDA < 2: +10")
            elif divida_ebitda < 4:
                score += 5
                detalhes.append("Dívida/EBITDA < 4: +5")
            elif divida_ebitda > 6:
                score -= 5
                detalhes.append("Dívida/EBITDA > 6: -5")
    
    return score, detalhes

# Aplicar o score e armazenar detalhes
df[['Score', 'Detalhes Score']] = df.apply(calcular_score, axis=1, result_type='expand')

# Filtros interativos
st.sidebar.header("Filtros")
setores_disponiveis = sorted(df['Setor (brapi)'].unique().tolist())
setor_filtro = st.sidebar.multiselect("Selecione Setores", setores_disponiveis, default=setores_disponiveis)
dy_min = st.sidebar.slider("DY 12 Meses Mínimo (%)", 0.0, 20.0, 3.5, step=0.1)
score_min = st.sidebar.slider("Score Mínimo", 0, 135, 70, step=1)

# Filtro de ordenação
st.sidebar.header("Ordenação")
colunas_ordenacao = ['Score', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'P/L', 'P/VP', 'ROE (%)', 'Payout Ratio (%)']
coluna_ordenacao = st.sidebar.selectbox("Ordenar por", colunas_ordenacao)
ordem = st.sidebar.radio("Ordem", ["Decrescente (⬇)", "Crescente (⬆)"], index=0)
ascending = True if ordem == "Crescente (⬆)" else False

# Aplicar filtros
df_filtrado = df[
    (df['Setor (brapi)'].isin(setor_filtro)) & 
    (df['DY (Taxa 12m, %)'] >= dy_min) & 
    (df['Score'] >= score_min)
].sort_values(by=coluna_ordenacao, ascending=ascending)

# Abas para organização
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Ranking", "Ranking Detalhado", "Gráficos", "Regras de Investimento", "Detalhamento do Score"])

with tab1:
    st.header("Ranking")
    st.markdown("Tabela resumida com as principais métricas das ações ranqueadas com base nos critérios de Barsi e Bazin.")

    # Cabeçalho da tabela Ranking
    colunas_ranking = ['Logo', 'Ticker', 'Empresa', 'Setor', 'Preço Atual', 'DY 12 Meses (%)', 'DY 5 Anos (%)', 
                       'Market Cap (R$)', 'Score']
    cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1.5, 1])
    for i, col_name in enumerate(colunas_ranking):
        with cols[i]:
            st.markdown(f"**{col_name}**")

    # Tabela Ranking
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
            st.write(f"{row['Score']:.0f}")

with tab2:
    st.header("Ranking Detalhado")
    st.markdown("A tabela abaixo mostra as ações ranqueadas com base nos critérios de Barsi e Bazin. Clique nos logotipos para mais detalhes.")

    # Cabeçalho da tabela Ranking Detalhado
    colunas_ranking_detalhado = ['Logo', 'Ticker', 'Empresa', 'Setor', 'Tipo', 'Preço Atual', 'P/L', 'P/VP', 'ROE (%)', 
                       'DY 12 Meses (%)', 'DY 5 Anos (%)', 'Último Dividendo (R$)', 'Data Últ. Div.', 'Data Ex-Div.', 
                       'Payout Ratio (%)', 'Dívida Total', 'Dívida/EBITDA', 'Market Cap (R$)', 'Score']
    cols = st.columns([1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.5, 1, 1.5, 1])
    for i, col_name in enumerate(colunas_ranking_detalhado):
        with cols[i]:
            st.markdown(f"**{col_name}**")

    # Tabela Ranking Detalhado
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
            st.write(f"{row['Score']:.0f}")

with tab3:
    st.header("Gráficos Interativos")
    
    # Seletor de ação para análise individual e mapa de dividendos
    acao_selecionada = st.selectbox("Selecione uma ação para análise individual e mapa de dividendos", df_filtrado['Ticker'].tolist())
    df_acao = df_filtrado[df_filtrado['Ticker'] == acao_selecionada].iloc[0]
    
    # Gráfico 1: Evolução do Score (simulado)
    st.subheader("Evolução do Score (Simulação)")
    fig1 = px.line(
        df_filtrado,
        x=df_filtrado.index,
        y='Score',
        color='Setor (brapi)',
        title="Evolução do Score",
        labels={'index': 'Ações', 'Score': 'Score'}
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

with tab4:
    st.header("Regras de Investimento")
    st.markdown("""
    Este aplicativo utiliza as filosofias de **Luiz Barsi** e **Décio Bazin** para ranquear ações, focando em empresas com dividendos consistentes e fundamentos sólidos. Abaixo estão os critérios usados para calcular o **Score** de cada ação:

    ### Critérios de Pontuação
    - **Dividend Yield Médio de 5 Anos (DY 5 Anos Média)**:
        - **> 8%**: +40 pontos
        - **> 6%**: +30 pontos
        - **> 4%**: +10 pontos
    - **Dividend Yield dos Últimos 12 Meses (DY 12m)**:
        - **> 5%**: +15 pontos
        - **> 3.5%**: +10 pontos
        - **> 2%**: +5 pontos
        - **< 2%**: -5 pontos
    - **Payout Ratio** (Percentual do lucro distribuído como dividendos):
        - **30% a 60%**: +15 pontos (ideal para sustentabilidade)
        - **60% a 80%**: +5 pontos
        - **< 20% ou > 80%**: -10 pontos (insustentável ou retenção excessiva)
    - **ROE (Retorno sobre o Patrimônio Líquido)**:
        - **> 12%**: +15 pontos
        - **> 8%**: +5 pontos
    - **P/L (Preço/Lucro)**:
        - **< 12**: +15 pontos (ação subvalorizada)
        - **< 18**: +5 pontos
        - **> 25**: -5 pontos (ação potencialmente sobrevalorizada)
    - **P/VP (Preço/Valor Patrimonial)**:
        - **< 1.5**: +10 pontos (ação barata em relação ao patrimônio)
        - **< 2.5**: +5 pontos
        - **> 4**: -5 pontos (ação cara)
    - **Último Dividendo**:
        - **Pago nos últimos 6 meses**: +5 pontos (indica consistência recente)
    - **Dívida Total / Market Cap** (exceto setor Financeiro):
        - **< 0.5**: +15 pontos (endividamento baixo)
        - **< 1.0**: +5 pontos
        - **> 2.0**: -5 pontos (endividamento alto)
    - **Dívida/EBITDA** (exceto setor Financeiro):
        - **< 2**: +10 pontos (endividamento saudável)
        - **< 4**: +5 pontos
        - **> 6**: -5 pontos (endividamento arriscado)

    ### Filosofia por Trás
    - **Décio Bazin**: Foco em empresas com **Dividend Yield** alto e consistente, que pagam dividendos regularmente, indicando saúde financeira e retorno ao acionista.
    - **Luiz Barsi**: Prioriza empresas com fundamentos sólidos (baixo P/L, P/VP, alto ROE) e dividendos sustentáveis (Payout Ratio equilibrado).
    - **Exceção para o Setor Financeiro**: Dívida Total e Dívida/EBITDA não são considerados para bancos e instituições financeiras, pois o endividamento é parte do modelo de negócios.

    ### Como Usar
    - Use os filtros no sidebar para ajustar setores, DY mínimo (12 meses) e Score mínimo.
    - Ordene a tabela por colunas como Score, DY, P/L, etc., em ordem crescente (⬆) ou decrescente (⬇).
    - Explore os gráficos para visualizar padrões, como DY vs. P/L ou distribuição do Payout Ratio.
    - Consulte a aba "Detalhamento do Score" para ver como o Score de cada empresa foi calculado.
    """)

with tab5:
    st.header("Detalhamento do Score")
    st.markdown("Clique no nome da empresa para ver como o Score foi calculado com base nos critérios de Barsi e Bazin.")
    
    for _, row in df_filtrado.iterrows():
        with st.expander(f"{row['Ticker']} - {row['Empresa']} (Score: {row['Score']})"):
            st.markdown(f"### Detalhamento do Score para {row['Ticker']} - {row['Empresa']}")
            for detalhe in row['Detalhes Score']:
                st.write(f"- {detalhe}")
            st.markdown(f"**Score Total: {row['Score']}**")

# Rodapé com crédito
st.markdown("""
---
**Desenvolvido por Gustavo Lima.**  
**Baseado nas filosofias de Luiz Barsi e Décio Bazin.**
""")