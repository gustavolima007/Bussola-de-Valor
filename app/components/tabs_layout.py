# app/components/tabs_layout.py
import streamlit as st
import pandas as pd
import plotly.express as px
from .calculadora import render_tab_calculadora

# --- Funções para cada Aba ---

def style_dy(val):
    """Aplica cor verde para DY >= 6% e vermelho para < 6%."""
    if pd.isna(val):
        return ''
    color = '#3dd56d' if val >= 6 else '#ff4b4b'
    return f'color: {color}'

def style_alvo(val):
    """Aplica cor verde para Alvo >= 0 e vermelho para < 0."""
    if pd.isna(val):
        return ''
    color = '#3dd56d' if val >= 0 else '#ff4b4b'
    return f'color: {color}'

def render_tab_rank_geral(df: pd.DataFrame):
    st.header(f"🏆 Rank Geral ({len(df)} ações encontradas)")
    cols_to_display = ['Logo', 'Ticker', 'Empresa', 'Setor', 'Perfil da Ação', 'Preço Atual', 'Preço Teto 5A', 'Alvo', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'Score Total']
    df_display = df[[col for col in cols_to_display if col in df.columns]]
    
    st.dataframe(
        df_display.style.applymap(style_dy, subset=['DY 5 Anos Média (%)', 'DY (Taxa 12m, %)'])
                         .applymap(style_alvo, subset=['Alvo']),
        column_config={
            "Logo": st.column_config.ImageColumn("Logo"),
            "Preço Atual": st.column_config.NumberColumn("Preço Atual", format="R$ %.2f"),
            "Preço Teto 5A": st.column_config.NumberColumn("Preço Teto 5A", format="R$ %.2f"),
            "Alvo": st.column_config.NumberColumn("Alvo %", format="%.2f%%"),
            "DY (Taxa 12m, %)": st.column_config.NumberColumn("DY 12m", format="%.2f%%"),
            "DY 5 Anos Média (%)": st.column_config.NumberColumn("DY 5 Anos", format="%.2f%%"),
            "Score Total": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=200),
        },
        use_container_width=True, hide_index=True
    )

def render_tab_rank_detalhado(df: pd.DataFrame):
    st.header(f"📋 Ranking Detalhado ({len(df)} ações encontradas)")
    cols = [
        'Logo', 'Ticker', 'Empresa', 'Setor', 'Perfil da Ação', 'Preço Atual',
        'P/L', 'P/VP', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'Payout Ratio (%)',
        'ROE (%)', 'Dívida/EBITDA', 'Crescimento Preço (%)', 'Sentimento Gauge', 'Score Total'
    ]
    df_display = df[[c for c in cols if c in df.columns]]
    
    st.dataframe(
        df_display.style.applymap(style_dy, subset=['DY 5 Anos Média (%)', 'DY (Taxa 12m, %)']),
        column_config={
            "Logo": st.column_config.ImageColumn("Logo"),
            "Preço Atual": st.column_config.NumberColumn("Preço Atual", format="R$ %.2f"),
            "DY (Taxa 12m, %)": st.column_config.NumberColumn("DY 12m", format="%.2f%%"),
            "DY 5 Anos Média (%)": st.column_config.NumberColumn("DY 5 Anos", format="%.2f%%"),
            "Payout Ratio (%)": st.column_config.NumberColumn("Payout", format="%.1f%%"),
            "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
            "Dívida/EBITDA": st.column_config.NumberColumn("Dív/EBITDA", format="%.2f"),
            "Crescimento Preço (%)": st.column_config.NumberColumn("Cresc. 5A", format="%.1f%%"),
            "Sentimento Gauge": st.column_config.NumberColumn("Sentimento", format="%d/100"),
            "Score Total": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=200),
        },
        use_container_width=True, hide_index=True
    )

