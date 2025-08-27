# -*- coding: utf-8 -*-
"""
💰 Script para Coleta de Histórico de Dividendos

Este script utiliza a biblioteca yfinance para buscar o histórico de dividendos
dos últimos 7 anos para uma lista de tickers da B3.

Etapas do Processo:
1.  Lê os tickers do arquivo 'data/acoes_e_fundos.csv'.
2.  Para cada ticker, consulta a API do Yahoo Finance.
3.  Filtra os dividendos para manter apenas os dos últimos 7 anos.
4.  Normaliza as datas e consolida os dados.
5.  Salva o resultado final em 'data/todos_dividendos.csv'.
6.  Exibe o progresso e informa sobre tickers com erros.
"""
import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from tqdm.auto import tqdm
from pathlib import Path
import warnings

# Ignora avisos de FutureWarning para manter o output limpo
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Configuração de Caminhos ---
# Define o diretório base 'data' para leitura e escrita dos arquivos
BASE = Path(__file__).resolve().parent.parent / 'data'
csv_path = BASE / "acoes_e_fundos.csv"
output_path = BASE / "todos_dividendos.csv"

# --- Leitura e Preparação dos Tickers ---
print(f"Lendo tickers de: {csv_path}")
df = pd.read_csv(csv_path)
# Extrai, limpa e garante que a lista de tickers não tenha duplicatas
tickers = df['ticker'].dropna().astype(str).str.strip().str.upper().unique().tolist()
print(f"Encontrados {len(tickers)} tickers únicos.")

# --- Definição do Período de Busca ---
# Define o intervalo de 7 anos a partir da data atual
end_date = datetime.today()
start_date = end_date - timedelta(days=7*365)
print(f"Buscando dividendos de {start_date.strftime('%Y-%m-%d')} até {end_date.strftime('%Y-%m-%d')}")

# Lista para armazenar os dataframes de dividendos de cada ativo
todos_dividendos = []

# --- Coleta de Dados via yfinance ---
# Itera sobre a lista de tickers com uma barra de progresso
for ticker in tqdm(tickers, desc="Coletando dividendos (7 anos)"):
    try:
        # Adiciona o sufixo .SA, padrão do Yahoo Finance para ativos da B3
        ticker_yf = f"{ticker}.SA"
        acao = yf.Ticker(ticker_yf)
        
        # Obtém a série temporal de dividendos
        dividendos = acao.dividends

        # Garante que o índice da série seja do tipo DatetimeIndex
        if not isinstance(dividendos.index, pd.DatetimeIndex):
            dividendos.index = pd.to_datetime(dividendos.index, errors='coerce')
        
        # Remove o fuso horário (timezone) para padronizar as datas
        if getattr(dividendos.index, "tz", None) is not None:
            dividendos.index = dividendos.index.tz_localize(None)

        # Filtra os dividendos para o período de 7 anos definido
        mask_date = dividendos.index >= pd.to_datetime(start_date)
        dividendos_periodo = dividendos[mask_date]

        # Verifica se existem dividendos no período antes de processar
        if not dividendos_periodo.empty:
            df_div = dividendos_periodo.reset_index()
            df_div.columns = ['Data', 'Valor']  # Renomeia as colunas
            df_div['Ticker'] = ticker  # Adiciona o ticker original (sem .SA)
            todos_dividendos.append(df_div)

    except Exception as e:
        # Captura e informa erros durante o processo para um ticker específico
        print(f"❌ Erro ao processar {ticker_yf}: {e}")

# --- Consolidação e Salvamento dos Dados ---
if todos_dividendos:
    print("\nConsolidando e salvando os dados...")
    # Concatena a lista de dataframes em um único dataframe final
    df_final = pd.concat(todos_dividendos, ignore_index=True)
    
    # Salva o resultado em um arquivo CSV
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"🏁 Finalizado! {len(df_final)} registros de dividendos salvos em {output_path}")
else:
    print("⚠️ Nenhum dividendo encontrado no período para os tickers fornecidos.")
