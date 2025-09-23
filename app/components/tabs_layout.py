# app/components/tabs_layout.py
import streamlit as st
import pandas as pd
import plotly.express as px

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

def style_graham(val):
    """Aplica cor baseada na margem de segurança Graham."""
    if pd.isna(val):
        return ''
    if val > 100:
        color = '#3dd56d'  # Verde para excepcional (>100%)
    elif val >= 50:
        color = '#3dd56d'  # Verde para muito boa (50-100%)
    elif val >= 20:
        color = '#ffaa00'  # Amarelo para boa (20-50%)
    elif val >= 0:
        color = '#ffaa00'  # Amarelo para aceitável (0-20%)
    else:
        color = '#ff4b4b'  # Vermelho para risco (<0%)
    return f'color: {color}'

def style_pl(val):
    """Aplica cor baseada no P/L."""
    if pd.isna(val) or val <= 0:
        return ''
    if val < 12:
        color = '#3dd56d'  # Verde
    elif val < 18:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_pvp(val):
    """Aplica cor baseada no P/VP."""
    if pd.isna(val) or val <= 0:
        return ''
    if val < 1.5:
        color = '#3dd56d'  # Verde
    elif val < 2.5:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_payout(val):
    """Aplica cor baseada no Payout."""
    if pd.isna(val):
        return ''
    if 30 <= val <= 80:
        color = '#3dd56d'  # Verde
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_roe(val):
    """Aplica cor baseada no ROE."""
    if pd.isna(val):
        return ''
    if val > 15:
        color = '#3dd56d'  # Verde
    elif val > 8:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_div_mc(val):
    """Aplica cor baseada na Dívida/Market Cap."""
    if pd.isna(val):
        return ''
    if val < 0.5:
        color = '#3dd56d'  # Verde
    elif val < 1.0:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_div_ebitda(val):
    """Aplica cor baseada na Dívida/EBITDA."""
    if pd.isna(val) or val < 0:
        return ''
    if val < 2:
        color = '#3dd56d'  # Verde
    elif val < 4:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_cresc(val):
    """Aplica cor baseada no Crescimento Preço (5A)."""
    if pd.isna(val):
        return ''
    if val > 15:
        color = '#3dd56d'  # Verde
    elif val > 5:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_pontuacao_final(val):
    """Aplica cor com base na Pontuação Final do Setor."""
    if pd.isna(val):
        return ''
    if val > 60:
        color = '#3dd56d'  # Verde
    elif val > 40:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def render_tab_rank_geral(df: pd.DataFrame):
    st.header(f"🏆 Ranking ({len(df)} ações encontradas)")
    cols_to_display = ['Logo', 'Ticker', 'Empresa', 'subsetor_b3', 'Perfil da Ação', 'Preço Atual', 'Preço Teto 5A', 'Alvo', 'margem_seguranca_percent', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'Score Total']
    df_display = df[[col for col in cols_to_display if col in df.columns]].rename(columns={'subsetor_b3': 'Setor', 'margem_seguranca_percent': 'Margem de Segurança %'})

    styler = df_display.style
    df_cols = df_display.columns

    dy_cols_to_style = [c for c in ['DY 5 Anos Média (%)', 'DY (Taxa 12m, %)'] if c in df_cols]
    if dy_cols_to_style:
        styler.map(style_dy, subset=dy_cols_to_style)

    if 'Alvo' in df_cols:
        styler.map(style_alvo, subset=['Alvo'])

    if 'Margem de Segurança %' in df_cols:
        styler.map(style_graham, subset=['Margem de Segurança %'])

    st.dataframe(
        styler,
        column_config={
            "Logo": st.column_config.ImageColumn("Logo"),
            "Preço Atual": st.column_config.NumberColumn("Preço Atual", format="R$ %.2f"),
            "Preço Teto 5A": st.column_config.NumberColumn("Preço Teto 5A", format="R$ %.2f"),
            "Alvo": st.column_config.NumberColumn("Alvo %", format="%.2f%% "),
            "Margem de Segurança %": st.column_config.NumberColumn("Margem Segurança %", format="%.2f%%",),
            "DY (Taxa 12m, %)": st.column_config.NumberColumn("DY 12m", format="%.2f%% "),
            "DY 5 Anos Média (%)": st.column_config.NumberColumn("DY 5 Anos", format="%.2f%% "),
            "Score Total": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=200),
        },
        use_container_width=True, hide_index=True
    )