def render_tab_analise_individual(df: pd.DataFrame):
    st.header("🔬 Análise Individual e Composição do Score")
    if df.empty:
        st.info("Nenhuma ação encontrada com os filtros atuais para análise.")
        return

    ticker_selecionado = st.selectbox(
        "Selecione a Ação para Análise", df['Ticker'].tolist(),
        format_func=lambda t: f"{t} - {df.loc[df['Ticker'] == t, 'Empresa'].iloc[0]}"
    )
    if not ticker_selecionado:
        return

    acao = df[df['Ticker'] == ticker_selecionado].iloc[0]
    st.subheader(f"{acao['Empresa']} ({ticker_selecionado})")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Preço Atual", f"R$ {acao.get('Preço Atual', 0):.2f}")
    c2.metric("P/L", f"{acao.get('P/L', 0):.2f}")
    c3.metric("P/VP", f"{acao.get('P/VP', 0):.2f}")
    c4.metric("DY 12m", f"{acao.get('DY (Taxa 12m, %)', 0):.2f}%")
    c5.metric("Perfil", acao.get('Perfil da Ação', 'N/A'))

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Composição do Score")
        st.metric("Score Total", f"{acao.get('Score Total', 0):.0f} / 200")
        for detail in acao.get('Score Details', []):
            st.markdown(f"• {detail}")
    with c2:
        st.subheader("Sentimento dos Analistas")
        rec_cols = ['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']
        if all(col in acao.index for col in rec_cols) and acao[rec_cols].sum() > 0:
            rec_df = pd.DataFrame(acao[rec_cols]).reset_index()
            rec_df.columns = ['Recomendação', 'Contagem']
            fig = px.bar(rec_df, x='Contagem', y='Recomendação', orientation='h',
                         title='Distribuição das Recomendações', text='Contagem')
            fig.update_traces(marker_color='#D4AF37') # Cor dourada
            fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados de recomendação de analistas para este ativo.")

