# -*- coding: utf-8 -*-
"""
💰 Script para Coleta de Histórico de Dividendos

Este script utiliza a biblioteca yfinance para buscar o histórico de dividendos
dos últimos 7 anos para uma lista de tickers da B3.

Etapas do Processo:
1.  Lê os tickers do arquivo 'data/acoes_e_fundos.csv'.
2.  Para cada ticker, consulta a API do Yahoo Finance.
3.  Filtra os dividendos para manter apenas os dos últimos 7 anos.
4.  Normaliza as datas e consolida os dados.
5.  Salva o resultado final em 'data/todos_dividendos.csv'.
6.  Exibe o progresso e informa sobre tickers com erros.
"""
import warnings
from pathlib import Path

import pandas as pd
import yfinance as yf
from tqdm.auto import tqdm

# Ignora avisos de FutureWarning para manter o output limpo
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Configuração de Caminhos ---
# Define o diretório base 'data' para leitura e escrita dos arquivos
BASE = Path(__file__).resolve().parent.parent / 'data'
CSV_PATH = BASE / "acoes_e_fundos.csv"
OUTPUT_PATH = BASE / "todos_dividendos.csv"

# --- Leitura e Preparação dos Tickers ---
print(f"Lendo tickers de: {CSV_PATH}")
try:
    df_tickers = pd.read_csv(CSV_PATH)
    # Extrai, limpa e garante que a lista de tickers não tenha duplicatas
    tickers = (
        df_tickers['ticker']
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
        .tolist()
    )
    print(f"Encontrados {len(tickers)} tickers únicos.")
except FileNotFoundError:
    print(f"❌ Erro: O arquivo {CSV_PATH} não foi encontrado.")
    tickers = []

# --- Definição do Período de Busca ---
# Define o intervalo de 7 anos a partir da data atual
# yfinance aceita datas no formato 'YYYY-MM-DD'
start_date = (pd.Timestamp.now() - pd.DateOffset(years=7)).strftime('%Y-%m-%d')
end_date = pd.Timestamp.now().strftime('%Y-%m-%d')
print(f"Buscando dividendos de {start_date} até {end_date}")

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
            df_div.columns = ['Data', 'Valor']  # Renomeia as colunas
            df_div['Data'] = pd.to_datetime(df_div['Data']).dt.tz_localize(None) # Normaliza a data
            df_div['Ticker'] = ticker  # Adiciona o ticker original (sem .SA)
            
            # Filtra os dividendos para o período de 7 anos definido
            df_div = df_div[(df_div['Data'] >= start_date) & (df_div['Data'] <= end_date)]

            if not df_div.empty:
                todos_dividendos.append(df_div)
            
    except Exception as e:
        erros.append((ticker_yf, e))

# --- Consolidação e Salvamento dos Dados ---
if todos_dividendos:
    print("\nConsolidando e salvando os dados...")
    # Concatena a lista de dataframes em um único dataframe final
    df_final = pd.concat(todos_dividendos, ignore_index=True)
    
    # Salva o resultado em um arquivo CSV
    df_final.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    
    print(f"🏁 Finalizado! {len(df_final)} registros de dividendos salvos em {OUTPUT_PATH}")
else:
    print("⚠️ Nenhum dividendo encontrado no período para os tickers fornecidos.")
    
if erros:
    print("\n--- Tickers com Erro ---")
    for ticker_err, erro_msg in erros:
        print(f"❌ Erro ao processar {ticker_err}: {erro_msg}")