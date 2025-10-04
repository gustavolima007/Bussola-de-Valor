# -*- coding: utf-8 -*-
"""
Modulo comum para o pipeline de engenharia de dados.

Este arquivo centraliza constantes e funções utilitárias que são
compartilhadas entre os diversos scripts do pipeline.
"""

from pathlib import Path
import pandas as pd

# Define o diretório base 'data' para leitura dos arquivos
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
LAND_DW_DIR = Path(__file__).resolve().parent.parent / 'duckdb' / 'land_dw'

def get_tickers() -> list:
    """
    Lê um arquivo Parquet e extrai uma lista de tickers únicos da coluna 'ticker'.

    Returns:
        list: Uma lista de tickers únicos. Retorna uma lista vazia em caso de erro.
    """
    parquet_path = LAND_DW_DIR / "acoes_e_fundos.parquet"

    try:
        df = pd.read_parquet(parquet_path)
        if 'ticker' not in df.columns:
            print(f"❌ Erro: A coluna 'ticker' não foi encontrada em {parquet_path}.")
            return []
        
        tickers = (
            df['ticker']
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .unique()
            .tolist()
        )
        print(f"ℹ️ Encontrados {len(tickers)} tickers únicos em {parquet_path.name}.")
        return tickers
        
    except FileNotFoundError:
        print(f"❌ Erro: O arquivo {parquet_path} não foi encontrado.")
        return []
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo de tickers: {e}")
        return []

def save_to_parquet(df: pd.DataFrame, file_name: str):
    """
    Salva um DataFrame em formato Parquet no diretório de staging.

    Args:
        df (pd.DataFrame): O DataFrame a ser salvo.
        file_name (str): O nome do arquivo (sem a extensão).
    """
    # Garante que o diretório de destino exista
    LAND_DW_DIR.mkdir(parents=True, exist_ok=True)
    
    output_path = LAND_DW_DIR / f"{file_name}.parquet"
    
    try:
        df.to_parquet(output_path, index=False)
        print(f"✅ Arquivo salvo: {output_path.name}")
    except Exception as e:
        print(f"❌ Erro ao salvar {output_path.name}: {e}")

def tratar_dados_para_json(df):
    """
    Prepara um DataFrame para ser salvo em JSON, tratando NaNs e Timestamps.

    - Substitui np.nan por None em colunas de ponto flutuante (float).
    - Converte colunas de Timestamp para strings no formato ISO 8601.
    - Remove espaços em branco extras de colunas de string.

    Args:
        df (pd.DataFrame): O DataFrame a ser tratado.

    Returns:
        pd.DataFrame: O DataFrame com os tipos de dados ajustados.
    """
    for col in df.columns:
        # Trata colunas de data e hora
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S+00') if pd.notnull(x) else None)
            
        # Trata colunas de string/objeto
        elif pd.api.types.is_object_dtype(df[col]):
            df[col] = df[col].str.strip()

    # Substitui todos os NaNs restantes por None
    df = df.where(pd.notnull(df), None)

    return df