
import requests
import pandas as pd

API_KEY = "1JOMGFU25K7B600A"
symbol = "TAEE4.SA" # TAEE4 na bolsa brasileira
function = "TIME_SERIES_DAILY" # Série temporal diária

url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&outputsize=full&apikey={API_KEY}'
r = requests.get(url)
data = r.json()

if "Time Series (Daily)" in data:
    # Acessa os dados da série temporal
    time_series_data = data["Time Series (Daily)"]

    # Converte os dados para um DataFrame do pandas
    df = pd.DataFrame.from_dict(time_series_data, orient='index')

    # Renomeia as colunas para facilitar a leitura
    df.columns = ['open', 'high', 'low', 'close', 'volume']

    # Converte os tipos de dados para numérico
    df = df.apply(pd.to_numeric)

    # Inverte a ordem das linhas para ter a data mais antiga primeiro
    df = df.sort_index()

    print(df.tail()) # Exibe as primeiras 5 linhas para ver o resultado
else:
    print("Erro ao obter dados. Verifique sua API Key ou o símbolo da ação.")