import yfinance as yf
import pandas as pd
import os
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD
"""
Script: 12-indices.py
Objetivo:
- Buscar os valores de fechamento anual dos principais índices da B3 nos últimos 5 anos.
- Substituir índices teóricos por ETFs equivalentes quando necessário.
- Gerar um arquivo CSV consolidado com os dados em: ../data/indices.csv
Índices incluídos:
- Ibovespa (BOVA11.SA)
- Small Caps (SMAL11.SA)
- Financeiro (FIND11.SA)
- Materiais Básicos (MATB11.SA)
- Dividendos (DIVO11.SA)
Notas:
- O histórico é limitado a 5 anos.
- Alguns ativos podem ter menos dados disponíveis.
- Fechamento anual baseado no último dia útil (2021-2024) ou dia atual (2025).
"""
from common import DATA_DIR, tratar_dados_para_json

output_annual_path = DATA_DIR / 'indices.csv'
indices = {
    "BOVA11.SA": "iShares Ibovespa",
    "SMAL11.SA": "Small Caps",
    "FIND11.SA": "Financeiro (ETF)",
    "MATB11.SA": "Materiais Básicos (ETF)",
    "DIVO11.SA": "Dividendos"
}

def compute_indicadores_tecnicos(hist: pd.DataFrame) -> dict:
    """Calcula RSI, MACD e Volume para um histórico de dados."""
    indicadores = {'rsi': None, 'macd': None, 'volume': None}
    if hist.empty or len(hist) < 35: # MACD precisa de ~35 períodos
        return indicadores

    close = hist['Close']
    indicadores['rsi'] = RSIIndicator(close=close, window=14).rsi().iloc[-1]
    indicadores['macd'] = MACD(close=close, window_slow=26, window_fast=12, window_sign=9).macd_diff().iloc[-1]
    indicadores['volume'] = hist['Volume'].iloc[-1] if 'Volume' in hist.columns and not hist['Volume'].empty else None
    
    return {k: round(v, 2) if v is not None else None for k, v in indicadores.items()}

def get_annual_closing(index_code, index_name):
    ticker = yf.Ticker(index_code)
    hist = ticker.history(period="5y", auto_adjust=True)
    if hist.empty:
        return pd.DataFrame()
   
    hist.reset_index(inplace=True)
    hist['year'] = pd.to_datetime(hist['Date']).dt.year
    
    # Calcula indicadores técnicos com base no histórico completo de 5 anos
    tecnicos = compute_indicadores_tecnicos(hist)
    annual = pd.DataFrame()
    current_year = datetime.now().year
    current_date = datetime.now().date()
    
    for year in range(current_year - 4, current_year + 1):
        year_data = hist[hist['year'] == year]
        if not year_data.empty:
            if year == current_year:  # Para 2025, usa o último dia disponível
                last_day = year_data[year_data['Date'] == year_data['Date'].max()]
            else:  # Para 2021-2024, usa o último dia útil do ano
                last_day = year_data[year_data['Date'] == year_data['Date'].max()]
            if not last_day.empty:
                last_day = last_day.copy()  # Evita o warning criando uma cópia
                last_day.loc[:, 'index'] = index_name  # Usa .loc para atribuição segura
                # Adiciona os indicadores técnicos a cada linha anual (serão os mesmos para o mesmo índice)
                for key, value in tecnicos.items():
                    last_day.loc[:, key] = value
                
                cols_to_keep = ['year', 'index', 'Close', 'rsi', 'macd', 'volume']
                annual = pd.concat([annual, last_day[[c for c in cols_to_keep if c in last_day.columns]]], ignore_index=True)
    
    return annual[annual['year'] >= current_year - 5]
def get_and_save_indices():
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        all_data = pd.DataFrame()
        print("Coletando dados dos índices da B3...\n")
        for code, name in indices.items():
            print(f"{name} ({code})...")
            df = get_annual_closing(code, name)
            if df.empty:
                print(f"Dados não encontrados para {name}.")
            else:
                anos = df['year'].nunique()
                if anos < 5:
                    print(f"Apenas {anos} anos disponíveis para {name}.")
                else:
                    print(f"Dados completos para {name}.")
                all_data = pd.concat([all_data, df], ignore_index=True)
        if not all_data.empty:
            all_data.columns = [col.lower() for col in all_data.columns]
            all_data['close'] = all_data['close'].round(2)
            all_data = tratar_dados_para_json(all_data)
            all_data.to_csv(output_annual_path, index=False)
            print(f"\nResumo anual salvo com sucesso em: {output_annual_path}")
        else:
            print("\nNenhum dado foi retornado para os índices.")
   
    except Exception as e:
        print(f"\nErro inesperado: {e}")
if __name__ == "__main__":
    get_and_save_indices()