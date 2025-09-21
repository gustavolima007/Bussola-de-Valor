import yfinance as yf

# O sufixo ".SA" é necessário para ações brasileiras no Yahoo Finance
ticker = yf.Ticker("BBAS3.SA")

# O dicionário 'info' contém todos os dados fundamentalistas disponíveis
info = ticker.info

print("Campos de dados disponíveis para BBAS3.SA via yfinance:")
# Imprime todas as chaves (nomes dos campos) em ordem alfabética
for key in sorted(info.keys()):
    print(f"- {key}")