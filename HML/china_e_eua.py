import yfinance as yf
import pandas as pd

# Tickers populares com alto volume (exemplos)
tickers_nyse = ['AAPL', 'TSLA', 'AMZN', 'NVDA', 'MSFT']  # EUA
tickers_china = ['BABA', 'JD', 'PDD', 'NIO', 'XPEV']     # China

def obter_dados(tickers, pais):
    dados = []
    for ticker in tickers:
        acao = yf.Ticker(ticker)
        info = acao.info
        dados.append({
            'pais': pais,
            'ticker': ticker,
            'preco_atual': info.get('currentPrice'),
            'volume_mercado': info.get('volume')
        })
    return dados

# Coletar dados
dados_eua = obter_dados(tickers_nyse, 'EUA')
dados_china = obter_dados(tickers_china, 'China')

# Criar DataFrame
df = pd.DataFrame(dados_eua + dados_china)

# Exibir resultado
print(df)
