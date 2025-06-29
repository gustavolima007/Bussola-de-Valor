import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Configuração da página
st.set_page_config(page_title="Investidor Inteligente - Bazin & Barsi", layout="wide", page_icon="📈")

# Título e descrição
st.title("Investidor Inteligente - Bazin & Barsi")
st.markdown("""
Bem-vindo ao **Investidor Inteligente**, um aplicativo para ranquear ações com base nas filosofias de **Luiz Barsi** e **Décio Bazin**. 
Priorizamos empresas com **Dividend Yield (DY)** consistente, fundamentos sólidos e setores defensivos (energia, saneamento, bancos, seguros, telecomunicações).
Use os filtros abaixo para personalizar o ranking e explorar gráficos interativos!
""")

# Carregar dados do Excel
try:
    df = pd.read_excel(r"E:\Github\finance-manager\datasets\relatorio_analise_b3.xlsx", index_col=0)
except FileNotFoundError:
    st.error("Arquivo 'relatorio_analise_b3.xlsx' não encontrado. Execute o script de coleta de dados primeiro.")
    st.stop()

# Função para converter valores monetários (ex.: "R$ 98.50 Bi" -> 98500000000.0)
def parse_currency(value):
    if isinstance(value, str):
        try:
            # Remove "R$", "Bi", espaços e converte
            cleaned_value = value.replace('R$', '').replace('Bi', '').strip()
            # Multiplica por 1 bilhão se contém "Bi"
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

colunas_numericas = ["Preço Atual", "P/L", "P/VP", "Market Cap (R$)", "Último Dividendo (R$)"]
for col in colunas_numericas:
    if col in df.columns:
        df[col] = df[col].apply(parse_currency)

if "Dívida Total" in df.columns:
    df["Dívida Total"] = df["Dívida Total"].apply(parse_currency)

if "Dívida/EBITDA" in df.columns:
    df["Dívida/EBITDA"] = pd.to_numeric(df["Dívida/EBITDA"], errors='coerce').fillna(0)

# Converter colunas de data
colunas_data = ["Data Últ. Div.", "Data Ex-Div."]
for col in colunas_data:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], format='%d-%m-%Y', errors='coerce')

# Função para calcular o score (Bazin & Barsi)
def calcular_score(row):
    score = 0
    
    # DY 5 Anos Média (%)
    dy_5_anos = row['DY 5 Anos Média (%)']
    if dy_5_anos > 8:
        score += 40
    elif dy_5_anos > 6:
        score += 30
    elif dy_5_anos > 4:
        score += 10
    
    # DY 12 meses (%)
    dy_12m = row['DY (Taxa 12m, %)']
    if dy_12m > 5:
        score += 15
    elif dy_12m > 3.5:
        score += 10
    elif dy_12m > 2:
        score += 5
    elif dy_12m < 2:
        score -= 5
    
    # Payout Ratio (%)
    payout = row['Payout Ratio (%)']
    if 30 <= payout <= 60:
        score += 15
    elif 60 < payout <= 80:
        score += 5
    elif payout > 80 or payout < 20:
        score -= 10
    
    # ROE (%)
    roe = row['ROE (%)']
    if roe > 12:
        score += 15
    elif roe > 8:
        score += 5
    
    # P/L
    pl = row['P/L']
    if pl > 0 and pl < 12:
        score += 15
    elif pl < 18:
        score += 5
    elif pl > 25:
        score -= 5
    
    # P/VP
    pvp = row['P/VP']
    if pvp > 0 and pvp < 1.5:
        score += 10
    elif pvp < 2.5:
        score += 5
    elif pvp > 4:
        score -= 5
    
    # Setores defensivos
    setores_defensivos = ['ENERGIA', 'SANEAMENTO', 'FINANCEIRO', 'SEGUROS', 'TELECOMUNICAÇÕES']
    if any(setor in str(row['Setor (brapi)']).upper() for setor in setores_defensivos):
        score += 15
    
    # Data Últ. Div. (nos últimos 6 meses)
    data_ult_div = row['Data Últ. Div.']
    if pd.notna(data_ult_div) and (datetime.now() - data_ult_div).days <= 180:
        score += 5
    
    # Dívida Total e Dívida/EBITDA (exceto bancos)
    if 'FINANCEIRO' not in str(row['Setor (brapi)']).upper():
        divida = row['Dívida Total']
        market_cap = row['Market Cap (R$)']
        if divida > 0 and market_cap > 0:
            debt_ratio = divida / market_cap
            if debt_ratio < 0.5:
                score += 15
            elif debt_ratio < 1.0:
                score += 5
            elif debt_ratio > 2.0:
                score -= 5
        
        # Dívida/EBITDA
        if 'Dívida/EBITDA' in row:
            divida_ebitda = row['Dívida/EBITDA']
            if divida_ebitda > 0 and divida_ebitda < 2:
                score += 10
            elif divida_ebitda < 4:
                score += 5
            elif divida_ebitda > 6:
                score -= 5
    
    return score