def render_tab_rank_detalhado(df: pd.DataFrame):
    st.header(f"📋 Indices ({len(df)} ações encontradas)")
    cols = [
        'Logo', 'Ticker', 'Empresa', 'subsetor_b3', 'Perfil da Ação', 'Preço Atual',
        'P/L', 'P/VP', 'margem_seguranca_percent', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'Payout Ratio (%)',
        'ROE (%)', 'Dívida/Market Cap', 'Dívida/EBITDA', 'Crescimento Preço (%)', 'Sentimento Gauge', 'Score Total'
    ]
    df_display = df[[c for c in cols if c in df.columns]].rename(columns={'subsetor_b3': 'Setor', 'margem_seguranca_percent': 'Margem de Segurança %'})
    
    styler = df_display.style
    df_cols = df_display.columns

    dy_cols_to_style = [c for c in ['DY 5 Anos Média (%)', 'DY (Taxa 12m, %)'] if c in df_cols]
    if dy_cols_to_style:
        styler.map(style_dy, subset=dy_cols_to_style)

    if 'Margem de Segurança %' in df_cols:
        styler.map(style_graham, subset=['Margem de Segurança %'])
    
    if 'P/L' in df_cols:
        styler.map(style_pl, subset=['P/L'])

    if 'P/VP' in df_cols:
        styler.map(style_pvp, subset=['P/VP'])

    if 'Payout Ratio (%)' in df_cols:
        styler.map(style_payout, subset=['Payout Ratio (%)'])

    if 'ROE (%)' in df_cols:
        styler.map(style_roe, subset=['ROE (%)'])

    if 'Dívida/Market Cap' in df_cols:
        styler.map(style_div_mc, subset=['Dívida/Market Cap'])

    if 'Dívida/EBITDA' in df_cols:
        styler.map(style_div_ebitda, subset=['Dívida/EBITDA'])

    if 'Crescimento Preço (%)' in df_cols:
        styler.map(style_cresc, subset=['Crescimento Preço (%)'])

    st.dataframe(
        styler,
        column_config={
            "Logo": st.column_config.ImageColumn("Logo"),
            "Preço Atual": st.column_config.NumberColumn("Preço Atual", format="R$ %.2f"),
            "Margem de Segurança %": st.column_config.NumberColumn("Margem Segurança %", format="%.2f%%",),
            "DY (Taxa 12m, %)": st.column_config.NumberColumn("DY 12m", format="%.2f%% "),
            "DY 5 Anos Média (%)": st.column_config.NumberColumn("DY 5 Anos", format="%.2f%% "),
            "Payout Ratio (%)": st.column_config.NumberColumn("Payout", format="%.1f%% "),
            "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%% "),
            "Dívida/Market Cap": st.column_config.NumberColumn("Dív/MCap", format="%.2f"),
            "Dívida/EBITDA": st.column_config.NumberColumn("Dív/EBITDA", format="%.2f"),
            "Crescimento Preço (%)": st.column_config.NumberColumn("Cresc. 5A", format="%.1f%% "),
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
        with st.container():
            details_html = ""
            for detail in acao.get('Score Details', []):
                details_html += f"<p style='margin-bottom: 0.5rem;'>• {detail}</p>"

            card_content = f'''
            <div class="analise-individual-container">
                <div data-testid="stMetric" style="background-color: transparent; border: none; padding: 0; box-shadow: none;">
                    <label data-testid="stMetricLabel" style="color: var(--text-light-color);">Score Total</label>
                    <div data-testid="stMetricValue" style="font-size: 2rem; font-weight: 700; color: var(--secondary-color);">{acao.get('Score Total', 0):.0f} / 200</div>
                </div>
                {details_html}
            </div>
            '''
            st.markdown(card_content, unsafe_allow_html=True)

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
    st.markdown('''
    A pontuação de cada ação é calculada somando-se os pontos de diversos critérios fundamentalistas, totalizando um máximo de **200 pontos**. Abaixo, detalhamos cada critério e sua relevância.
    ''')

    with st.expander("1. Dividend Yield (DY) - Até 45 pontos"):
        st.markdown('''
        - **O que é?** O Dividend Yield (DY) representa o retorno em dividendos pago pela ação, dividido pelo seu preço. A média de 5 anos reflete a consistência dos pagamentos.
        - **Por que analisar?** É o principal indicador para investidores focados em renda passiva, como defendido por **Luiz Barsi**. Um DY alto e consistente indica uma \"vaca leiteira\" – empresas que geram fluxo de caixa estável.
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
        ''')

    with st.expander("2. Valuation (P/L e P/VP) - Até 35 pontos"):
        st.markdown('''
        - **O que são?** P/L (Preço/Lucro) e P/VP (Preço/Valor Patrimonial) são indicadores de valuation, popularizados por **Benjamin Graham**, para avaliar se uma ação está \"barata\" em relação aos lucros ou patrimônio.
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
        ''')

    with st.expander("3. Rentabilidade e Gestão (ROE e Payout) - Até 35 pontos"):
        st.markdown('''
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
        ''')

    with st.expander("4. Saúde Financeira (Endividamento) - Até 20 pontos"):
        st.markdown('''
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
        ''')

    with st.expander("5. Crescimento e Sentimento - Até 25 pontos"):
        st.markdown('''
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
        ''')

    with st.expander("6. Ciclo de Mercado e Fórmula de Graham - Até +35 pontos"):
        st.markdown('''
        - **O que são?** O **Ciclo de Mercado** usa indicadores técnicos (RSI, MACD, Volume) para avaliar o *timing* psicológico do mercado. A **Fórmula de Graham** calcula o \"preço justo\" (`√(22.5 * LPA * VPA)`) para encontrar a margem de segurança.
        - **Por que analisar?** Juntos, eles respondem \"o quê comprar\" (Graham) e \"quando comprar\" (Ciclo). Comprar ativos com alta margem de segurança durante períodos de pânico é uma estratégia poderosa.
        - **Cálculo do Score (Ciclo):**
            - Compra (Pânico): **+15 pontos**
            - Observação (Neutro): **0 pontos**
            - Venda (Euforia): **-15 pontos**
        - **Cálculo do Score (Graham):**
            - Margem > 100%: **+20 pontos**
            - Margem 50% a 100%: **+15 pontos**
            - Margem 20% a 50%: **+10 pontos**
            - Margem 0% a 20%: **+5 pontos**
            - Margem < 0%: **-10 pontos**
        ''')

    st.markdown("---")
    st.subheader("Guia de Perfil da Ação")
    st.markdown('''
A classificação por perfil ajuda a entender o porte, o risco e o potencial de cada empresa com base no **Valor de Mercado (Market Cap)** e **Preço por Ação**.
    ''')
    with st.expander("Como o Perfil é Calculado?"):
        st.markdown('''
        - **Penny Stock:** Preço da Ação < R$ 1,00.
        - **Micro Cap:** Valor de Mercado < R$ 2 bilhões.
        - **Small Cap:** Valor de Mercado entre R$ 2 bilhões e R$ 10 bilhões.
        - **Mid Cap:** Valor de Mercado entre R$ 10 bilhões e R$ 50 bilhões.
        - **Blue Chip:** Valor de Mercado > R$ 50 bilhões.
        ''')



def render_tab_dividendos(df: pd.DataFrame, all_data: dict, ticker_foco: str = None):
    st.header("🔍 Análise de Dividendos")
    
    todos_dividendos = all_data.get('todos_dividendos', pd.DataFrame())
    dividend_yield_extra = all_data.get('dividend_yield', pd.DataFrame())

    if dividend_yield_extra.empty:
        st.warning("Arquivo 'dividend_yield.csv' não encontrado ou vazio.")
        return

    # Filtra os dados de dividend yield com base nos tickers do dataframe filtrado principal
    filtered_tickers = df['Ticker'].unique()
    dy_data = dividend_yield_extra[dividend_yield_extra['ticker'].isin(filtered_tickers)].copy()

    st.subheader("Calendário de Dividendos por Mês")
    if not todos_dividendos.empty and ticker_foco:
        serie_foco = todos_dividendos[todos_dividendos['ticker_base'] == ticker_foco].copy()
        if not serie_foco.empty:
            serie_foco['Data'] = pd.to_datetime(serie_foco['Data'], errors='coerce')
            serie_foco['Mes'] = serie_foco['Data'].dt.month

            # Contar a frequência de dividendos por mês
            dividendos_por_mes = serie_foco['Mes'].value_counts().sort_index()
            
            # Criar DataFrame para o Plotly
            df_meses = pd.DataFrame({
                'Mes': range(1, 13),
                'Frequencia': [dividendos_por_mes.get(m, 0) for m in range(1, 13)]
            })
            
            # Mapear números dos meses para nomes
            nomes_meses = {
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            }
            df_meses['Nome_Mes'] = df_meses['Mes'].map(nomes_meses)

            fig_heatmap = px.bar(df_meses, 
                                 x='Nome_Mes', 
                                 y='Frequencia', 
                                 title=f"Frequência de Dividendos por Mês - {ticker_foco}",
                                 labels={'Nome_Mes': 'Mês', 'Frequencia': 'Número de Pagamentos'},
                                 color='Frequencia', # Adiciona calor baseado na frequência
                                 color_continuous_scale=px.colors.sequential.Plasma) # Escala de cor
            fig_heatmap.update_layout(margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info(f"Não há dados de dividendos para o ticker {ticker_foco}.")
    elif not ticker_foco:
        st.info("Selecione um ticker na barra lateral para ver a frequência de dividendos por mês.")
    else:
        st.warning("Dados de 'todos_dividendos.csv' não encontrados.")

    st.subheader("Série Temporal de Dividendos")
    if not todos_dividendos.empty and ticker_foco:
        serie = todos_dividendos[todos_dividendos['ticker_base'] == ticker_foco].copy()
        if not serie.empty:
            serie['Data'] = pd.to_datetime(serie['Data'], errors='coerce')
            fig_div = px.line(serie.sort_values('Data'), x='Data', y='Valor', title=f"Dividendos ao longo do tempo - {ticker_foco}")
            fig_div.update_layout(margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_div, use_container_width=True)
        else:
            st.info(f"Não há dados de dividendos para o ticker {ticker_foco}.")
    elif not ticker_foco:
        st.info("Selecione um ticker na barra lateral para ver a série temporal de dividendos.")
    else:
        st.warning("Dados de 'todos_dividendos.csv' não encontrados.")

    st.divider() 
    
    if not dy_data.empty:
        st.subheader("Top 20 Maiores Pagadores (12M)")
        dy_data['DY12M'] = pd.to_numeric(dy_data['DY12M'], errors='coerce').fillna(0)
        top12 = dy_data.nlargest(20, 'DY12M')
        fig12 = px.bar(top12.sort_values('DY12M'), 
                     x='DY12M', 
                     y='ticker', 
                     orientation='h', 
                     title='Top 20: Maiores DY 12 Meses', 
                     text='DY12M')
        fig12.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
        fig12.update_layout(margin=dict(l=20, r=20, t=50, b=20), 
                          xaxis_title="Dividend Yield (12M) %",
                          yaxis_title="Ticker")
        st.plotly_chart(fig12, use_container_width=True)

        st.subheader("Top 20 Maiores Pagadores (5 Anos)")
        dy_data['DY5anos'] = pd.to_numeric(dy_data['DY5anos'], errors='coerce').fillna(0)
        top_5y = dy_data.nlargest(20, 'DY5anos')
        fig_5y = px.bar(top_5y.sort_values('DY5anos'), 
                      x='DY5anos', 
                      y='ticker', 
                      orientation='h', 
                      title='Top 20: Maiores DY 5 Anos (Média)', 
                      text='DY5anos')
        fig_5y.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
        fig_5y.update_layout(margin=dict(l=20, r=20, t=50, b=20), 
                           xaxis_title="Dividend Yield (5 Anos Média) %",
                           yaxis_title="Ticker")
        st.plotly_chart(fig_5y, use_container_width=True)
    else:
        st.info("Nenhuma ação encontrada com os filtros atuais para exibir os gráficos de maiores pagadores.")
        
    

def render_tabs(df_unfiltered: pd.DataFrame, df_filtrado: pd.DataFrame, all_data: dict, ticker_foco: str = None):
    """Cria e gerencia o conteúdo de todas as abas da aplicação."""
    from .calculadora import render_tab_calculadora
    tab_titles = [
        "🏆 Ranking", "📋 Indices", "🔬 Análise",
        "🔍 Dividendos", "📈 Ciclo de mercado",
        "🏗️ Setores", "⚖️ Recuperação Judicial", "🧭 Guia da Bússola", "💰 Calculadora"
    ]
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(tab_titles)

    with tab1:
        render_tab_rank_geral(df_filtrado)
    with tab2:
        render_tab_rank_detalhado(df_filtrado)
    with tab3:
        render_tab_analise_individual(df_filtrado)
    with tab4:
        render_tab_dividendos(df_filtrado, all_data, ticker_foco)
    with tab5:
        render_tab_ciclo_mercado(df_unfiltered, all_data)
    with tab6:
        render_tab_rank_setores(df_filtrado, all_data)
    with tab7:
        render_tab_recuperacao_judicial(all_data)
    with tab8:
        render_tab_guia()
    with tab9:
        render_tab_calculadora(all_data, ticker_foco)
        
    

def render_tab_rank_setores(df_filtrado: pd.DataFrame, all_data: dict):
    st.header("🏗️ Análise de Setores")

    av_setor = all_data.get('avaliacao_setor', pd.DataFrame())
    if not av_setor.empty:
        st.subheader("Ranking de Setores por Pontuação Média")
        st.markdown("Esta tabela classifica os subsetores com base em uma pontuação final que considera o desempenho médio de suas ações, a penalidade por recuperação judicial e o dividend yield médio dos últimos 5 anos.")

        av_display = av_setor.rename(columns={
            'subsetor_b3': 'Subsetor',
            'pontuacao_original_subsetor': 'Pontuação Original',
            'penalidade_rj': 'Penalidade (RJ)',
            'dy_5a_subsetor': 'DY 5 Anos Setor (%)',
            'pontuacao_subsetor': 'Pontuação Final'
        }).sort_values('Pontuação Final', ascending=False)

        cols_to_show = ['Subsetor', 'Pontuação Original', 'Penalidade (RJ)', 'DY 5 Anos Setor (%)', 'Pontuação Final']
        if 'Pontuação Original' not in av_display.columns:
            cols_to_show.remove('Pontuação Original')
        if 'Penalidade (RJ)' not in av_display.columns:
            cols_to_show.remove('Penalidade (RJ)')
        if 'DY 5 Anos Setor (%)' not in av_display.columns:
            cols_to_show.remove('DY 5 Anos Setor (%)')

        styler = av_display[cols_to_show].style.map(style_pontuacao_final, subset=['Pontuação Final'])

        st.dataframe(
            styler,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Pontuação Original': st.column_config.NumberColumn('Pontuação Original', format='%.1f', help="Pontuação média dos ativos do setor, antes da penalidade."),
                'Penalidade (RJ)': st.column_config.NumberColumn('Penalidade', format='-%.1f', help="Penalidade subtraída da pontuação original devido ao histórico de RJs do setor."),
                'DY 5 Anos Setor (%)': st.column_config.NumberColumn('DY 5 Anos (%)', format='%.2f%%', help="Média do Dividend Yield dos últimos 5 anos para o setor."),
                'Pontuação Final': st.column_config.NumberColumn('Pontuação Final', format='%.1f', help="Pontuação final do setor após a aplicação da penalidade e bônus de dividendos.")
            }
        )
        
        fig = px.bar(av_display.sort_values('Pontuação Final'), x='Pontuação Final', y='Subsetor', orientation='h', title='<b>Desempenho Relativo dos Setores</b>')
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

    else:
        st.warning("Arquivo 'avaliacao_setor.csv' não encontrado para gerar o ranking.")

    # Adicionado Top 15 por Score
    if not df_filtrado.empty:
        st.subheader("Top 15 Ações por Score (Filtro Atual)")
        top = df_filtrado.nlargest(15, 'Score Total')
        fig_bar = px.bar(top.sort_values('Score Total'), x='Score Total', y='Ticker', orientation='h', color='subsetor_b3', hover_data=['Empresa'])
        fig_bar.update_layout(margin=dict(l=20, r=20, t=50, b=20), legend_title_text='Setor')
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.divider()
    st.subheader("Análise Qualitativa dos Setores (Foco em Dividendos)")
    st.markdown('''
Abaixo, apresentamos uma análise qualitativa de cada setor, com motivos para investir e pontos de atenção, especialmente para carteiras focadas em renda passiva.
    ''')

    # Dicionário com descrições de cada setor
    sector_descriptions = {
        "Petróleo, Gás e Biocombustíveis": {
            "Por que investir?": "Alta geração de caixa em períodos de preços elevados de commodities, com empresas frequentemente pagando dividendos robustos. Setor estratégico com demanda global constante.",
            "Por que não investir?": "Volatilidade ligada aos preços internacionais do petróleo e gás. Riscos regulatórios e impactos ambientais podem pressionar margens e gerar custos adicionais."
        },
        "Energia Elétrica": {
            "Por que investir?": "Demanda estável e previsível devido à essencialidade dos serviços. Contratos de concessão longos garantem receita recorrente, ideal para dividendos consistentes.",
            "Por que não investir?": "Forte regulação governamental e risco de interferência política. Altos investimentos em infraestrutura podem limitar o fluxo de caixa livre."
        },
        "Saneamento": {
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
            subsetor = row['Subsetor']
            pontuacao = row['Pontuação Final']
            desc = sector_descriptions.get(subsetor, {
                "Por que investir?": "Informações específicas não disponíveis. Setor pode oferecer oportunidades dependendo das condições de mercado.",
                "Por que não investir?": "Riscos específicos não detalhados. Considere avaliar a volatilidade e a estabilidade de dividendos."
            })
            with st.container(border=True):
                st.markdown(f"<h5>{subsetor} <span style='float: right; font-size: 0.9rem; color: #ffaa00;'>Pontuação: {pontuacao:.2f}</span></h5>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"✅ **Por que investir?**")
                    st.markdown(f"<p style='font-size: 0.9rem;'>{desc['Por que investir?']}</p>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"❌ **Por que não investir?**")
                    st.markdown(f"<p style='font-size: 0.9rem;'>{desc['Por que não investir?']}</p>", unsafe_allow_html=True)
    else:
        st.warning("Não foi possível carregar as análises setoriais devido à ausência de dados no arquivo 'avaliacao_setor.csv'.")
    
def render_tab_recuperacao_judicial(all_data: dict):
    st.header("⚖️ Recuperação Judicial e Falências")
    rj_df = all_data.get('rj', pd.DataFrame())
    setores_df = all_data.get('avaliacao_setor', pd.DataFrame())

    # Garante que todos os setores sejam exibidos, mesmo sem ocorrências
    if not setores_df.empty and 'subsetor_b3' in setores_df.columns:
        all_setores = pd.DataFrame(setores_df['subsetor_b3'].unique(), columns=['Setor'])
    else:
        st.warning("Arquivo 'avaliacao_setor.csv' não encontrado. A lista de setores pode estar incompleta.")
        all_setores = pd.DataFrame(rj_df['setor'].unique(), columns=['Setor']) if not rj_df.empty else pd.DataFrame(columns=['Setor'])

    if rj_df.empty:
        rj_counts = all_setores.copy()
        rj_counts['Quantidade de Ocorrências'] = 0
    else:
        ocorrencias = rj_df['setor'].value_counts().reset_index()
        ocorrencias.columns = ['Setor', 'Quantidade de Ocorrências']
        rj_counts = pd.merge(all_setores, ocorrencias, on='Setor', how='left')
        rj_counts['Quantidade de Ocorrências'].fillna(0, inplace=True)
        rj_counts['Quantidade de Ocorrências'] = rj_counts['Quantidade de Ocorrências'].astype(int)

    # --- Cálculo da Penalidade (para exibição) ---
    min_ocorrencias = rj_counts['Quantidade de Ocorrências'].min()
    max_ocorrencias = rj_counts['Quantidade de Ocorrências'].max()

    def calcular_penalidade(ocorrencias):
        if ocorrencias == 0 or (max_ocorrencias - min_ocorrencias) == 0:
            return 0.0
        penalidade_normalizada = (ocorrencias - min_ocorrencias) / (max_ocorrencias - min_ocorrencias)
        return penalidade_normalizada * 20  # Fator de impacto

    rj_counts['Penalidade (Pontos)'] = rj_counts['Quantidade de Ocorrências'].apply(calcular_penalidade)

    # Contar ocorrências por setor
    st.subheader("Ocorrências por Setor")
    st.dataframe(
        rj_counts.sort_values('Quantidade de Ocorrências', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Quantidade de Ocorrências": st.column_config.NumberColumn(
                "Ocorrências", format="%d", help="Número de vezes que empresas do setor entraram em RJ ou faliram."
            ),
            "Penalidade (Pontos)": st.column_config.NumberColumn(
                "Penalidade", format="%.2f", help="Penalidade aplicada ao score médio do setor devido ao histórico de RJs."
            ),
        }
    )

    with st.expander("Como a penalidade é calculada?"):
        st.markdown(f"""
A pontuação de cada setor é penalizada com base no seu histórico de recuperações judiciais e falências para refletir o risco setorial. A fórmula é:

        1.  **Contagem de Ocorrências**: Contamos quantas empresas de cada setor estão na nossa base de dados de RJ/Falência.
            - *Mínimo de ocorrências em um setor*: **{min_ocorrencias}**
            - *Máximo de ocorrências em um setor*: **{max_ocorrencias}**

        2.  **Penalidade Normalizada**: O número de ocorrências de um setor é normalizado em uma escala de 0 a 1.
            - `Penalidade Normalizada = (Ocorrências do Setor - Mínimo) / (Máximo - Mínimo)`

        3.  **Penalidade Ajustada**: A penalidade normalizada é multiplicada por um fator de impacto de **20 pontos**.
            - `Penalidade Ajustada = Penalidade Normalizada * 20`

        4.  **Pontuação Final do Setor**: A penalidade ajustada é subtraída da pontuação média original do setor.
        """)

    st.divider()
    st.subheader(f"Lista de Empresas ({len(rj_df)} encontradas)")

    if rj_df.empty:
        st.info("Nenhuma empresa na lista de recuperação judicial ou falência.")
        return

    # Seleciona e renomeia colunas para exibição
    cols_to_show = ['nome', 'ticker', 'setor', 'data_entrada_rj', 'data_saida_rj', 'data_falencia', 'duracao_rj']
    df_display = rj_df[[col for col in cols_to_show if col in rj_df.columns]].copy()
    df_display.rename(columns={
        'nome': 'Empresa',
        'ticker': 'Ticker',
        'setor': 'Setor',
        'data_entrada_rj': 'Início RJ',
        'data_saida_rj': 'Fim RJ',
        'data_falencia': 'Falência',
        'duracao_rj': 'Duração'
    }, inplace=True)

    # Formata as colunas de data
    for col in ['Início RJ', 'Fim RJ', 'Falência']:
        if col in df_display.columns:
            df_display[col] = pd.to_datetime(df_display[col], errors='coerce').dt.strftime('%d/%m/%Y')

    # Limpa valores nulos para exibição
    df_display.fillna('-', inplace=True)
    df_display['Ticker'] = df_display['Ticker'].replace({None: '-'})

    st.dataframe(
        df_display.sort_values(by='Início RJ', ascending=False),
        use_container_width=True,
        hide_index=True
    )

# --- Função Principal de Renderização ---

def render_tab_ciclo_mercado(df_unfiltered: pd.DataFrame, all_data: dict):
    st.header("📈 Ciclo de mercado")
    df_ciclo_raw = all_data.get('ciclo_mercado', pd.DataFrame())
    df_setor = all_data.get('avaliacao_setor', pd.DataFrame())

    if df_ciclo_raw.empty:
        st.warning("Arquivo 'ciclo_mercado.csv' não encontrado ou sem dados. Execute o pipeline ou o script 11-ciclo_mercado.py para gerar os dados.")
        return

    # Renomear coluna de status e fazer merge para obter o subsetor do df_unfiltered
    df_ciclo = df_ciclo_raw.rename(columns={'Status 🟢🔴': 'Status'})
    
    # Use df_unfiltered to get subsetor_b3 for all tickers
    ticker_col_name = 'Ticker' if 'Ticker' in df_unfiltered.columns else 'ticker_base' 
    
    if 'subsetor_b3' not in df_ciclo.columns and ticker_col_name in df_unfiltered.columns and 'subsetor_b3' in df_unfiltered.columns:
        df_ciclo = pd.merge(
            df_ciclo,
            df_unfiltered[[ticker_col_name, 'subsetor_b3']].drop_duplicates(),
            left_on='ticker',  # Coluna em df_ciclo (minúsculo)
            right_on=ticker_col_name, # Coluna em df_unfiltered (pode ser 'Ticker' ou 'ticker_base')
            how='left'         # Mantém todos os dados de ciclo
        )

    if 'subsetor_b3' not in df_ciclo.columns or df_ciclo['subsetor_b3'].isnull().all():
        st.warning("Não foi possível obter a informação de subsetor para os dados de ciclo de mercado.")
        # Mostra a tabela original como fallback
        with st.expander("Ver dados completos do Ciclo de Mercado"):
            st.dataframe(
                df_ciclo_raw,
                use_container_width=True,
                hide_index=True,
                column_config={"Score 📈": st.column_config.NumberColumn("Score 📈", format="%d")}
            )
        return

    # --- Criar a tabela de resumo ---
    st.subheader("Resumo do Status por Setor")
    
    # Contar os status por subsetor
    status_counts = pd.crosstab(df_ciclo['subsetor_b3'], df_ciclo['Status'])
    
    # Renomear colunas
    status_counts = status_counts.rename(columns={
        'Compra': 'qtde_compra',
        'Observação': 'qtde_observacao',
        'Venda': 'qtde_venda'
    })
    
    # Garantir que todas as colunas de status existam
    for col in ['qtde_compra', 'qtde_observacao', 'qtde_venda']:
        if col not in status_counts.columns:
            status_counts[col] = 0
            
    status_counts = status_counts.reset_index()

    # Preparar o dataframe de pontuação do setor
    if not df_setor.empty:
        df_setor_scores = df_setor[['subsetor_b3', 'pontuacao_subsetor']].drop_duplicates()
        summary_df = pd.merge(status_counts, df_setor_scores, on='subsetor_b3', how='left')
        summary_df = summary_df.rename(columns={
            'subsetor_b3': 'Subsetor',
            'pontuacao_subsetor': 'pontuação do setor'
        })
    else:
        summary_df = status_counts.rename(columns={'subsetor_b3': 'Subsetor'})
        summary_df['pontuação do setor'] = 'N/A'

    # Calcular o Momentum Score
    summary_df['total_ativos'] = summary_df['qtde_compra'] + summary_df['qtde_observacao'] + summary_df['qtde_venda']
    # Avoid division by zero
    summary_df['Momentum Score'] = summary_df.apply(
        lambda row: ((row['qtde_compra'] * 1) + (row['qtde_venda'] * -1)) / row['total_ativos'] if row['total_ativos'] != 0 else 0,
        axis=1
    )
    
    # Reordenar colunas
    summary_df = summary_df[['Subsetor', 'pontuação do setor', 'Momentum Score', 'qtde_compra', 'qtde_observacao', 'qtde_venda']]
    
    # Ordenar pela pontuação do setor
    if 'pontuação do setor' in summary_df.columns and pd.api.types.is_numeric_dtype(summary_df['pontuação do setor']):
        summary_df = summary_df.sort_values(by='pontuação do setor', ascending=False)


    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "pontuação do setor": st.column_config.NumberColumn("Pontuação", format="%.2f"),
            "Momentum Score": st.column_config.NumberColumn("Momentum", format="%.2f"),
            "qtde_compra": st.column_config.NumberColumn("Compra"),
            "qtde_observacao": st.column_config.NumberColumn("Observação"),
            "qtde_venda": st.column_config.NumberColumn("Venda"),
        }
    )

    st.divider()

    st.subheader("Dados completos do Ciclo de Mercado")
    st.dataframe(
        df_ciclo_raw,
        use_container_width=True,
        hide_index=True,
        column_config={"Score 📈": st.column_config.NumberColumn("Score 📈", format="%d")}
    )
