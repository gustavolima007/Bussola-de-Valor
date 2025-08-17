import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Coleta, para cada ticker da lista, os dividendos dos últimos 7 anos via yfinance,
# normaliza datas e tickers, consolida em um único DataFrame e salva em ../data/todos_dividendos.csv,
# registrando no console os tickers com e sem pagamentos recentes.


# Caminho do arquivo CSV com os tickers (sem .env)
csv_path = "../data/acoes_e_fundos.csv"

# Lê o CSV e extrai os tickers
df = pd.read_csv(csv_path)
tickers = df['ticker'].dropna().unique().tolist()

# Define o período de 7 anos
end_date = datetime.today()
start_date = end_date - timedelta(days=7*365)

todos_dividendos = []

for ticker in tickers:
    try:
        acao = yf.Ticker(ticker)
        dividendos = acao.dividends

        # Remove timezone do índice
        dividendos.index = dividendos.index.tz_localize(None)

        # Filtra dividendos dos últimos 7 anos
        dividendos = dividendos[dividendos.index >= start_date]

        if not dividendos.empty:
            df_div = dividendos.reset_index()
            df_div.columns = ['Data', 'Valor']
            df_div['Ticker'] = ticker.replace('.SA', '')
            todos_dividendos.append(df_div)

            print(f"✅ Dividendos coletados para {ticker}")
        else:
            print(f"⚠️ Sem dividendos recentes para {ticker}")
    except Exception as e:
        print(f"❌ Erro ao processar {ticker}: {e}")

# Junta tudo em um único DataFrame
df_final = pd.concat(todos_dividendos, ignore_index=True)

# Salva em um único CSV
df_final.to_csv("../data/todos_dividendos.csv", index=False)

print("🏁 Finalizado! Dividendos salvos em todos_dividendos.csv")
