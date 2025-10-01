# -*- coding: utf-8 -*-
"""
Modulo comum para o pipeline de engenharia de dados.

Este arquivo centraliza constantes e funções utilitárias que são
compartilhadas entre os diversos scripts do pipeline.
"""

from pathlib import Path
import pandas as pd

# Define o diretório base 'data' para leitura e escrita dos arquivos
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

def get_tickers(csv_path=None) -> list:
    """
    Lê um arquivo CSV e extrai uma lista de tickers únicos da coluna 'ticker'.

    Args:
        csv_path (str, optional): Caminho para o arquivo CSV. 
                                  Se None, usa o padrão 'acoes_e_fundos.csv'.

    Returns:
        list: Uma lista de tickers únicos. Retorna uma lista vazia em caso de erro.
    """
    if csv_path is None:
        csv_path = DATA_DIR / "acoes_e_fundos.csv"

    try:
        df = pd.read_csv(csv_path)
        if 'ticker' not in df.columns:
            print(f"Erro: A coluna 'ticker' não foi encontrada em {csv_path}.")
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
        print(f"Encontrados {len(tickers)} tickers únicos em {csv_path.name}.")
        return tickers
        
    except FileNotFoundError:
        print(f"❌ Erro: O arquivo {csv_path} não foi encontrado.")
        return []
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo de tickers: {e}")
        return []

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
