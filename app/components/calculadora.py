# app/components/calculadora.py
import streamlit as st
import pandas as pd

def render_tab_calculadora(all_data: dict, ticker_foco: str = None):
    st.header("💰 Calculadora de Dividendos 🧮")

    dividendos_ano = all_data.get('dividendos_ano', pd.DataFrame())

    if dividendos_ano.empty:
        st.warning("Não foram encontrados dados de dividendos na tabela 'dividendos_ano'.")
        return

    st.subheader("Calcule seus dividendos recebidos")

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        # Input para a quantidade de ações
        quantidade_acoes = st.number_input("Quantidade de Ações", min_value=1, value=100, step=100)

        # Seleção do ticker
        tickers_disponiveis = sorted(dividendos_ano['ticker'].unique())
        
        # Define o ticker selecionado com base no filtro "Ticker em Foco"
        if ticker_foco and ticker_foco in tickers_disponiveis:
            ticker_selecionado = st.selectbox("Selecione o Ticker", tickers_disponiveis, index=tickers_disponiveis.index(ticker_foco))
        else:
            ticker_selecionado = st.selectbox("Selecione o Ticker", tickers_disponiveis)

        # Filtro de anos
        anos_disponiveis = sorted(dividendos_ano['ano'].unique(), reverse=True)
        anos_selecionados = st.multiselect("Selecione os Anos", anos_disponiveis, default=anos_disponiveis)

    if ticker_selecionado and quantidade_acoes > 0 and anos_selecionados:
        precos_acoes = all_data.get('precos_acoes', pd.DataFrame())

        # Filtra os dados para o ticker e anos selecionados
        df_ticker = dividendos_ano[
            (dividendos_ano['ticker'] == ticker_selecionado) &
            (dividendos_ano['ano'].isin(anos_selecionados))
        ].copy()
        
        # Calcula o valor a receber
        df_ticker['valor_a_receber'] = df_ticker['dividendo'] * quantidade_acoes
        
        # Seleciona e renomeia as colunas para exibição
        df_resultado = df_ticker[['ticker', 'ano', 'valor_a_receber']].rename(
            columns={
                'ticker': 'Ticker',
                'ano': 'Ano',
                'valor_a_receber': 'Valor a Receber (R$)'
            }
        )

        # Calcula o valor total a receber
        valor_total = df_ticker['valor_a_receber'].sum()

        # Calcula o valor do investimento
        preco_atual = 0
        if not precos_acoes.empty:
            preco_info = precos_acoes[precos_acoes['ticker'] == ticker_selecionado]
            if not preco_info.empty:
                preco_atual = preco_info['fechamento_atual'].iloc[0]
        
        valor_investimento = quantidade_acoes * preco_atual

        with col1:
            st.subheader(f"Dividendos projetados para {quantidade_acoes} ações de {ticker_selecionado}:")
            st.metric("Valor Total a Receber (período selecionado)", f"R$ {valor_total:,.2f}")
            if preco_atual > 0:
                st.metric("Preço da Ação", f"R$ {preco_atual:,.2f}")
            if valor_investimento > 0:
                st.metric("Valor deste investimento", f"R$ {valor_investimento:,.2f}")
        
        with col2:
            # Exibe o dataframe com o resultado
            st.dataframe(
                df_resultado,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Valor a Receber (R$)": st.column_config.NumberColumn(
                        "Valor a Receber (R$)",
                        format="R$ %.2f"
                    )
                }
            )
    elif not anos_selecionados:
        st.warning("Selecione pelo menos um ano para exibir os resultados.")
