# -*- coding: utf-8 -*-
"""
Script otimizado para extrair dados de ativos listados na B3 via API Brapi,
removendo tickers fracionados ('F'), ativos com type 'bdr', o setor 'Miscellaneous',
tickers com setor ausente/nulo, e as colunas 'change', 'market_cap' e 'name',
renomeando a coluna 'stock' para 'ticker',
salvando o resultado em um arquivo CSV no diretório 'data'.
"""

import requests
import pandas as pd
from pathlib import Path
import time

def extrair_dados_brapi():
    """
    Extrai dados de ativos da B3 via API Brapi, remove tickers fracionados ('F'),
    ativos com type 'bdr', o setor 'Miscellaneous', tickers com setor ausente/nulo,
    colunas 'change', 'market_cap' e 'name', renomeia 'stock' para 'ticker',
    e salva em um arquivo CSV.
    
    Retorna:
        pandas.DataFrame: DataFrame com os dados filtrados ou None em caso de erro.
    """
    api_url = "https://brapi.dev/api/quote/list"
    csv_output = "ativos_b3_completo.csv"
    base_dir = Path(__file__).resolve().parent / 'data'

    print("Iniciando extração de dados via Brapi...")
    start_time = time.time()

    try:
        # Requisição à API Brapi
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        ativos = data.get('stocks', [])

        if not ativos:
            print("Nenhum ativo encontrado na resposta da API.")
            return None

        print("Processando dados...")
        # Criar DataFrame diretamente
        df_ativos = pd.DataFrame(ativos)

        # Filtrar tickers fracionados ('F') e ativos com type 'bdr'
        df_ativos = df_ativos[
            ~df_ativos['stock'].str.endswith('F') & 
            (df_ativos['type'] != 'bdr')
        ]

        # Remover setor 'Miscellaneous' e setores ausentes/nulos
        df_ativos = df_ativos[
            (df_ativos['sector'] != 'Miscellaneous') & 
            (df_ativos['sector'].notna()) & 
            (df_ativos['sector'].str.strip() != '') & 
            (df_ativos['sector'] != 'N/A')
        ]

        # Renomear coluna 'stock' para 'ticker'
        df_ativos = df_ativos.rename(columns={'stock': 'ticker'})

        # Remover colunas 'change', 'market_cap' e 'name', se existirem
        colunas_remover = [col for col in ['change', 'market_cap', 'name'] if col in df_ativos.columns]
        if colunas_remover:
            df_ativos = df_ativos.drop(columns=colunas_remover)
            print(f"Colunas removidas: {colunas_remover}")
        else:
            print("Nenhuma das colunas 'change', 'market_cap' ou 'name' encontrada no dataset.")

        # Limpar dados: substituir NaN e strings vazias por 'N/A' nas colunas restantes
        df_ativos = df_ativos.fillna('N/A')
        df_ativos = df_ativos.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df_ativos = df_ativos.replace('', 'N/A')

        # Criar diretório de saída
        base_dir.mkdir(parents=True, exist_ok=True)

        # Salvar em CSV
        csv_path = base_dir / csv_output
        df_ativos.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"Arquivo CSV salvo em: {csv_path}")

        elapsed_time = time.time() - start_time
        print(f"Concluído em {elapsed_time:.2f} segundos. Total de ativos: {len(df_ativos)}")
        return df_ativos

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição à API: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

if __name__ == "__main__":
    df = extrair_dados_brapi()
    if df is not None:
        print("\nAmostra dos primeiros 5 ativos:")
        print(df.head().to_string(index=False))
        print(f"\nColunas disponíveis: {list(df.columns)}")