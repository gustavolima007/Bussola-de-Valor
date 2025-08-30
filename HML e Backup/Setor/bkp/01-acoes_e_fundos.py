# -*- coding: utf-8 -*-
"""
📄 Script para extrair e processar dados de ações e fundos da B3.

Este script se conecta à API Brapi para obter uma lista de todos os ativos
disponíveis, realiza uma série de filtros e limpezas, e salva o resultado
em um arquivo CSV.

Otimizações e Filtros:
- Remove tickers fracionados (terminados em 'F').
- Exclui BDRs (Brazilian Depositary Receipts).
- Elimina o setor 'Miscellaneous' e ativos com setor não especificado.
- Remove colunas desnecessárias ('change', 'market_cap', 'name', 'close').
- Renomeia as colunas para um padrão em português e minúsculas.
- Salva o DataFrame resultante em 'data/acoes_e_fundos.csv'.
"""

import requests
import pandas as pd
from pathlib import Path
import time

def extrair_dados_brapi():
    """
    Extrai, filtra e processa dados de ativos da B3 usando a API Brapi.

    Returns:
        pandas.DataFrame: Um DataFrame contendo os dados dos ativos filtrados
                          e processados. Retorna None se ocorrer um erro.
    """
    api_url = "https://brapi.dev/api/quote/list"
    csv_output = "acoes_e_fundos.csv"
    # Define o diretório base para salvar os dados (pasta 'data' no nível raiz do projeto)
    base_dir = Path(__file__).resolve().parent.parent / 'data'

    print("Iniciando extração de dados via Brapi...")
    start_time = time.time()

    try:
        # Realiza a requisição GET para a API com um timeout de 15 segundos
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()  # Lança uma exceção para respostas com erro (status code >= 400)
        data = response.json()
        ativos = data.get('stocks', [])

        if not ativos:
            print("Nenhum ativo encontrado na resposta da API.")
            return None

        print("Processando dados...")
        # Converte a lista de ativos em um DataFrame do pandas
        df_ativos = pd.DataFrame(ativos)

        # Filtra tickers que não terminam com 'F' (não fracionados) e não são do tipo 'bdr'
        df_ativos = df_ativos[
            ~df_ativos['stock'].str.endswith('F') &
            (df_ativos['type'] != 'bdr')
        ]

        # Remove o setor 'Miscellaneous' e ativos com setor nulo, vazio ou 'N/A'
        df_ativos = df_ativos[
            (df_ativos['sector'] != 'Miscellaneous') &
            (df_ativos['sector'].notna()) &
            (df_ativos['sector'].str.strip() != '') &
            (df_ativos['sector'] != 'N/A')
        ]

        # Define um dicionário para renomear as colunas para o padrão português
        colunas_renomear = {
            'stock': 'ticker',
            'sector': 'setor_brapi',
            'type': 'tipo',
            'volume': 'volume',
            'logo': 'logo',
            'changePercent': 'percentual_variacao'  # Renomeia se a coluna existir
        }
        df_ativos = df_ativos.rename(columns=colunas_renomear)

        # Define as colunas a serem removidas e as remove do DataFrame, se existirem
        colunas_remover = [col for col in ['change', 'market_cap', 'name', 'close'] if col in df_ativos.columns]
        if colunas_remover:
            df_ativos = df_ativos.drop(columns=colunas_remover)
            print(f"Colunas removidas: {colunas_remover}")
        else:
            print("Nenhuma das colunas alvo para remoção foi encontrada.")

        # Realiza a limpeza dos dados, preenchendo valores nulos e vazios com 'N/A'
        df_ativos = df_ativos.fillna('N/A')
        # Remove espaços em branco do início e fim das strings
        df_ativos = df_ativos.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df_ativos = df_ativos.replace('', 'N/A')

        # Garante que o diretório de saída exista
        base_dir.mkdir(parents=True, exist_ok=True)

        # Salva o DataFrame limpo em um arquivo CSV
        csv_path = base_dir / csv_output
        df_ativos.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"Arquivo CSV salvo com sucesso em: {csv_path}")

        elapsed_time = time.time() - start_time
        print(f"Concluído em {elapsed_time:.2f} segundos. Total de ativos: {len(df_ativos)}")
        return df_ativos

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição à API: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None

if __name__ == "__main__":
    df = extrair_dados_brapi()
    if df is not None:
        print("\nAmostra dos primeiros 5 ativos:")
        print(df.head().to_string(index=False))
        print(f"\nColunas disponíveis: {list(df.columns)}")