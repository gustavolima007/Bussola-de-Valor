# app/components/tabs_layout.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Funções para cada Aba ---

def style_dy(val):
    """Coloração DY conforme regras do usuário."""
    if pd.isna(val):
        return ''
    if val > 6:
        color = '#3dd56d'  # Verde
    elif 3 <= val <= 6:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_alvo(val):
    """Aplica cor verde para Alvo >= 0 e vermelho para < 0."""
    if pd.isna(val):
        return ''
    color = '#3dd56d' if val >= 0 else '#ff4b4b'
    return f'color: {color}'

def style_valorizacao(val):
    """Aplica cor verde para valorização positiva e vermelha para negativa."""
    if pd.isna(val):
        return ''
    color = '#3dd56d' if val > 0 else '#ff4b4b' if val < 0 else ''
    return f'color: {color}'

def style_graham(val):
    """Aplica cor baseada na margem de segurança Graham."""
    if pd.isna(val):
        return ''
    if val > 100:
        color = '#3dd56d'  # Verde
    elif val >= 0:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_pl(val):
    """Aplica cor baseada no P/L."""
    if pd.isna(val) or val <= 0:
        return ''
    if val < 15:
        color = '#3dd56d'  # Verde
    elif 15 <= val <= 20:
        color = '#ffaa00'  # Amarelo
    elif val > 25:
        color = '#ff4b4b'  # Vermelho
    else:
        color = ''
    return f'color: {color}'

def style_pvp(val):
    """Aplica cor baseada no P/VP."""
    if pd.isna(val) or val <= 0:
        return ''
    if val < 1.0:
        color = '#3dd56d'  # Verde
    elif 1.0 <= val <= 2.5:
        color = '#ffaa00'  # Amarelo
    elif val > 4.0:
        color = '#ff4b4b'  # Vermelho
    else:
        color = ''
    return f'color: {color}'

def style_payout(val):
    """Aplica cor baseada no Payout."""
    if pd.isna(val):
        return ''
    if 25 <= val <= 65:
        color = '#3dd56d'  # Verde
    elif 65 < val <= 85:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_roe(val):
    """Aplica cor baseada no ROE."""
    if pd.isna(val):
        return ''
    if val > 12:
        color = '#3dd56d'  # Verde
    elif 8 <= val <= 12:
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
    elif 0.5 <= val <= 1.0:
        color = '#ffaa00'  # Amarelo
    elif val > 1.5:
        color = '#ff4b4b'  # Vermelho
    else:
        color = ''
    return f'color: {color}'

def style_div_ebitda(val):
    """Aplica cor baseada na Dívida/EBITDA."""
    if pd.isna(val) or val < 0:
        return ''
    if val < 1.5:
        color = '#3dd56d'  # Verde
    elif 1.5 <= val <= 4:
        color = '#ffaa00'  # Amarelo
    elif val > 5:
        color = '#ff4b4b'  # Vermelho
    else:
        color = ''
    return f'color: {color}'

def style_cresc(val):
    """Aplica cor baseada no Crescimento Preço (5A)."""
    if pd.isna(val):
        return ''
    if val > 10:
        color = '#3dd56d'  # Verde
    elif 5 <= val <= 10:
        color = '#ffaa00'  # Amarelo
    elif val < 0:
        color = '#ff4b4b'  # Vermelho
    else:
        color = ''
    return f'color: {color}'

def style_pontuacao_final(val):
    """Score Total: Verde >=600, Amarelo 300-599, Vermelho <300"""
    if pd.isna(val):
        return ''
    if val >= 600:
        color = '#3dd56d'  # Verde
    elif 300 <= val < 600:
        color = '#ffaa00'  # Amarelo
    else:
        color = '#ff4b4b'  # Vermelho
    return f'color: {color}'

def style_ciclo_mercado(row: pd.Series, cols_to_style: list) -> list:
    """Aplica cor às colunas técnicas com base no status do ciclo de mercado."""
    status = row.get('status_ciclo', 'Observação')
    if status == 'Compra':
        color = '#3dd56d'  # Verde
    elif status == 'Venda':
        color = '#ff4b4b'  # Vermelho
    else: # Observação ou N/A
        color = '#ffaa00'  # Amarelo
    
    return [f'color: {color}' if col in cols_to_style else '' for col in row.index]

