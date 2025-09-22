# app/data_loader.py
import streamlit as st
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
from scoring import calculate_score_and_details, build_score_details_from_row

@st.cache_data
def read_csv_cached(path, **kwargs):
    """Lê um CSV com cache para acelerar recarregamentos."""
    return pd.read_csv(path, **kwargs)

def load_main_data(path: str) -> pd.DataFrame:
    """Carrega o dataset consolidado, tratando tipos numéricos e datas."""
    if not os.path.exists(path):
        st.error(f"Arquivo de dados principal não encontrado em '{path}'. Verifique o caminho.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, index_col=0)
        numeric_cols = [
            'Preço Atual', 'P/L', 'P/VP', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)',
            'Payout Ratio (%)', 'Crescimento Preço (%)', 'ROE (%)', 'Dívida Total',
            'Market Cap', 'Dívida/EBITDA', 'Sentimento Gauge', 'Strong Buy', 'Buy',
            'Hold', 'Sell', 'Strong Sell'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        for col in ["Data Últ. Div.", "Data Ex-Div."]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        # Renomear colunas de recomendação para maiúsculo
        rename_dict = {
            'strong_buy': 'Strong Buy',
            'buy': 'Buy',
            'hold': 'Hold',
            'sell': 'Sell',
            'strong_sell': 'Strong Sell'
        }
        df.rename(columns={k: v for k, v in rename_dict.items() if k in df.columns}, inplace=True)
        df['Ticker'] = df.index.str.replace('.SA', '')
        return df
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar ou processar o arquivo CSV principal: {e}")
        return pd.DataFrame()

def load_and_merge_data(base_path: Path) -> tuple[pd.DataFrame, dict]:
    """
    Orquestra o carregamento de todos os CSVs, realiza os merges,
    calcula o score e retorna o DataFrame final e um dicionário com dados de apoio.
    """
    load_dotenv()
    data_path_env = os.getenv('B3_REPORT_PATH')

    # --- Carrega DataFrame Principal ---
    if data_path_env:
        df = load_main_data(data_path_env)
    else:
        # Fallback para carregar e montar a partir de CSVs individuais
        try:
            indic = read_csv_cached(base_path / 'indicadores.csv')
            dy = read_csv_cached(base_path / 'dividend_yield.csv')
            indic['ticker_base'] = indic['ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
            dy['ticker_base'] = dy['ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
            df = indic.merge(dy[['ticker_base','DY12M','DY5anos']], on='ticker_base', how='left')
            df.rename(columns={
                'empresa':'Empresa','setor_brapi':'Setor (brapi)','logo':'Logo','perfil_acao':'Perfil da Ação',
                'market_cap':'Market Cap','preco_atual':'Preço Atual','p_l':'P/L','p_vp':'P/VP',
                'payout_ratio':'Payout Ratio (%)','crescimento_preco_5a':'Crescimento Preço (%)','roe':'ROE (%)',
                'divida_total':'Dívida Total','divida_ebitda':'Dívida/EBITDA','sentimento_gauge':'Sentimento Gauge',
                'DY12M':'DY (Taxa 12m, %)','DY5anos':'DY 5 Anos Média (%)',
                'strong_buy': 'Strong Buy', 'buy': 'Buy', 'hold': 'Hold', 'sell': 'Sell', 'strong_sell': 'Strong Sell'
            }, inplace=True)

            # Garante que colunas de DY e recomendação sejam numéricas e preenche NaNs com 0
            numeric_cols = [
                'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            df['Ticker'] = df['ticker_base']
        except Exception as e:
            st.error(f"Falha ao montar dados base de '{base_path}': {e}")
            return pd.DataFrame(), {}

    if df.empty:
        return pd.DataFrame(), {}

    # --- Cálculo de Dívida/Market Cap ---
    if 'Dívida Total' in df.columns and 'Market Cap' in df.columns:
        # Garante que as colunas são numéricas antes da divisão
        df['Dívida Total'] = pd.to_numeric(df['Dívida Total'], errors='coerce')
        df['Market Cap'] = pd.to_numeric(df['Market Cap'], errors='coerce')
        # Evita divisão por zero
        df['Dívida/Market Cap'] = df.apply(
            lambda row: row['Dívida Total'] / row['Market Cap'] if row['Market Cap'] != 0 else 0,
            axis=1
        )

    # --- Merge com Scores Externos ---
    try:
        scores_df = read_csv_cached(base_path / 'scores.csv')
        df = df.merge(scores_df, left_on='Ticker', right_on='ticker_base', how='left')
        df['Score Total'] = pd.to_numeric(df['score_total'], errors='coerce').fillna(0)
        df['Score Details'] = df.apply(build_score_details_from_row, axis=1)
    except FileNotFoundError:
        st.info("Arquivo 'scores.csv' não encontrado. Calculando score em tempo real.")
        score_results = df.apply(calculate_score_and_details, axis=1)
        df['Score Total'] = score_results.apply(lambda x: x[0])
        df['Score Details'] = score_results.apply(lambda x: x[1])
    except Exception as e:
        st.warning(f"Não foi possível carregar 'scores.csv': {e}. Calculando score em tempo real.")
        score_results = df.apply(calculate_score_and_details, axis=1)
        df['Score Total'] = score_results.apply(lambda x: x[0])
        df['Score Details'] = score_results.apply(lambda x: x[1])


    # --- Merge com Dados de Apoio ---
    try:
        pt = read_csv_cached(base_path / 'preco_teto.csv')
        pt['ticker_base'] = pt['ticker'].astype(str).str.upper().str.replace('.SA', '', regex=False).str.strip()
        df = df.merge(pt[['ticker_base', 'preco_teto_5anos', 'diferenca_percentual']], left_on='Ticker', right_on='ticker_base', how='left')
        df.rename(columns={'preco_teto_5anos': 'Preço Teto 5A', 'diferenca_percentual': 'Alvo'}, inplace=True)
    except Exception: pass

    try:
        pa = read_csv_cached(base_path / 'precos_acoes.csv')
        pa['ticker_base'] = pa['ticker'].astype(str).str.upper().str.replace('.SA', '', regex=False).str.strip()
        df = df.merge(pa[['ticker_base', 'fechamento_atual']], left_on='Ticker', right_on='ticker_base', how='left')
        if 'fechamento_atual' in df.columns:
            df['Preço Atual'] = df['fechamento_atual'].combine_first(df['Preço Atual'])
            df.drop(columns=['fechamento_atual'], inplace=True)
    except Exception: pass
    
    # --- Merge com Avaliação de Setor ---
    try:
        df_setor = read_csv_cached(base_path / 'avaliacao_setor.csv')
        # Ambas as tabelas usam 'subsetor_b3' para a junção.
        if 'subsetor_b3' in df.columns and 'subsetor_b3' in df_setor.columns:
            # Seleciona apenas as colunas necessárias para o merge para evitar duplicatas.
            df_setor_scores = df_setor[['subsetor_b3', 'pontuacao_subsetor']].drop_duplicates(subset=['subsetor_b3'])
            df = df.merge(df_setor_scores, on='subsetor_b3', how='left')
        else:
            st.warning("Não foi possível fazer o merge da pontuação de subsetor. Coluna 'subsetor_b3' não encontrada.")
    except FileNotFoundError:
        st.warning("Arquivo 'avaliacao_setor.csv' não encontrado. A pontuação por subsetor não será carregada.")
    except Exception as e:
        st.warning(f"Erro ao processar 'avaliacao_setor.csv': {e}")

    # --- Merge com Ciclo de Mercado ---
    try:
        df_ciclo = read_csv_cached(base_path / 'ciclo_mercado.csv')
        if not df_ciclo.empty:
            # Renomear a coluna de status e selecionar as colunas de interesse
            df_ciclo_to_merge = df_ciclo[['ticker', 'Status 🟢🔴']].rename(columns={'Status 🟢🔴': 'Status Ciclo'})
            # Normalizar o ticker para o merge
            df_ciclo_to_merge['ticker_base'] = df_ciclo_to_merge['ticker'].str.strip().str.upper()
            df_ciclo_to_merge.set_index('ticker_base', inplace=True)
            # Fazer o merge com o dataframe principal
            df = df.merge(df_ciclo_to_merge[['Status Ciclo']], left_on='Ticker', right_index=True, how='left')
            # Preencher valores nulos na nova coluna, se houver
            df['Status Ciclo'].fillna('N/A', inplace=True)
    except Exception as e:
        st.warning(f"Não foi possível fazer o merge com os dados de ciclo de mercado: {e}")

    # Limpa colunas auxiliares de merge
    df.drop(columns=[col for col in df.columns if 'ticker_base' in str(col)], inplace=True, errors='ignore')

    

    # --- Carrega datasets para gráficos ---
    all_data = {}
    optional_files = [
        'dividendos_ano', 'dividendos_ano_resumo', 'todos_dividendos',
        'dividend_yield', 'avaliacao_setor', 'precos_acoes', 'ciclo_mercado', 'rj'
    ]
    for filename in optional_files:
        try:
            data = read_csv_cached(base_path / f'{filename}.csv')
            if 'ticker' in data.columns:
                data['ticker_base'] = data['ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
            if 'Ticker' in data.columns:
                 data['ticker_base'] = data['Ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
            all_data[filename] = data
        except Exception:
            all_data[filename] = pd.DataFrame()

    return df, all_data

def load_indices_scores(data_path: Path) -> dict:
    """
    Carrega os valores de fechamento mais recentes dos índices e a variação percentual
    em relação ao ano anterior.

    Args:
        data_path (Path): Caminho para a pasta de dados.

    Returns:
        dict: Dicionário com os dados de cada índice.
              Ex: {'iShares Ibovespa': {'score': 142.79, 'delta': 9.51}}
    """
    file_path = data_path / "indices.csv"
    indices_data = {}
    try:
        df = pd.read_csv(file_path)
        
        for index_name in df['index'].unique():
            index_df = df[df['index'] == index_name].sort_values('year', ascending=False)
            
            if len(index_df) < 2:
                latest_close = index_df['close'].iloc[0] if not index_df.empty else float('nan')
                delta = float('nan')
            else:
                latest_close = index_df['close'].iloc[0]
                previous_close = index_df['close'].iloc[1]
                
                if previous_close == 0:
                    delta = float('inf') if latest_close > 0 else 0.0
                else:
                    delta = ((latest_close - previous_close) / previous_close) * 100
            
            indices_data[index_name] = {'score': latest_close, 'delta': delta}
            
        return indices_data

    except (FileNotFoundError, KeyError, IndexError):
        return {}
