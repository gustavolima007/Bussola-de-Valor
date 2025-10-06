# -*- coding: utf-8 -*-
"""
📈 Script para Coleta de Dados de Índices da B3

- Busca os valores de fechamento anual dos principais índices (via ETFs) nos últimos 5 anos.
- Calcula indicadores técnicos (RSI, MACD, Volume).
- Gera um arquivo Parquet consolidado.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD
from common import save_to_parquet

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
    if hist.empty or len(hist) < 35:
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
    
    tecnicos = compute_indicadores_tecnicos(hist)
    annual = pd.DataFrame()
    current_year = datetime.now().year
    
    for year in range(current_year - 4, current_year + 1):
        year_data = hist[hist['year'] == year]
        if not year_data.empty:
            last_day = year_data[year_data['Date'] == year_data['Date'].max()]
            if not last_day.empty:
                last_day = last_day.copy()
                last_day.loc[:, 'index'] = index_name
                for key, value in tecnicos.items():
                    last_day.loc[:, key] = value
                
                cols_to_keep = ['year', 'index', 'Close', 'rsi', 'macd', 'volume']
                annual = pd.concat([annual, last_day[[c for c in cols_to_keep if c in last_day.columns]]], ignore_index=True)
    
    return annual[annual['year'] >= current_year - 5]

def get_and_save_indices():
    try:
        all_data = pd.DataFrame()
        print("Coletando dados dos índices da B3...\n")
        for code, name in indices.items():
            print(f"  - {name} ({code})...")
            df = get_annual_closing(code, name)
            if df.empty:
                print(f"    Dados não encontrados para {name}.")
            else:
                anos = df['year'].nunique()
                if anos < 5:
                    print(f"    Apenas {anos} anos disponíveis para {name}.")
                else:
                    print(f"    Dados de {name} coletados.")
                all_data = pd.concat([all_data, df], ignore_index=True)
                
        if not all_data.empty:
            all_data.columns = [col.lower() for col in all_data.columns]
            all_data['close'] = all_data['close'].round(2)
            save_to_parquet(all_data, "indices")
            print(f"\nColeta de dados de índices concluída.")
        else:
            print("\nNenhum dado retornado para os índices.")
   
    except Exception as e:
        print(f"\nErro inesperado: {e}")

if __name__ == "__main__":
    get_and_save_indices()