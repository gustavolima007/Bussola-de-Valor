import yfinance as yf
import pandas as pd

def get_pl_ratio(ticker):
    """
    Obtém o índice P/L (Preço/Lucro) via yfinance (TTM).
    """
    try:
        stock = yf.Ticker(ticker + '.SA')  # Sufixo .SA para B3
        info = stock.info
        # P/L = Preço da ação / Lucro por ação (EPS, TTM)
        pl_ratio = info.get('trailingPE', None)
        if pl_ratio is not None:
            return f"{pl_ratio:.2f}"
        return "Não disponível"
    except Exception as e:
        return f"Erro: {str(e)}"

# Tickers solicitados
tickers = ['TAEE4', 'SANB4', 'BBSE3']

# Coleta dados
data = []
for ticker in tickers:
    pl = get_pl_ratio(ticker)
    data.append({
        'Ticker': ticker,
        'P/L': pl
    })

# Cria DataFrame com duas colunas
df = pd.DataFrame(data)

# Exibe a tabela
print("Índice P/L (Preço/Lucro) - TTM:")
print(df[['Ticker', 'P/L']].to_string(index=False))
