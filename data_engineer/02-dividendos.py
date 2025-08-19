import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from tqdm.auto import tqdm
from pathlib import Path
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Coleta, para cada ticker da lista, os dividendos dos últimos 7 anos via yfinance,
# normaliza datas e tickers, consolida em um único DataFrame e salva em ../data/todos_dividendos.csv,
# registrando no console os tickers com e sem pagamentos recentes.


# Caminho do arquivo CSV com os tickers (absoluto baseado no repo)
BASE = Path(__file__).resolve().parent.parent / 'data'
csv_path = BASE / "acoes_e_fundos.csv"

# Lê o CSV e extrai os tickers (base sem .SA)
df = pd.read_csv(csv_path)
tickers = df['ticker'].dropna().astype(str).str.strip().str.upper().unique().tolist()

# Define o período de 7 anos
end_date = datetime.today()
start_date = end_date - timedelta(days=7*365)

todos_dividendos = []

for ticker in tqdm(tickers, desc="Coletando dividendos (7 anos)"):
    try:
        ticker_yf = f"{ticker}.SA"
        acao = yf.Ticker(ticker_yf)
        dividendos = acao.dividends

        # Garante que o índice seja DatetimeIndex e remova timezone se existir
        if not isinstance(dividendos.index, pd.DatetimeIndex):
            dividendos.index = pd.to_datetime(dividendos.index, errors='coerce')
        try:
            if getattr(dividendos.index, "tz", None) is not None:
                dividendos.index = dividendos.index.tz_localize(None)
        except Exception:
            pass

        # Filtra dividendos dos últimos 7 anos
        mask_date = dividendos.index >= pd.to_datetime(start_date)
        dividendos = dividendos[mask_date]

        if dividendos is not None and not getattr(dividendos, 'empty', True):
            df_div = dividendos.reset_index()
            df_div.columns = ['Data', 'Valor']
            df_div['Ticker'] = ticker  # já está sem .SA
            todos_dividendos.append(df_div)
            print(f"✅ Dividendos coletados para {ticker_yf}")
        else:
            print(f"⚠️ Sem dividendos recentes para {ticker_yf}")
    except Exception as e:
        print(f"❌ Erro ao processar {ticker_yf}: {e}")

# Junta tudo em um único DataFrame
df_final = pd.concat(todos_dividendos, ignore_index=True)

# Salva em um único CSV
saida = BASE / "todos_dividendos.csv"
df_final.to_csv(saida, index=False)

print(f"🏁 Finalizado! Dividendos salvos em {saida}")
