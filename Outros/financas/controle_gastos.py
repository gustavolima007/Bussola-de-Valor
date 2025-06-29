import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
from datetime import datetime

# Função para tratar os dados
def clean_and_prepare_data(file_path: str) -> pd.DataFrame:
    """
    Carrega e trata o arquivo Excel para análise de gastos, removendo transação específica.
    """
    try:
        df = pd.read_excel(file_path)
        with duckdb.connect(database=':memory:') as con:
            con.register('extrato_df', df)
            df['Data e hora'] = pd.to_datetime(df['Data e hora'], format='%d/%m/%Y %H:%M')
            # Converter meses para português
            meses_portugues = {
                'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
                'April': 'abril', 'May': 'maio', 'June': 'junho',
                'July': 'julho', 'August': 'agosto', 'September': 'setembro',
                'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
            }
            df['Mes'] = df['Data e hora'].dt.strftime('%B').map(meses_portugues)
            # Remover transação específica
            df = df[~((df['Data e hora'] == pd.to_datetime('2024-01-05 20:11:00')) & 
                      (df['Transação'] == 'Pix enviado') & 
                      (df['Descrição'] == 'Natalino De Oliveira Lima') & 
                      (df['Valor'] == -10000))]
            # Ajuste para tratar Investimentos como aportes (valores positivos)
            df['Tipo'] = df.apply(
                lambda x: 'Aporte' if x['Categoria'] == 'Investimentos' and x['Valor'] < 0 
                else ('Receita' if x['Valor'] > 0 or 'recebido' in x['Transação'].lower() else 'Despesa'), axis=1
            )
            df.loc[df['Categoria'] == 'Investimentos', 'Valor'] = df.loc[df['Categoria'] == 'Investimentos', 'Valor'].abs()
            return df
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None

# Função para calcular KPIs
def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calcula KPIs para análise de gastos, separando aportes.
    """
    kpis = {}
    df_sem_invest = df[df['Categoria'] != 'Investimentos']
    receitas = df_sem_invest[df_sem_invest['Tipo'] == 'Receita']['Valor'].sum()
    despesas = abs(df_sem_invest[df_sem_invest['Tipo'] == 'Despesa']['Valor'].sum())
    kpis['Soma de Valor'] = receitas - despesas
    kpis['Media de Valor'] = df_sem_invest['Valor'].mean() if not df_sem_invest.empty else 0
    return kpis

# Função principal do Streamlit
def main():
    st.title("Controle de Gastos 2024")
    st.write("Maximize investimentos em dividendos e mantenha reserva em renda fixa. | Atualizado em 12:10 PM -03, 22/06/2025")

    # Caminho do arquivo Excel
    excel_file_path = r"E:\Github\finance-manager\financas\datasets\Extrato_2024-01-01_a_2024-12-08_LIMPO.xlsx"
    
    # Carregar dados
    df = clean_and_prepare_data(excel_file_path)
    
    if df is not None:
        # Filtros interativos
        meses = ['Todos'] + sorted(df['Mes'].unique().tolist())
        categorias = ['Todos'] + sorted([cat for cat in df['Categoria'].unique() if cat != 'Investimentos'])
        transacoes = ['Todos'] + sorted(df['Transação'].unique().tolist())

        mes_selecionado = st.selectbox("Mês", meses)
        categoria_selecionada = st.selectbox("Categoria", categorias)
        transacao_selecionada = st.selectbox("Transação", transacoes)

        # Filtrar dados
        df_filtrado = df.copy()
        if mes_selecionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Mes'] == mes_selecionado]
        if categoria_selecionada != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_selecionada]
        if transacao_selecionada != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Transação'] == transacao_selecionada]

        # Calcular KPIs
        kpis = calculate_kpis(df_filtrado)

        # Exibir KPIs
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Soma de Valor", f"R$ {kpis['Soma de Valor']:.2f}")
        with col2:
            st.metric("Média de Valor", f"R$ {kpis['Media de Valor']:.2f}")

        # Gráfico: Distribuição de Gastos por Categoria (sem Investimentos)
        st.subheader("Distribuição de Gastos por Categoria")
        df_sem_invest = df_filtrado[df_filtrado['Categoria'] != 'Investimentos']
        if not df_sem_invest.empty:
            soma_categoria = df_sem_invest.groupby('Categoria')['Valor'].sum().reset_index()
            soma_categoria['Valor_Abs'] = soma_categoria['Valor'].abs()  # Valores absolutos para o gráfico
            fig_pie = px.pie(soma_categoria, values='Valor_Abs', names='Categoria',
                             title='Distribuição de Gastos por Categoria',
                             color_discrete_sequence=px.colors.qualitative.Safe,  # Paleta harmoniosa
                             hole=0.3)  # Ajuste no donut para melhor visual
            fig_pie.update_traces(textposition='inside', textinfo='percent+label',
                                  textfont_size=12, marker=dict(line=dict(color='#FFFFFF', width=1.5)))
            fig_pie.update_layout(
                showlegend=True,
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.1),
                margin=dict(l=40, r=40, t=40, b=40),
                uniformtext_minsize=10, uniformtext_mode='hide'  # Evita sobreposição
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.write("Nenhum dado disponível para exibir o gráfico.")

        # Gráfico: Evolução de Gastos por Mês (sem Investimentos)
        st.subheader("Evolução de Gastos por Mês")
        if not df_sem_invest.empty:
            soma_mes = df_sem_invest.groupby('Mes')['Valor'].sum().reset_index()
            fig_bar = px.bar(soma_mes, x='Mes', y='Valor',
                             title='Evolução de Gastos por Mês',
                             color='Valor', color_continuous_scale=px.colors.sequential.Viridis)
            fig_bar.update_layout(
                xaxis_title="Mês",
                yaxis_title="Valor (R$)",
                showlegend=False,
                margin=dict(l=50, r=50, t=50, b=50),
                plot_bgcolor='rgba(245, 245, 245, 0.9)',  # Fundo claro
                paper_bgcolor='rgba(255, 255, 255, 1)'
            )
            fig_bar.update_traces(marker_line_color='rgb(50, 50, 50)',
                                marker_line_width=1, opacity=0.9)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("Nenhum dado disponível para exibir o gráfico.")

        # Tabela de Transações (sem Investimentos)
        st.subheader("Detalhe das Transações")
        st.dataframe(df_sem_invest[['Data e hora', 'Mes', 'Categoria', 'Transação', 'Descrição', 'Valor', 'Tipo']])

        # Recomendações
        st.write("**Dicas:**")
        st.write("- Use o saldo disponível para alocar em renda fixa (ex.: Tesouro Selic) para reserva.")
        st.write("- Planeje aportes em ações de dividendos (ex.: TAEE11, BBAS3).")

if __name__ == "__main__":
    main()