def style_pontuacao_final_setor(val):
    if pd.isna(val): return ''
    if val >= 415:
        return 'color: #15803d'  # Verde Escuro (Excelente)
    if 365 <= val < 415:
        return 'color: #3dd56d'  # Verde Claro (Muito bom)
    if 300 <= val < 365:
        return 'color: #ffaa00'  # Amarelo (Razoável)
    if 200 <= val < 300:
        return 'color: #ff7f50'  # Laranja (Fraco)
    return 'color: #ff4b4b'      # Vermelho (Ruim)

def style_score_dy_setor(val):
    if pd.isna(val): return ''
    if val >= 40: return 'color: #3dd56d'
    if 30 <= val < 40: return 'color: #58d68d'
    if 20 <= val < 30: return 'color: #ffaa00'
    if 0 <= val < 20: return 'color: #ff7f50'
    return 'color: #ff4b4b'

def style_score_roe_setor(val):
    if pd.isna(val): return ''
    if val >= 30: return 'color: #3dd56d'
    if 20 <= val < 30: return 'color: #58d68d'
    if 10 <= val < 20: return 'color: #ffaa00'
    return 'color: #ff4b4b'

def style_score_beta_setor(val):
    if pd.isna(val): return ''
    if val >= 20: return 'color: #3dd56d'
    if 10 <= val < 20: return 'color: #58d68d'
    if 0 <= val < 10: return 'color: #ffaa00'
    return 'color: #ff4b4b'

def style_score_payout_setor(val):
    if pd.isna(val): return ''
    if val >= 20: return 'color: #3dd56d'
    if 10 <= val < 20: return 'color: #58d68d'
    return 'color: #ff4b4b'

def style_score_empresas_boas_setor(val):
    if pd.isna(val): return ''
    if val >= 30: return 'color: #3dd56d'
    if 20 <= val < 30: return 'color: #58d68d'
    if 10 <= val < 20: return 'color: #ffaa00'
    return 'color: #ff4b4b'

def style_penalidade_empresas_ruins_setor(val):
    if pd.isna(val): return ''
    if val == 0: return 'color: #3dd56d'
    if val == -10: return 'color: #ffaa00'
    if val == -20: return 'color: #ff7f50'
    return 'color: #ff4b4b'

def style_score_graham_setor(val):
    if pd.isna(val): return ''
    if val >= 30: return 'color: #3dd56d'
    if 20 <= val < 30: return 'color: #58d68d'
    if 10 <= val < 20: return 'color: #ffaa00'
    return 'color: #ff4b4b'

def style_penalidade_rj_setor(val):
    if pd.isna(val): return ''
    if val == 0: return 'color: #3dd56d'
    if -20 <= val < 0: return 'color: #ffaa00'
    if -30 <= val < -20: return 'color: #ff7f50'
    return 'color: #ff4b4b'

def render_tab_rank_geral(df: pd.DataFrame):
    st.header(f"🏆 Ranking ({len(df)} ações encontradas)")
    cols_to_display = ['Logo', 'Ticker', 'Empresa', 'subsetor_b3', 'Perfil da Ação', 'Preço 1M', 'Val 1M', 'Preço 6M', 'Val 6M', 'Preço Atual', 'Preço Teto 5A', 'Alvo', 'margem_seguranca_percent', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'Score Total']
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
        
    val_cols_to_style = [c for c in ['Val 1M', 'Val 6M'] if c in df_cols]
    if val_cols_to_style:
        styler.map(style_valorizacao, subset=val_cols_to_style)

    st.dataframe(
        styler,
        column_config={
            "Logo": st.column_config.ImageColumn("Logo"),
            "Preço 1M": st.column_config.NumberColumn("Preço 1M", format="R$ %.2f"),
            "Val 1M": st.column_config.NumberColumn("Val 1M", format="%.2f%%"),
            "Preço 6M": st.column_config.NumberColumn("Preço 6M", format="R$ %.2f"),
            "Val 6M": st.column_config.NumberColumn("Val 6M", format="%.2f%%"),
            "Preço Atual": st.column_config.NumberColumn("Preço Atual", format="R$ %.2f"),
            "Preço Teto 5A": st.column_config.NumberColumn("Preço Teto 5A", format="R$ %.2f"),
            "Alvo": st.column_config.NumberColumn("Alvo %", format="%.2f%% "),
            "Margem de Segurança %": st.column_config.NumberColumn("Margem Segurança %", format="%.2f%%",),
            "DY (Taxa 12m, %)": st.column_config.NumberColumn("DY 12m", format="%.2f%% "),
            "DY 5 Anos Média (%)": st.column_config.NumberColumn("DY 5 Anos", format="%.2f%% "),
            "Score Total": st.column_config.ProgressColumn("Pontuação", format="%d", min_value=0, max_value=1000),
        },
        use_container_width=True, hide_index=True
    )