def render_tab_guia():
    st.header("🧭 Guia da Bússola de Valor")
    st.markdown("Entenda a metodologia por trás do score e dos conceitos de investimento baseados nos princípios de **Barsi, Bazin, Buffett, Lynch e Graham**.")

    st.subheader("Critérios de Pontuação (Score)")
    st.markdown("""
    A pontuação de cada ação é calculada somando-se os pontos de diversos critérios fundamentalistas, totalizando um máximo de **200 pontos**. Abaixo, detalhamos cada critério e sua relevância.
    """)

    with st.expander("1. Dividend Yield (DY) - Até 45 pontos"):
        st.markdown("""
        - **O que é?** O Dividend Yield (DY) representa o retorno em dividendos pago pela ação, dividido pelo seu preço. A média de 5 anos reflete a consistência dos pagamentos.
        - **Por que analisar?** É o principal indicador para investidores focados em renda passiva, como defendido por **Luiz Barsi**. Um DY alto e consistente indica uma "vaca leiteira" – empresas que geram fluxo de caixa estável.
        - **Cálculo do Score:**
            - **DY 12 meses:** 
                - > 5%: **+20 pontos**
                - 3.5%–5%: **+15 pontos**
                - 2%–3.5%: **+10 pontos**
                - < 2% (e > 0%): **-5 pontos**
            - **DY Média 5 Anos:** 
                - > 8%: **+25 pontos**
                - 6%–8%: **+20 pontos**
                - 4%–6%: **+10 pontos**
        """)

    with st.expander("2. Valuation (P/L e P/VP) - Até 35 pontos"):
        st.markdown("""
        - **O que são?** P/L (Preço/Lucro) e P/VP (Preço/Valor Patrimonial) são indicadores de valuation, popularizados por **Benjamin Graham**, para avaliar se uma ação está "barata" em relação aos lucros ou patrimônio.
        - **Por que analisar?** Comprar ativos abaixo de seu valor intrínseco é a essência do *Value Investing*, criando uma margem de segurança contra a volatilidade do mercado.
        - **Cálculo do Score:**
            - **P/L:**
                - < 12: **+15 pontos**
                - 12–18: **+10 pontos**
                - > 25: **-5 pontos**
            - **P/VP:**
                - < 0.66: **+20 pontos**
                - 0.66–1.5: **+10 pontos**
                - 1.5–2.5: **+5 pontos**
                - > 4: **-5 pontos**
        """)

    with st.expander("3. Rentabilidade e Gestão (ROE e Payout) - Até 35 pontos"):
        st.markdown("""
        - **O que são?** ROE (Return on Equity) mede a eficiência da empresa em gerar lucro com o capital próprio. Payout é a porcentagem do lucro distribuída como dividendos.
        - **Por que analisar?** Um ROE alto, valorizado por **Warren Buffett**, indica boa gestão e vantagens competitivas. Um Payout equilibrado mostra que a empresa remunera acionistas sem comprometer o reinvestimento.
        - **Cálculo do Score:**
            - **ROE (Setor Financeiro):**
                - > 15%: **+25 pontos**
                - 12%–15%: **+20 pontos**
                - 8%–12%: **+10 pontos**
            - **ROE (Outros Setores):**
                - > 12%: **+15 pontos**
                - 8%–12%: **+5 pontos**
            - **Payout:**
                - 30%–60%: **+10 pontos**
                - 60%–80%: **+5 pontos**
                - < 20% ou > 80%: **-5 pontos**
        """)

    with st.expander("4. Saúde Financeira (Endividamento) - Até 20 pontos"):
        st.markdown("""
        - **O que é?** Avalia a dívida da empresa em relação ao seu valor de mercado (Dívida/Market Cap) e geração de caixa (Dívida/EBITDA). *Não se aplica ao setor financeiro.*
        - **Por que analisar?** Empresas com dívidas controladas são mais resilientes a crises e têm maior flexibilidade para crescer e pagar dividendos, um princípio valorizado por **Bazin** e **Graham**.
        - **Cálculo do Score:**
            - **Dívida/Market Cap:**
                - < 0.5: **+10 pontos**
                - 0.5–1.0: **+5 pontos**
                - > 2.0: **-5 pontos**
            - **Dívida/EBITDA:**
                - < 1: **+10 pontos**
                - 1–2: **+5 pontos**
                - > 6: **-5 pontos**
        """)

    with st.expander("5. Crescimento e Sentimento - Até 25 pontos"):
        st.markdown("""
        - **O que são?** Crescimento do preço da ação nos últimos 5 anos e a recomendação consolidada de analistas (Sentimento Gauge).
        - **Por que analisar?** O crescimento histórico reflete a valorização do ativo, enquanto o sentimento de mercado, enfatizado por **Peter Lynch**, adiciona uma camada de análise sobre a percepção atual.
        - **Cálculo do Score:**
            - **Crescimento Preço 5 Anos:**
                - > 15%: **+15 pontos**
                - 10%–15%: **+10 pontos**
                - 5%–10%: **+5 pontos**
                - < 0%: **-5 pontos**
            - **Sentimento do Mercado:** 
                - Varia de **-5 a +10 pontos**, proporcional à nota de 0 a 100.
        """)

    st.markdown("---")
    st.subheader("Guia de Perfil da Ação")
    st.markdown("""
    A classificação por perfil ajuda a entender o porte, o risco e o potencial de cada empresa com base no **Valor de Mercado (Market Cap)** e **Preço por Ação**.
    """)
    with st.expander("Como o Perfil é Calculado?"):
        st.markdown("""
        - **Penny Stock:** Preço da Ação < R$ 1,00.
        - **Micro Cap:** Valor de Mercado < R$ 2 bilhões.
        - **Small Cap:** Valor de Mercado entre R$ 2 bilhões e R$ 10 bilhões.
        - **Mid Cap:** Valor de Mercado entre R$ 10 bilhões e R$ 50 bilhões.
        - **Blue Chip:** Valor de Mercado > R$ 50 bilhões.
        """)

def render_tab_insights(df: pd.DataFrame):
    st.header("✨ Insights Visuais")
    if df.empty:
        st.info("Nenhum dado para exibir com os filtros atuais.")
        return

    st.subheader("Top 15 por Score")
    top = df.nlargest(15, 'Score Total')
    fig_bar = px.bar(top.sort_values('Score Total'), x='Score Total', y='Ticker', orientation='h', color='Setor', hover_data=['Empresa'])
    fig_bar.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.divider()
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("DY 12m vs. P/L")
        fig = px.scatter(df, x='P/L', y='DY (Taxa 12m, %)', color='Setor', hover_data=['Ticker'])
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Distribuição de P/L (Histograma)")
        query_df = df.query("`P/L` > 0 and `P/L` < 50")
        fig_hist = px.histogram(query_df, x='P/L', nbins=30, title='Distribuição de P/L (0 a 50)')
        fig_hist.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.subheader("DY 5 anos vs. P/VP")
        fig = px.scatter(df, x='P/VP', y='DY 5 Anos Média (%)', color='Setor', hover_data=['Ticker'])
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Score por Setor (Boxplot)")
        fig_box = px.box(df, x='Setor', y='Score Total', title='Score por Setor')
        fig_box.update_layout(xaxis={'categoryorder':'total descending'}, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_box, use_container_width=True)

