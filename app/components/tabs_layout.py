# app/components/tabs_layout.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Funções para cada Aba ---

def render_tab_rank_geral(df: pd.DataFrame):
    st.header(f"🏆 Rank Geral ({len(df)} ações encontradas)")
    cols_to_display = ['Logo', 'Ticker', 'Empresa', 'Setor', 'Perfil da Ação', 'Preço Atual', 'Preço Teto 5A', 'Alvo', 'DY 5 Anos Média (%)', 'Score Total']
    df_display = df[[col for col in cols_to_display if col in df.columns]]
    
    st.dataframe(df_display,
        column_config={
            "Logo": st.column_config.ImageColumn("Logo"),
            "Preço Atual": st.column_config.NumberColumn("Preço Atual", format="R$ %.2f"),
            "Preço Teto 5A": st.column_config.NumberColumn("Preço Teto 5A", format="R$ %.2f"),
            "Alvo": st.column_config.NumberColumn("Alvo %", format="%.2f%%"),
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
    st.dataframe(df_display,
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
            # ATUALIZAÇÃO VISUAL: Cor 'Hold' alterada para dourado.
            color_map = {
                'Strong Buy': '#2f9e44', 'Buy': '#8ce99a', 'Hold': '#FFD700', 
                'Sell': '#64b5f6', 'Strong Sell': '#1565c0'
            }
            fig = px.bar(rec_df, x='Contagem', y='Recomendação', orientation='h',
                         title='Distribuição das Recomendações', text='Contagem', color='Recomendação',
                         color_discrete_map=color_map)
            fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados de recomendação de analistas para este ativo.")

def render_tab_guia():
    st.header("🧭 Guia da Bússola de Valor")
    st.markdown("Entenda a metodologia por trás do score e dos conceitos de investimento.")
    # (O conteúdo expander do guia original pode ser colado aqui)
    with st.expander("1. Dividend Yield (DY) - Até 45 pontos"): st.markdown("...")
    with st.expander("2. Valuation (P/L e P/VP) - Até 35 pontos"): st.markdown("...")
    with st.expander("3. Rentabilidade e Gestão (ROE e Payout) - Até 35 pontos"): st.markdown("...")
    with st.expander("4. Saúde Financeira (Endividamento) - Até 20 pontos"): st.markdown("...")
    with st.expander("5. Crescimento e Sentimento - Até 25 pontos"): st.markdown("...")


def render_tab_insights(df: pd.DataFrame):
    st.header("✨ Insights Visuais")
    if df.empty:
        st.info("Nenhum dado para exibir com os filtros atuais.")
        return

    st.subheader("Top 15 por Score")
    top = df.nlargest(15, 'Score Total')
    fig_bar = px.bar(top.sort_values('Score Total'), x='Score Total', y='Ticker', orientation='h', color='Setor', hover_data=['Empresa'])
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("DY 12m vs. P/L")
        fig = px.scatter(df, x='P/L', y='DY (Taxa 12m, %)', color='Setor', hover_data=['Ticker'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Distribuição de P/L (Histograma)")
        # CORREÇÃO DO ERRO: Nomes de colunas com caracteres especiais devem usar backticks (` `) no método query.
        query_df = df.query("`P/L` > 0 and `P/L` < 50")
        fig_hist = px.histogram(query_df, x='P/L', nbins=30, title='Distribuição de P/L (0 a 50)')
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.subheader("DY 5 anos vs. P/VP")
        fig = px.scatter(df, x='P/VP', y='DY 5 Anos Média (%)', color='Setor', hover_data=['Ticker'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Score por Setor (Boxplot)")
        fig_box = px.box(df, x='Setor', y='Score Total', title='Score por Setor')
        fig_box.update_layout(xaxis={'categoryorder':'total descending'})
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

    c1, c2 = st.columns(2)
    with c1:
        if not todos_dividendos.empty:
            st.subheader("Série Temporal de Dividendos")
            tickers_opt = sorted(todos_dividendos['ticker_base'].dropna().unique().tolist())
            t_sel = st.selectbox("Selecione um ticker", tickers_opt, index=0)
            if t_sel:
                serie = todos_dividendos[todos_dividendos['ticker_base'] == t_sel]
                serie['Data'] = pd.to_datetime(serie['Data'], errors='coerce')
                fig_div = px.line(serie.sort_values('Data'), x='Data', y='Valor', title=f"Dividendos ao longo do tempo - {t_sel}")
                st.plotly_chart(fig_div, use_container_width=True)
    with c2:
        if not dividendos_ano_resumo.empty:
            st.subheader("Top 20 Maiores Pagadores (12M)")
            top12 = dividendos_ano_resumo.nlargest(20, 'valor_12m')
            fig12 = px.bar(top12.sort_values('valor_12m'), x='valor_12m', y='ticker', orientation='h', title='Top 20: Dividendos Acumulados em 12 Meses')
            st.plotly_chart(fig12, use_container_width=True)
            
    st.divider()
    
    if not dividend_yield_extra.empty:
        st.subheader("Relação DY 12m vs DY 5 anos")
        dyy = dividend_yield_extra.copy()
        dyy['DY12M'] = pd.to_numeric(dyy['DY12M'], errors='coerce')
        dyy['DY5anos'] = pd.to_numeric(dyy['DY5anos'], errors='coerce')
        dyy.dropna(subset=['DY12M','DY5anos'], inplace=True)
        fig_dy = px.scatter(dyy, x='DY12M', y='DY5anos', hover_data=['ticker'], title='Relação DY 12m x DY 5 anos (por ticker)')
        st.plotly_chart(fig_dy, use_container_width=True)


def render_tab_rank_setores(all_data: dict):
    st.header("🏗️ Rank de Setores")
    av_setor = all_data.get('avaliacao_setor', pd.DataFrame())
    if not av_setor.empty:
        av_display = av_setor.rename(columns={'setor': 'Setor', 'pontuacao': 'Pontuação'}).sort_values('Pontuação', ascending=False)
        st.dataframe(av_display, use_container_width=True, hide_index=True,
                     column_config={'Pontuação': st.column_config.NumberColumn('Pontuação', format='%.1f')})
        
        fig = px.bar(av_display.sort_values('Pontuação'), x='Pontuação', y='Setor', orientation='h', title='Ranking de Setores por Pontuação Média')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Arquivo 'avaliacao_setor.csv' não encontrado para gerar o ranking.")


# --- Função Principal de Renderização ---

def render_tabs(df_filtrado: pd.DataFrame, all_data: dict):
    """Cria e gerencia o conteúdo de todas as abas da aplicação."""
    tab_titles = [
        "🏆 Rank Geral", "📋 Rank Detalhado", "🔬 Análise Individual",
        "✨ Insights Visuais", "🔍 Análise de Dividendos", "🏗️ Rank Setores", "🧭 Guia da Bússola"
    ]
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_titles)

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
