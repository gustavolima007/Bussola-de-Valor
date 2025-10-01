# -*- coding: utf-8 -*-
"""
Script para Coleta de P/L (Preço/Lucro) de Ações

Este script utiliza a biblioteca yfinance para obter o índice P/L (TTM) de
todas as ações listadas no arquivo acoes_e_fundos.csv.

O resultado é salvo em um novo arquivo CSV chamado pl_ratio.csv no diretório de dados.
"""

import pandas as pd
import yfinance as yf
from tqdm import tqdm
from pathlib import Path
import time

# --- Configurações ---
DATA_DIR = Path(__file__).parent.parent / "data"
CAMINHO_ARQUIVO_ENTRADA = DATA_DIR / "acoes_e_fundos.csv"
CAMINHO_ARQUIVO_SAIDA = DATA_DIR / "pl_ratio.csv"

def get_pl_ratio(ticker: str) -> str:
    """
    Obtém o índice P/L (Preço/Lucro) via yfinance (TTM).
    """
    try:
        # Adiciona o sufixo .SA para ações da B3 e busca os dados
        stock = yf.Ticker(f"{ticker}.SA")
        info = stock.info
        
        # P/L = Preço da ação / Lucro por ação (EPS, TTM)
        pl_ratio = info.get('trailingPE')
        
        if pl_ratio is not None and pl_ratio > 0:
            return f"{pl_ratio:.2f}"
        return "N/A"
    except Exception:
        return "N/A"

def main():
    """
    Função principal para orquestrar a coleta de P/L.
    """
    print("="*80)
    print("--- Coleta de P/L (Preço/Lucro) ---")
    print("="*80)

    if not CAMINHO_ARQUIVO_ENTRADA.exists():
        print(f"[X] ERRO: Arquivo de entrada não encontrado: {CAMINHO_ARQUIVO_ENTRADA}")
        return

    print(f"[>] Lendo tickers de: {CAMINHO_ARQUIVO_ENTRADA}")
    df_input = pd.read_csv(CAMINHO_ARQUIVO_ENTRADA)
    
    # Filtra apenas por ações (tipo 'stock')
    df_stocks = df_input[df_input['tipo'] == 'stock'].copy()
    tickers = df_stocks['ticker'].unique()
    
    total_tickers = len(tickers)
    print(f"[+] {total_tickers} tickers de ações encontrados.")

    if total_tickers == 0:
        print("[!] Nenhum ticker de ação encontrado para processar.")
        return

    # --- Coleta de Dados ---
    print("\n[>] Coletando P/L para cada ticker...")
    data = []
    
    with tqdm(total=total_tickers, desc="Coletando P/L", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
        for ticker in tickers:
            pl = get_pl_ratio(ticker)
            data.append({
                'ticker': ticker,
                'p_l': pl
            })
            pbar.update(1)
            time.sleep(0.1) # Pausa para evitar rate limiting

    # --- Salvando Resultados ---
    print("\n" + "="*80)
    print("--- Resumo da Execução ---")

    if not data:
        print("[X] ERRO: Nenhum dado de P/L foi coletado.")
        return

    df_output = pd.DataFrame(data)
    
    # Garante que o diretório de saída exista
    CAMINHO_ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    
    # Salva o arquivo
    df_output.to_csv(CAMINHO_ARQUIVO_SAIDA, index=False, encoding='utf-8-sig')
    
    print(f"[+] {len(df_output)} P/L de tickers coletados com sucesso.")
    print(f"    - Arquivo salvo em: {CAMINHO_ARQUIVO_SAIDA}")
    
    # Mostra uma amostra dos dados
    print("\n--- Amostra dos Dados ---")
    print(df_output.head().to_string(index=False))
    print("="*80)

if __name__ == "__main__":
    main()
