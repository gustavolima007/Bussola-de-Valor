import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# Define os caminhos dos arquivos de saída
base_path = os.path.join(os.path.dirname(__file__), '..', 'data')
output_recent_path = os.path.join(base_path, 'ibovespa.csv')
output_annual_path = os.path.join(base_path, 'ibovespa_anual.csv')

def get_and_save_ibov():
    """Busca dados recentes e anuais do Ibovespa e salva em arquivos CSV."""
    try:
        print("Buscando dados do Ibovespa (^BVSP)...")
        ibov = yf.Ticker("^BVSP")
        
        # --- 1. DADOS RECENTES (para a métrica) ---
        hist_recent = ibov.history(period="1mo") # Aumenta para 1 mês por segurança
        if not hist_recent.empty:
            hist_recent.reset_index(inplace=True)
            hist_recent.columns = [col.lower() for col in hist_recent.columns]
            os.makedirs(base_path, exist_ok=True)
            hist_recent.to_csv(output_recent_path, index=False)
            print(f"Dados recentes do Ibovespa salvos em: {output_recent_path}")
        else:
            print("Não foram retornados dados recentes para o Ibovespa.")

        # --- 2. DADOS ANUAIS (último registro dos últimos 10 anos) ---
        # Pega o histórico de 11 anos para garantir que temos 10 anos completos
        hist_multi_year = ibov.history(period="11y")
        if not hist_multi_year.empty:
            hist_multi_year.reset_index(inplace=True)
            hist_multi_year.columns = [col.lower() for col in hist_multi_year.columns]
            hist_multi_year['year'] = pd.to_datetime(hist_multi_year['date']).dt.year

            # Pega o último registro de cada ano
            annual_summary = hist_multi_year.groupby('year').last().reset_index()

            # Filtra para manter apenas os últimos 10 anos a partir do ano atual
            current_year = datetime.now().year
            annual_summary = annual_summary[annual_summary['year'] >= current_year - 10]

            annual_summary.to_csv(output_annual_path, index=False)
            print(f"Resumo anual do Ibovespa salvo em: {output_annual_path}")
        else:
            print("Não foram retornados dados históricos (10 anos) para o Ibovespa.")
            
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    get_and_save_ibov()
