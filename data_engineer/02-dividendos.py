# -*- coding: utf-8 -*-
"""
💰 Script para Coleta de Histórico de Dividendos

Este script utiliza a biblioteca yfinance para buscar o histórico de dividendos
dos últimos 7 anos para uma lista de tickers da B3.

Etapas do Processo:
1.  Lê os tickers do arquivo Parquet gerado anteriormente.
2.  Para cada ticker, consulta a API do Yahoo Finance.
3.  Filtra os dividendos para manter apenas os dos últimos 7 anos.
4.  Normaliza as datas e consolida os dados.
5.  Salva o resultado final em formato Parquet.
6.  Exibe o progresso e informa sobre tickers com erros.
"""
import warnings
from pathlib import Path

import pandas as pd
import yfinance as yf
from tqdm.auto import tqdm

# Importa as utilidades comuns do pipeline
from common import get_tickers, save_to_parquet

# Ignora avisos de FutureWarning para manter o output limpo
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Leitura e Preparação dos Tickers ---
tickers = get_tickers()

# --- Definição do Período de Busca ---
# Define o intervalo de 7 anos a partir da data atual
start_date = (pd.Timestamp.now() - pd.DateOffset(years=7)).strftime('%Y-%m-%d')
end_date = pd.Timestamp.now().strftime('%Y-%m-%d')
print(f"Buscando dividendos de {start_date} a {end_date}.")

# Lista para armazenar os dataframes de dividendos de cada ativo
todos_dividendos = []
erros = []

# Itera sobre a lista de tickers com uma barra de progresso
for ticker in tqdm(tickers, desc="Coletando dividendos (7 anos)"):
    ticker_yf = f"{ticker}.SA"
    try:
        # Obtém a série temporal de dividendos diretamente para o período
        dividendos = yf.Ticker(ticker_yf).dividends

        # Processamento e filtro dos dados
        if not dividendos.empty:
            df_div = dividendos.reset_index()
            
            if len(df_div.columns) == 2:
                df_div.columns = ['data', 'valor']
            else:
                print(f"Formato inesperado de dividendos para {ticker_yf}: {df_div.columns}")
                continue

            df_div['data'] = pd.to_datetime(df_div['data']).dt.tz_localize(None)
            df_div['ticker'] = ticker  # Adiciona o ticker original (sem .SA)
            
            # Filtra os dividendos para o período de 7 anos definido
            df_div = df_div[(df_div['data'] >= start_date) & (df_div['data'] <= end_date)]

            if not df_div.empty:
                todos_dividendos.append(df_div)
            
    except Exception as e:
        erros.append((ticker, e))

# --- Consolidação e Salvamento dos Dados ---
if todos_dividendos:
    print("\nConsolidando dados...")
    # Concatena a lista de dataframes em um único dataframe final
    df_final = pd.concat(todos_dividendos, ignore_index=True)
    
    # Salva o resultado em um arquivo Parquet
    save_to_parquet(df_final, "todos_dividendos")
    
    print(f"{len(df_final)} registros de dividendos processados.")
else:
    print("Nenhum dividendo encontrado para os tickers e período informados.")
    
if erros:
    print("\n--- Tickers com Erro ---")
    for ticker_err, erro_msg in erros:
        print(f"{ticker_err}: {erro_msg}")