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