def render_tab_dividendos(all_data: dict):
    st.header("🔍 Análise de Dividendos")
    
    todos_dividendos = all_data.get('todos_dividendos', pd.DataFrame())
    dividendos_ano = all_data.get('dividendos_ano', pd.DataFrame())
    dividendos_ano_resumo = all_data.get('dividendos_ano_resumo', pd.DataFrame())
    dividend_yield_extra = all_data.get('dividend_yield', pd.DataFrame())

    if todos_dividendos.empty and dividendos_ano.empty:
        st.warning("Não foram encontrados dados de dividendos ('todos_dividendos.csv', 'dividendos_ano.csv').")
        return

    c1, c2 = st.columns([1, 1])
    with c1:
        if not todos_dividendos.empty:
            st.subheader("Série Temporal de Dividendos")
            tickers_opt = sorted(todos_dividendos['ticker_base'].dropna().unique().tolist())
            t_sel = st.selectbox("Selecione um ticker", tickers_opt, index=0)
            if t_sel:
                serie = todos_dividendos[todos_dividendos['ticker_base'] == t_sel]
                serie['Data'] = pd.to_datetime(serie['Data'], errors='coerce')
                fig_div = px.line(serie.sort_values('Data'), x='Data', y='Valor', title=f"Dividendos ao longo do tempo - {t_sel}")
                fig_div.update_layout(margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_div, use_container_width=True)
    with c2:
        if not dividendos_ano_resumo.empty:
            st.subheader("Top 20 Maiores Pagadores (12M)")
            top12 = dividendos_ano_resumo.nlargest(20, 'valor_12m')
            fig12 = px.bar(top12.sort_values('valor_12m'), x='valor_12m', y='ticker', orientation='h', title='Top 20: Dividendos Acumulados em 12 Meses')
            fig12.update_layout(margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig12, use_container_width=True)
            
    st.divider()
    
    if not dividend_yield_extra.empty:
        st.subheader("Relação DY 12m vs DY 5 anos")
        dyy = dividend_yield_extra.copy()
        dyy['DY12M'] = pd.to_numeric(dyy['DY12M'], errors='coerce')
        dyy['DY5anos'] = pd.to_numeric(dyy['DY5anos'], errors='coerce')
        dyy.dropna(subset=['DY12M','DY5anos'], inplace=True)
        fig_dy = px.scatter(dyy, x='DY12M', y='DY5anos', hover_data=['ticker'], title='Relação DY 12m x DY 5 anos (por ticker)')
        fig_dy.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_dy, use_container_width=True)

