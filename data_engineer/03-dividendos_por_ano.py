import pandas as pd
from tqdm.auto import tqdm
# Agrega os dividendos por ano e ticker a partir de ../data/todos_dividendos.csv,
# padronizando colunas e salvando o total anual por ativo em ../data/dividendos_ano.csv.


from pathlib import Path

# Caminho relativo ao script
BASE = Path(__file__).resolve().parent.parent / 'data'

# Ler o arquivo CSV
df = pd.read_csv(BASE / 'todos_dividendos.csv')

# Converter a coluna 'Data' para datetime e extrair o ano
df['Data'] = pd.to_datetime(df['Data'])
df['ano'] = df['Data'].dt.year

# Renomear colunas para minúsculas
df = df.rename(columns={'Ticker': 'ticker', 'Valor': 'dividendo', 'Data': 'data'})

# Somar os dividendos por ano e ticker
soma_por_ano_ticker = df.groupby(['ano', 'ticker'])['dividendo'].sum().reset_index()

# Salvar o resultado em um CSV
soma_por_ano_ticker.to_csv(BASE / 'dividendos_ano.csv', index=False)
print(f"Arquivo 'dividendos_ano.csv' gerado com sucesso em: {BASE / 'dividendos_ano.csv'}")