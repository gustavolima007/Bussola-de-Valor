# app/data_loader.py
import streamlit as st
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
from scoring import calculate_score_and_details, build_score_details_from_row, calculate_scores_in_parallel
from datetime import datetime
import duckdb

# --- Configuração do Banco de Dados ---
DB_PATH = "duckdb/banco_dw/dw.duckdb"

@st.cache_resource
def get_db_connection():
    """Cria e gerencia uma conexão com o banco de dados DuckDB."""
    try:
        return duckdb.connect(database=DB_PATH, read_only=True)
    except Exception as e:
        st.error(f"Falha ao conectar ao banco de dados DuckDB: {e}")
        return None

@st.cache_data
def read_table_cached(table_name: str, **kwargs) -> pd.DataFrame:
    """Lê uma tabela do DuckDB com cache para acelerar recarregamentos."""
    conn = get_db_connection()
    if conn:
        try:
            return conn.table(table_name).to_df()
        except Exception as e:
            st.error(f"Erro ao ler a tabela '{table_name}': {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=60)
def get_last_update_time() -> str | None:
    """
    Lê os timestamps de atualização da pipeline e do loader, e retorna o mais recente.
    """
    pipeline_time_path = Path('duckdb/land_dw/pipeline_datetime.parquet')
    loader_time_path = Path('duckdb/land_dw/loader_datetime.parquet')
    
    latest_time = None

    try:
        if pipeline_time_path.exists():
            df_pipeline = pd.read_parquet(pipeline_time_path)
            if not df_pipeline.empty and 'pipeline_datetime' in df_pipeline.columns:
                pipeline_time = pd.to_datetime(df_pipeline['pipeline_datetime'].iloc[0])
                latest_time = pipeline_time
    except Exception as e:
        st.warning(f"Não foi possível ler o timestamp da pipeline: {e}")

    try:
        if loader_time_path.exists():
            df_loader = pd.read_parquet(loader_time_path)
            if not df_loader.empty and 'loader_datetime' in df_loader.columns:
                loader_time = pd.to_datetime(df_loader['loader_datetime'].iloc[0])
                if latest_time is None or loader_time > latest_time:
                    latest_time = loader_time
    except Exception as e:
        st.warning(f"Não foi possível ler o timestamp do loader: {e}")

    if latest_time:
        return latest_time.strftime("%d/%m/%Y às %H:%M:%S")
    
    # Fallback para o método antigo se os arquivos novos não existirem
    db_file = Path(DB_PATH)
    if db_file.exists():
        try:
            last_mod_timestamp = db_file.stat().st_mtime
            last_mod_datetime = datetime.fromtimestamp(last_mod_timestamp)
            return last_mod_datetime.strftime("%d/%m/%Y às %H:%M:%S")
        except Exception:
            return None
            
    return None

def load_main_data() -> pd.DataFrame:
    """Carrega o dataset consolidado do DuckDB, tratando tipos numéricos e datas."""
    df = read_table_cached("indicadores") # Assumindo que 'indicadores' é a tabela principal
    if df.empty:
        st.error("A tabela 'indicadores' não foi encontrada ou está vazia.")
        return pd.DataFrame()
    try:
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
        
        rename_dict = {
            'strong_buy': 'Strong Buy',
            'buy': 'Buy',
            'hold': 'Hold',
            'sell': 'Sell',
            'strong_sell': 'Strong Sell'
        }
        df.rename(columns={k: v for k, v in rename_dict.items() if k in df.columns}, inplace=True)
        df['Ticker'] = df['ticker'].str.replace('.SA', '')
        return df
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os dados da tabela 'indicadores': {e}")
        return pd.DataFrame()

def load_and_merge_data() -> tuple[pd.DataFrame, dict]:
    """
    Orquestra o carregamento de todas as tabelas do DuckDB, realiza os merges,
    calcula o score e retorna o DataFrame final e um dicionário com dados de apoio.
    """
    # --- Carrega DataFrame Principal ---
    indic = read_table_cached('indicadores')
    if indic.empty:
        st.error("Tabela 'indicadores' não encontrada ou vazia. A aplicação não pode continuar.")
        return pd.DataFrame(), {}

    dy = read_table_cached('dividend_yield')
    indic['ticker_base'] = indic['ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
    dy['ticker_base'] = dy['ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
    df = indic.merge(dy[['ticker_base','DY12m','DY5anos']], on='ticker_base', how='left')
    df.rename(columns={
        'empresa':'Empresa','logo':'Logo','perfil_acao':'Perfil da Ação',
        'market_cap':'Market Cap','preco_atual':'Preço Atual','p_l':'P/L','p_vp':'P/VP',
        'payout_ratio':'Payout Ratio (%)','crescimento_preco_5a':'Crescimento Preço (%)','roe':'ROE (%)',
        'divida_total':'Dívida Total','divida_ebitda':'Dívida/EBITDA','sentimento_gauge':'Sentimento Gauge',
        'DY12m':'DY (Taxa 12m, %)','DY5anos':'DY 5 Anos Média (%)',
        'strong_buy': 'Strong Buy', 'buy': 'Buy', 'hold': 'Hold', 'sell': 'Sell', 'strong_sell': 'Strong Sell',
        'beta':'Beta','current_ratio':'Current Ratio','liquidez_media_diaria':'Volume Médio Diário','fcf_yield':'FCF Yield'
    }, inplace=True)
    
    # Cria coluna 'Setor (brapi)' a partir de 'subsetor_b3' mantendo ambas
    if 'subsetor_b3' in df.columns:
        df['Setor (brapi)'] = df['subsetor_b3']

    # Converte todas as colunas numéricas necessárias
    numeric_cols = [
        'Preço Atual', 'P/L', 'P/VP', 'DY (Taxa 12m, %)', 'DY 5 Anos Média (%)', 
        'Payout Ratio (%)', 'Crescimento Preço (%)', 'ROE (%)', 'Dívida Total', 
        'Market Cap', 'Dívida/EBITDA', 'Sentimento Gauge', 'Strong Buy', 'Buy', 
        'Hold', 'Sell', 'Strong Sell', 'Beta', 'Current Ratio', 'Volume Médio Diário', 
        'FCF Yield', 'margem_seguranca_percent'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['Ticker'] = df['ticker_base']

    if df.empty:
        return pd.DataFrame(), {}

    # --- Cálculo de Dívida/Market Cap ---
    if 'Dívida Total' in df.columns and 'Market Cap' in df.columns:
        df['Dívida Total'] = pd.to_numeric(df['Dívida Total'], errors='coerce')
        df['Market Cap'] = pd.to_numeric(df['Market Cap'], errors='coerce')
        df['Dívida/Market Cap'] = df.apply(
            lambda row: row['Dívida Total'] / row['Market Cap'] if row['Market Cap'] != 0 else 0,
            axis=1
        )

    # --- Merge com Scores Externos ---
    scores_df = read_table_cached('scores')
    if not scores_df.empty:
        # Normaliza o ticker da tabela scores
        scores_df['ticker_base'] = scores_df['ticker'].astype(str).str.upper().str.replace('.SA', '', regex=False).str.strip()
        df = df.merge(scores_df, left_on='Ticker', right_on='ticker_base', how='left', suffixes=('', '_scores'))
        df['Score Total'] = pd.to_numeric(df['score_total'], errors='coerce').fillna(0)
        df['Score Details'] = df.apply(build_score_details_from_row, axis=1)
    else:
        st.info("Tabela 'scores' não encontrada. Calculando score em tempo real.")
        score_results = calculate_scores_in_parallel(df)
        df['Score Total'] = [result[0] for result in score_results]
        df['Score Details'] = [result[1] for result in score_results]


    # --- Merge com Dados de Apoio ---
    pt = read_table_cached('preco_teto')
    if not pt.empty:
        pt['ticker_base'] = pt['ticker'].astype(str).str.upper().str.replace('.SA', '', regex=False).str.strip()
        df = df.merge(pt[['ticker_base', 'preco_teto_5anos', 'diferenca_percentual']], left_on='Ticker', right_on='ticker_base', how='left', suffixes=('', '_pt'))
        df.rename(columns={'preco_teto_5anos': 'Preço Teto 5A', 'diferenca_percentual': 'Alvo'}, inplace=True)

    # --- Merge com Preços de Ações (1M e 6M) ---
    pa = read_table_cached('precos_acoes')
    if not pa.empty:
        if 'ticker' in pa.columns and 'Ticker' in df.columns:
            pa['ticker_base'] = pa['ticker'].astype(str).str.upper().str.replace('.SA', '', regex=False).str.strip()

            cols_to_merge = ['ticker_base', 'fechamento_atual', 'fechamento_1m_atras', 'fechamento_6m_atras']
            pa_cols = [col for col in cols_to_merge if col in pa.columns]

            df = df.merge(pa[pa_cols], left_on='Ticker', right_on='ticker_base', how='left', suffixes=('', '_pa'))

            if 'fechamento_atual' in df.columns:
                df['Preço Atual'] = df['fechamento_atual'].combine_first(df['Preço Atual'])
                df.drop(columns=['fechamento_atual'], inplace=True)

            df.rename(columns={
                'fechamento_1m_atras': 'Preço 1M',
                'fechamento_6m_atras': 'Preço 6M'
            }, inplace=True)

            # --- Cálculo da Valorização (1M e 6M) ---
            for period in ['1M', '6M']:
                price_col = f'Preço {period}'
                val_col = f'Val {period}'
                if price_col in df.columns and 'Preço Atual' in df.columns:
                    df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
                    df['Preço Atual'] = pd.to_numeric(df['Preço Atual'], errors='coerce')
                    df[val_col] = df.apply(
                        lambda row: ((row['Preço Atual'] - row[price_col]) / row[price_col]) * 100 if row[price_col] and row[price_col] != 0 else 0,
                        axis=1
                    )
    else:
        st.warning("Tabela 'precos_acoes' não encontrada. As colunas 'Preço 1M' e 'Preço 6M' não serão exibidas.")
    
    # --- Merge com Avaliação de Setor ---
    df_setor = read_table_cached('avaliacao_setor')
    if not df_setor.empty:
        if 'subsetor_b3' in df.columns and 'subsetor_b3' in df_setor.columns:
            df_setor_scores = df_setor[['subsetor_b3', 'pontuacao_final']].drop_duplicates(subset=['subsetor_b3'])
            df = df.merge(df_setor_scores, on='subsetor_b3', how='left')
        else:
            st.warning("Não foi possível fazer o merge da pontuação de subsetor. Coluna 'subsetor_b3' não encontrada.")
    else:
        st.warning("Tabela 'avaliacao_setor' não encontrada. A pontuação por subsetor não será carregada.")
        df['pontuacao_final'] = 0

    # --- Processa Coluna Ciclo de Mercado ---
    if 'status_ciclo' in df.columns:
        df.rename(columns={'status_ciclo': 'Status Ciclo'}, inplace=True)
        df['Status Ciclo'].fillna('N/A', inplace=True)
    else:
        df['Status Ciclo'] = 'N/A'

    # Limpa colunas auxiliares de merge
    df.drop(columns=[col for col in df.columns if 'ticker_base' in str(col)], inplace=True, errors='ignore')

    # --- Carrega datasets para gráficos ---
    all_data = {}
    optional_tables = [
        'dividendos_ano', 'dividendos_ano_resumo', 'todos_dividendos',
        'dividend_yield', 'avaliacao_setor', 'precos_acoes', 'ciclo_mercado', 'rj'
    ]
    for table_name in optional_tables:
        data = read_table_cached(table_name)
        if not data.empty:
            if 'ticker' in data.columns:
                data['ticker_base'] = data['ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
            if 'Ticker' in data.columns:
                 data['ticker_base'] = data['Ticker'].astype(str).str.upper().str.replace('.SA','', regex=False).str.strip()
        all_data[table_name] = data

    return df, all_data

def load_indices_scores() -> dict:
    """
    Carrega os valores de fechamento mais recentes dos índices e a variação percentual
    em relação ao ano anterior a partir do DuckDB.
    """
    indices_data = {}
    df = read_table_cached("indices")
    if df.empty:
        return {}
        
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