def render_tab_rank_detalhado(df: pd.DataFrame, df_unfiltered: pd.DataFrame):
    st.header(f"📊 Indicadores ({len(df)} ações encontradas)")
    cols = [
        'Logo', 'Ticker', 'Empresa', 'subsetor_b3', 'Perfil da Ação', 'Preço Atual', 'Preço Teto 5A', 'Alvo',
        'P/L', 'P/VP', 'margem_seguranca_percent', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)',
        'Payout Ratio (%)', 'ROE (%)', 'Dívida/Market Cap', 'Dívida/EBITDA', 'Crescimento Preço (%)',
        'Sentimento Gauge', 'rsi_14_1y', 'macd_diff_1y', 'volume_1y', 'Score Total'
    ]
    df_display = df[[c for c in cols if c in df.columns]].rename(columns={'subsetor_b3': 'Setor', 'margem_seguranca_percent': 'Margem de Segurança %'})
    
    styler = df_display.style
    df_cols = df_display.columns

    dy_cols_to_style = [c for c in ['DY 5 Anos Média (%)', 'DY (Taxa 12m, %)'] if c in df_cols]
    if dy_cols_to_style:
        styler.map(style_dy, subset=dy_cols_to_style)

    if 'Alvo' in df_cols:
        styler.map(style_alvo, subset=['Alvo'])

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

    # Aplica estilo baseado no ciclo de mercado
    tech_cols = ['rsi_14_1y', 'macd_diff_1y', 'volume_1y']
    if 'status_ciclo' in df.columns and all(c in df.columns for c in tech_cols):
        styler.apply(style_ciclo_mercado, cols_to_style=tech_cols, axis=1)

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
            "Payout Ratio (%)": st.column_config.NumberColumn("Payout", format="%.1f%% "),
            "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%% "),
            "Dívida/Market Cap": st.column_config.NumberColumn("Dív/MCap", format="%.2f"),
            "Dívida/EBITDA": st.column_config.NumberColumn("Dív/EBITDA", format="%.2f"),
            "Crescimento Preço (%)": st.column_config.NumberColumn("Cresc. 5A", format="%.1f%% "),
            "Sentimento Gauge": st.column_config.NumberColumn("Sentimento", format="%d/100"),
            "rsi_14_1y": st.column_config.NumberColumn("RSI (Sentimento)", format="%.2f"),
            "macd_diff_1y": st.column_config.NumberColumn("MACD (Tendência)", format="%.3f"),
            "volume_1y": st.column_config.NumberColumn("Volume (Convicção)", format="%d"),
            "Score Total": st.column_config.ProgressColumn("Pontuação", format="%d", min_value=0, max_value=1000),
        },
        use_container_width=True, 
        hide_index=True
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
                    <div data-testid="stMetricValue" style="font-size: 2rem; font-weight: 700; color: var(--secondary-color);">{acao.get('Score Total', 0):.0f} / 1000</div>
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
    
    st.subheader("Critérios de Pontuação (Score) - Máximo de 500 pontos")
    st.markdown('''
    A pontuação de cada ação é calculada somando-se os pontos de diversos critérios fundamentalistas, totalizando um máximo de **200 pontos**. Navegue pelas abas abaixo para detalhar cada critério.
    ''')

    tab_titles = [
        "1. Dividend Yield (45 pts)",
        "2. Valuation (35 pts)",
        "3. Rentabilidade (35 pts)", # TODO: Update total points in titles
        "4. Endividamento (20 pts)",
        "5. Crescimento (25 pts)",
        "6. Ciclo de Mercado (±15 pts)",
        "7. Fórmula de Graham (20 pts)"
    ]
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_titles)

    with tab1: # Dividend Yield
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
                - > 10%: **+30 pontos** (Excelente histórico)
                - 8%–10%: **+25 pontos** (Muito atrativo)
                - 6%–8%: **+20 pontos** (Bom histórico)
                - 4%–6%: **+10 pontos** (Regular)
        ''')

    with tab2: # Valuation
        st.markdown('''
        - **O que são?** P/L (Preço/Lucro) e P/VP (Preço/Valor Patrimonial) são indicadores de valuation, popularizados por **Benjamin Graham**, para avaliar se uma ação está \"barata\" em relação aos lucros ou patrimônio.
        - **Por que analisar?** Comprar ativos abaixo de seu valor intrínseco é a essência do *Value Investing*, criando uma margem de segurança contra a volatilidade do mercado.
        - **Cálculo do Score:**
            - **P/L:**
                - < 12: **+15 pontos**
                - 12–18: **+10 pontos** 
                - > 25: **-5 pontos**
            - **P/VP:**
                - < 0.50: **+45 pontos** (Extremamente descontada)
                - 0.50 – 0.66: **+40 pontos** (Muito abaixo do valor)
                - 0.66 – 1.00: **+30 pontos** (Abaixo do valor)
                - 1.00 – 1.50: **+15 pontos** (Próximo ao valor)
                - 1.50 – 2.50: **+5 pontos** (Leve sobrepreço)
                - > 4.00: **-10 pontos** (Potencial bolha)
        ''')

    with tab3: # Rentabilidade
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

    with tab4: # Endividamento
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

    with tab5: # Crescimento
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

    with tab6: # Ciclo de Mercado
        st.markdown('''
        - **O que é?** O **Ciclo de Mercado** usa indicadores técnicos (RSI, MACD, Volume) para avaliar o *timing* psicológico do mercado, identificando se o ativo está em um momento de euforia (venda) ou pânico (compra).
        - **Por que analisar?** Ajuda a responder **"quando comprar"**. Comprar ativos durante períodos de pessimismo extremo (pânico) historicamente oferece melhores pontos de entrada e maiores retornos potenciais.
        - **Cálculo do Score (Ciclo):**
            - Compra (Pânico): **+15 pontos**
            - Observação (Neutro): **0 pontos**
            - Venda (Euforia): **-15 pontos**
        ''')
    with tab7: # Fórmula de Graham
        st.markdown('''
        - **O que é?** A **Fórmula de Graham** calcula o \"preço justo\" de uma ação (`√(22.5 * LPA * VPA)`) e o compara com o preço atual para encontrar a **margem de segurança**.
        - **Por que analisar?** Ajuda a responder **\"o quê comprar\"**. Uma margem de segurança alta indica que a ação está sendo negociada bem abaixo de seu valor intrínseco, protegendo o investidor de perdas e aumentando o potencial de ganho.
        - **Cálculo do Score (Graham):**
            - Margem > 200%: **+40 pontos** (Barganha extrema)
            - 150% – 200%: **+35 pontos** (Excelente margem)
            - 100% – 150%: **+30 pontos** (Muito atrativo)
            - 50% – 100%: **+20 pontos** (Boa margem)
            - 20% – 50%: **+10 pontos** (Margem aceitável)
            - 0% – 20%: **+5 pontos** (Margem mínima)
            - < 0%: **-20 pontos** (Risco elevado)
        ''')

    st.markdown("---")
    st.subheader("Guia de Perfil da Ação")
    st.markdown('''
    A classificação por perfil ajuda a entender o porte, o risco e o potencial de cada empresa com base no **Valor de Mercado (Market Cap)** e **Preço por Ação**.
    ''')

    # Using columns for a card-like layout
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("##### 💎 Blue Chip")
            st.markdown("**Valor de Mercado > R$ 50 bilhões.**")
            st.markdown("_Empresas gigantes, líderes em seus setores, com alta liquidez e consideradas mais seguras._")

        with st.container(border=True):
            st.markdown("##### 📈 Mid Cap")
            st.markdown("**Valor de Mercado entre R$ 10 bilhões e R$ 50 bilhões.**")
            st.markdown("_Empresas de médio porte, com bom potencial de crescimento e risco moderado._")

        with st.container(border=True):
            st.markdown("##### 🚀 Small Cap")
            st.markdown("**Valor de Mercado entre R$ 2 bilhões e R$ 10 bilhões.**")
            st.markdown("_Empresas menores com alto potencial de crescimento, mas também maior risco e volatilidade._")

    with col2:
        with st.container(border=True):
            st.markdown("##### 🌱 Micro Cap")
            st.markdown("**Valor de Mercado < R$ 2 bilhões.**")
            st.markdown("_Empresas muito pequenas, com altíssimo potencial de valorização e risco elevado._")

        with st.container(border=True):
            st.markdown("##### 🪙 Penny Stock")
            st.markdown("**Preço da Ação < R$ 1,00.**")
            st.markdown("_Ações de baixíssimo valor, especulativas e com altíssimo risco. Podem ou não ser Micro Caps._")


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
            serie_foco['data'] = pd.to_datetime(serie_foco['data'], errors='coerce')
            serie_foco['Mes'] = serie_foco['data'].dt.month

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
            serie['data'] = pd.to_datetime(serie['data'], errors='coerce')
            fig_div = px.line(serie.sort_values('data'), x='data', y='valor', title=f"Dividendos ao longo do tempo - {ticker_foco}")
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
        dy_data['DY12m'] = pd.to_numeric(dy_data['DY12m'], errors='coerce').fillna(0)
        top12 = dy_data.nlargest(20, 'DY12m')
        fig12 = px.bar(top12.sort_values('DY12m'), 
                     x='DY12m', 
                     y='ticker', 
                     orientation='h', 
                     title='Top 20: Maiores DY 12 Meses', 
                     text='DY12m')
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
        "🏆 Ranking", "🔬 Análise",
        "🔍 Dividendos", "🏗️ Setores", "⚖️ Recuperação Judicial",
        "🧭 Guia da Bússola", "💰 Calculadora"
    ]
    tab1, tab_analise, tab_dividendos, tab_setores, tab_rj, tab_guia, tab_calculadora = st.tabs(tab_titles)

    with tab1:
        render_tab_rank_geral(df_filtrado)
        st.divider()
        render_tab_rank_detalhado(df_filtrado, df_unfiltered)
    with tab_analise:
        render_tab_analise_individual(df_filtrado)
    with tab_dividendos:
        render_tab_dividendos(df_filtrado, all_data, ticker_foco)
    with tab_setores:
        render_tab_rank_setores(df_unfiltered, df_filtrado, all_data)
    with tab_rj:
        render_tab_recuperacao_judicial(all_data)
    with tab_guia:
        render_tab_guia()
    with tab_calculadora:
        render_tab_calculadora(all_data, ticker_foco)
        
    

def render_tab_rank_setores(df_unfiltered: pd.DataFrame, df_filtrado: pd.DataFrame, all_data: dict):
    st.header("🏗️ Análise de Setores")

    av_setor = all_data.get('avaliacao_setor', pd.DataFrame())
    if not av_setor.empty:
        st.subheader("Ranking de Setores por Pontuação Média")
        st.markdown("Esta tabela classifica os subsetores com base em uma pontuação final que considera o desempenho médio de suas ações, a penalidade por recuperação judicial e o dividend yield médio dos últimos 5 anos.")

        # Define as colunas de pontuação e seus novos nomes
        rename_map = {
            'subsetor_b3': 'Setor',
            'pontuacao_final': 'Pont. Final',
            'score_original': 'Pont. Inicial',
            'score_dy': 'DY',
            'score_roe': 'ROE',
            'score_beta': 'Beta',
            'score_payout': 'Payout',
            'score_empresas_boas': 'Pont. > 150',
            'penalidade_empresas_ruins': 'Pont < 50',
            'score_graham': 'Graham',
            'penalidade_rj': 'Penalidade Recuperação Judicial'
        }
        
        av_display = av_setor.rename(columns=rename_map).sort_values(by='Pont. Final', ascending=False)

        # Define a ordem das colunas a serem exibidas
        cols_to_show = [
            'Setor', 'Pont. Final', 'Pont. Inicial',
            'DY', 'ROE', 'Beta', 'Payout',
            'Pont. > 150', 'Pont < 50', 'Graham', 'Penalidade Recuperação Judicial'
        ]
        
        # Filtra apenas as colunas que realmente existem no dataframe
        cols_to_show_existing = [col for col in cols_to_show if col in av_display.columns]
        
        styler = av_display[cols_to_show_existing].style.map(style_pontuacao_final_setor, subset=['Pont. Final'])
        styler.map(style_score_dy_setor, subset=['DY'])
        styler.map(style_score_roe_setor, subset=['ROE'])
        styler.map(style_score_beta_setor, subset=['Beta'])
        styler.map(style_score_payout_setor, subset=['Payout'])
        styler.map(style_score_empresas_boas_setor, subset=['Pont. > 150'])
        styler.map(style_penalidade_empresas_ruins_setor, subset=['Pont < 50'])
        styler.map(style_score_graham_setor, subset=['Graham'])
        styler.map(style_penalidade_rj_setor, subset=['Penalidade Recuperação Judicial'])

        # Configuração das colunas para o dataframe do Streamlit
        column_config = {
            'Pont. Final': st.column_config.NumberColumn('Pont. Final', format='%.1f', help="Pontuação final do subsetor, somando todos os critérios."),
            'Pont. Inicial': st.column_config.NumberColumn('Pont. Inicial', format='%.1f', help="Média da pontuação de todas as empresas do setor."),
            'DY': st.column_config.NumberColumn('DY', format='%.1f'),
            'ROE': st.column_config.NumberColumn('ROE', format='%.1f'),
            'Beta': st.column_config.NumberColumn('Beta', format='%.1f'),
            'Payout': st.column_config.NumberColumn('Payout', format='%.1f'),
            'Pont. > 150': st.column_config.NumberColumn('Pont. > 150', format='%.1f'),
            'Pont < 50': st.column_config.NumberColumn('Pont < 50', format='%.1f'),
            'Graham': st.column_config.NumberColumn('Graham', format='%.1f'),
            'Penalidade Recuperação Judicial': st.column_config.NumberColumn('Penalidade Recuperação Judicial', format='%.1f')
        }

        st.dataframe(
            styler,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        
        fig = px.bar(av_display, x='Pont. Final', y='Setor', orientation='h', title='<b>Desempenho Relativo dos Setores</b>')
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
            subsetor = row['Setor']
            pontuacao = row['Pont. Final']
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

    st.subheader("Como a penalidade é calculada?")
    st.markdown("A pontuação de cada setor é penalizada para refletir o risco com base no seu histórico de recuperações judiciais e falências.")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mínimo de ocorrências em um setor", f"{min_ocorrencias}")
    with col2:
        st.metric("Máximo de ocorrências em um setor", f"{max_ocorrencias}")

    st.markdown("""
    **Fórmula da Penalidade:**

    1.  **Normalização**: As ocorrências de cada setor são normalizadas para uma escala de 0 a 1.
        ```
        Penalidade Normalizada = (Ocorrências do Setor - Mínimo) / (Máximo - Mínimo)
        ```
    2.  **Ajuste**: A penalidade normalizada é multiplicada por um fator de impacto de **20 pontos**.
        ```
        Penalidade Ajustada = Penalidade Normalizada * 20
        ```
    3.  **Aplicação**: A penalidade ajustada é subtraída da pontuação original do setor.
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