def render_tab_rank_setores(all_data: dict):
    st.header("🏗️ Rank de Setores")
    av_setor = all_data.get('avaliacao_setor', pd.DataFrame())
    if not av_setor.empty:
        av_display = av_setor.rename(columns={'setor_resumido': 'Setor', 'pontuacao': 'Pontuação'}).sort_values('Pontuação', ascending=False)
        st.dataframe(av_display[['Setor', 'Pontuação']], use_container_width=True, hide_index=True,
                     column_config={'Pontuação': st.column_config.NumberColumn('Pontuação', format='%.1f')})
        
        fig = px.bar(av_display.sort_values('Pontuação'), x='Pontuação', y='Setor', orientation='h', title='Ranking de Setores por Pontuação Média')
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Arquivo 'avaliacao_setor.csv' não encontrado para gerar o ranking.")
    
    st.divider()
    st.subheader("Análise Setorial (Foco em Dividendos)")
    st.markdown("""
    Abaixo, apresentamos uma análise detalhada de cada setor, ordenada por pontuação média, com motivos para investir e cuidados a serem considerados, especialmente para carteiras focadas em dividendos.
    """)

    # Dicionário com descrições de cada setor
    sector_descriptions = {
        "Petróleo, Gás e Biocombustíveis": {
            "Por que investir?": "Alta geração de caixa em períodos de preços elevados de commodities, com empresas frequentemente pagando dividendos robustos. Setor estratégico com demanda global constante.",
            "Por que não investir?": "Volatilidade ligada aos preços internacionais do petróleo e gás. Riscos regulatórios e impactos ambientais podem pressionar margens e gerar custos adicionais."
        },
        "Energia Elétrica e Saneamento": {
            "Por que investir?": "Demanda estável e previsível devido à essencialidade dos serviços. Contratos de concessão longos garantem receita recorrente, ideal para dividendos consistentes.",
            "Por que não investir?": "Forte regulação governamental e risco de interferência política. Altos investimentos em infraestrutura podem limitar o fluxo de caixa livre."
        },
        "Bancos, Seguros e Financeiros": {
            "Por que investir?": "Essenciais para a economia, com alta lucratividade e dividendos consistentes. Barreiras regulatórias protegem contra concorrência, favorecendo estabilidade.",
            "Por que não investir?": "Sensível a crises econômicas e flutuações nas taxas de juros. Concorrência de fintechs pode reduzir margens no longo prazo."
        },
        "Mineração e Siderurgia": {
            "Por que investir?": "Exposição a commodities globais, com potencial de lucros elevados em ciclos de alta. Empresas líderes frequentemente distribuem dividendos atrativos.",
            "Por que não investir?": "Alta volatilidade devido à dependência de preços internacionais. Custos elevados de operação e riscos ambientais podem impactar resultados."
        },
        "Papel, Química e Outros": {
            "Por que investir?": "Demanda constante por produtos essenciais, como papel e químicos industriais. Algumas empresas oferecem dividendos estáveis devido a operações consolidadas.",
            "Por que não investir?": "Exposição a custos de matéria-prima e energia. Concorrência global pode pressionar margens, especialmente em ciclos econômicos fracos."
        },
        "Serviços Industriais": {
            "Por que investir?": "Suporte a setores essenciais como construção e energia, com contratos de longo prazo que geram receita previsível e dividendos moderados.",
            "Por que não investir?": "Dependência de grandes projetos e ciclos econômicos. Margens geralmente mais baixas e sensibilidade a crises setoriais."
        },
        "Máquinas e Equipamentos Industriais": {
            "Por que investir?": "Demanda por equipamentos em setores de crescimento, como infraestrutura e manufatura. Empresas bem geridas podem oferecer dividendos estáveis.",
            "Por que não investir?": "Alta dependência de investimentos industriais e ciclos econômicos. Concorrência internacional pode limitar crescimento."
        },
        "Serviços Comerciais": {
            "Por que investir?": "Diversificação de serviços, incluindo consultoria e marketing, com algumas empresas oferecendo dividendos consistentes em nichos estáveis.",
            "Por que não investir?": "Alta concorrência e margens reduzidas. Dependência de contratos específicos pode levar a volatilidade nos lucros."
        },
        "Comércio Varejista": {
            "Por que investir?": "Demanda resiliente por bens de consumo, com algumas empresas oferecendo dividendos moderados. Setor beneficia-se de crescimento econômico.",
            "Por que não investir?": "Concorrência intensa, especialmente do e-commerce. Sensibilidade a mudanças no consumo e margens geralmente apertadas."
        },
        "Alimentos, Bebidas e Higiene": {
            "Por que investir?": "Demanda inelástica por produtos essenciais, garantindo receita estável. Empresas líderes pagam dividendos consistentes.",
            "Por que não investir?": "Concorrência global e pressão de custos de matéria-prima. Margens podem ser comprimidas por inflação ou mudanças regulatórias."
        },
        "Tecnologia – Hardware": {
            "Por que investir?": "Crescimento impulsionado pela digitalização e inovação tecnológica. Algumas empresas oferecem dividendos em nichos específicos.",
            "Por que não investir?": "Alta volatilidade e necessidade constante de inovação. Dividendos geralmente baixos devido ao foco em reinvestimento."
        },
        "Bens Duráveis (Eletro e Autos)": {
            "Por que investir?": "Demanda por eletrodomésticos e automóveis em mercados emergentes. Empresas consolidadas podem oferecer dividendos moderados.",
            "Por que não investir?": "Ciclos econômicos afetam fortemente a demanda. Concorrência global e custos elevados de produção limitam margens."
        },
        "Telefonia, Internet e Mídia": {
            "Por que investir?": "Serviço essencial na era digital, com receitas recorrentes via assinaturas. Barreiras de entrada protegem empresas estabelecidas.",
            "Por que não investir?": "Alta concorrência e necessidade de investimentos em tecnologias como 5G. Regulação intensa pode limitar lucros."
        },
        "Tecnologia – Software": {
            "Por que investir?": "Crescimento rápido devido à transformação digital. Modelos de assinatura geram receita recorrente em algumas empresas.",
            "Por que não investir?": "Dividendos raros devido ao foco em reinvestimento. Alta volatilidade e competição no setor tecnológico."
        },
        "Distribuição e Comércio": {
            "Por que investir?": "Demanda estável por bens essenciais, com algumas empresas oferecendo dividendos moderados devido a operações consolidadas.",
            "Por que não investir?": "Margens baixas e concorrência acirrada. Dependência de cadeias de suprimento pode gerar riscos operacionais."
        },
        "Saúde – Tecnologia e Equipamentos": {
            "Por que investir?": "Crescimento impulsionado por inovação e demanda por equipamentos médicos. Algumas empresas oferecem dividendos estáveis.",
            "Por que não investir?": "Altos custos de pesquisa e desenvolvimento. Dividendos limitados devido à necessidade de reinvestimento."
        },
        "Transporte e Logística": {
            "Por que investir?": "Essencial para cadeias globais de suprimento, com algumas empresas oferecendo dividendos em nichos estáveis como logística portuária.",
            "Por que não investir?": "Alta sensibilidade a custos de combustível e ciclos econômicos. Margens apertadas e necessidade de investimentos em infraestrutura."
        },
        "Saúde – Serviços Médicos": {
            "Por que investir?": "Demanda crescente por serviços de saúde, com receitas estáveis em hospitais e clínicas. Algumas empresas pagam dividendos moderados.",
            "Por que não investir?": "Regulação intensa e custos operacionais elevados. Concorrência e riscos legais podem impactar lucros."
        },
        "Serviços de Educação e Turismo": {
            "Por que investir?": "Crescimento em mercados emergentes e demanda por educação. Algumas empresas podem oferecer dividendos em nichos específicos.",
            "Por que não investir?": "Alta sensibilidade a crises econômicas e mudanças no comportamento do consumidor. Dividendos raros e margens geralmente baixas."
        }
    }

    # Exibir análise setorial ordenada pelo CSV
    if not av_setor.empty:
        for _, row in av_display.iterrows():
            setor = row['Setor']
            pontuacao = row['Pontuação']
            desc = sector_descriptions.get(setor, {
                "Por que investir?": "Informações específicas não disponíveis. Setor pode oferecer oportunidades dependendo das condições de mercado.",
                "Por que não investir?": "Riscos específicos não detalhados. Considere avaliar a volatilidade e a estabilidade de dividendos."
            })
            with st.expander(f"{setor} (Pontuação: {pontuacao:.2f})"):
                st.markdown(f"""
                - **Por que investir?** {desc['Por que investir?']}
                - **Por que não investir?** {desc['Por que não investir?']}
                """)
    else:
        st.warning("Não foi possível carregar as análises setoriais devido à ausência de dados no arquivo 'avaliacao_setor.csv'.")

# --- Função Principal de Renderização ---

from .calculadora import render_tab_calculadora

def render_tabs(df_filtrado: pd.DataFrame, all_data: dict, ticker_foco: str = None):
    """Cria e gerencia o conteúdo de todas as abas da aplicação."""
    tab_titles = [
        "🏆 Rank Geral", "📋 Rank Detalhado", "🔬 Análise Individual",
        "✨ Insights Visuais", "🔍 Análise de Dividendos", "🏗️ Rank Setores", "🧭 Guia da Bússola", "💰 Calculadora"
    ]
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(tab_titles)

    with tab1:
        render_tab_rank_geral(df_filtrado)
    with tab2:
        render_tab_rank_detalhado(df_filtrado)
    with tab3:
        render_tab_analise_individual(df_filtrado)
    with tab4:
        render_tab_insights(df_filtrado)
    with tab5:
        render_tab_dividendos(all_data)
    with tab6:
        render_tab_rank_setores(all_data)
    with tab7:
        render_tab_guia()
    with tab8:
        render_tab_calculadora(all_data, ticker_foco)