# Aplicar o score
df['Score'] = df.apply(calcular_score, axis=1)

# Filtrar empresas com score mínimo e DY 5 anos > 6%
df_ranking = df[(df['Score'] >= 70) & (df['DY 5 Anos Média (%)'] > 6)].sort_values(by='Score', ascending=False)

# Filtros interativos
st.sidebar.header("Filtros")
setores_disponiveis = df['Setor (brapi)'].unique().tolist()
setor_filtro = st.sidebar.multiselect("Selecione Setores", setores_disponiveis, default=setores_disponiveis)
dy_min = st.sidebar.slider("DY 12 Meses Mínimo (%)", 0.0, 10.0, 3.5)
score_min = st.sidebar.slider("Score Mínimo", 0, 100, 70)

# Aplicar filtros
df_filtrado = df_ranking[df_ranking['Setor (brapi)'].isin(setor_filtro) & (df_ranking['DY (Taxa 12m, %)'] >= dy_min) & (df_ranking['Score'] >= score_min)]

# Abas para organização
tab1, tab2 = st.tabs(["Ranking de Ações", "Gráficos"])

with tab1:
    st.header("Ranking de Ações")
    st.markdown("A tabela abaixo mostra as ações ranqueadas com base nos critérios de Barsi e Bazin. Clique nos logotipos para mais detalhes.")

    # Tabela com logotipos
    for _, row in df_filtrado.iterrows():
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1, 2, 2, 1, 1, 1, 1, 1, 1, 1])
        with col1:
            if row['Logo'] != 'N/A' and isinstance(row['Logo'], str):
                try:
                    st.image(row['Logo'], width=50)
                except:
                    st.write("Logo N/A")
            else:
                st.write("Logo N/A")
        with col2:
            st.write(row['Empresa'])
        with col3:
            st.write(row['Setor (brapi)'])
        with col4:
            st.write(f"{row['DY (Taxa 12m, %)']:.2f}%")
        with col5:
            st.write(f"{row['DY 5 Anos Média (%)']:.2f}%")
        with col6:
            st.write(f"{row['P/L']:.2f}")
        with col7:
            st.write(f"{row['P/VP']:.2f}")
        with col8:
            st.write(f"{row['ROE (%)']:.2f}%")
        with col9:
            st.write(f"{row['Payout Ratio (%)']:.2f}%")
        with col10:
            st.write(f"{row['Score']:.0f}")

with tab2:
    st.header("Gráficos Interativos")
    
    # Gráfico 1: DY 5 Anos vs. P/L
    fig1 = px.scatter(
        df_filtrado,
        x='P/L',
        y='DY 5 Anos Média (%)',
        color='Setor (brapi)',
        size='Score',
        hover_data=['Empresa', 'ROE (%)', 'Payout Ratio (%)'],
        title="DY 5 Anos Média vs. P/L",
        labels={'P/L': 'Preço/Lucro', 'DY 5 Anos Média (%)': 'DY Médio 5 Anos (%)'}
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico 2: Score por Empresa
    fig2 = px.bar(
        df_filtrado,
        x='Empresa',
        y='Score',
        color='Setor (brapi)',
        title="Score por Empresa",
        text='Score'
    )
    fig2.update_traces(textposition='auto')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Gráfico 3: Distribuição do Payout Ratio
    fig3 = px.histogram(
        df_filtrado,
        x='Payout Ratio (%)',
        nbins=20,
        title="Distribuição do Payout Ratio",
        labels={'Payout Ratio (%)': 'Payout Ratio (%)'}
    )
    st.plotly_chart(fig3, use_container_width=True)

# Rodapé
st.markdown("""
---
**Desenvolvido por Grok 3 | xAI**  
Baseado nas filosofias de Luiz Barsi e Décio Bazin. Dados de: `relatorio_analise_b3.xlsx`.
""")