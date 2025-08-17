import pandas as pd
# Agrega os dividendos por ano e ticker a partir de ../data/todos_dividendos.csv,
# padronizando colunas e salvando o total anual por ativo em ../data/dividendos_ano.csv.


# Ler o arquivo CSV
df = pd.read_csv('../data/todos_dividendos.csv')

# Converter a coluna 'Data' para datetime e extrair o ano
df['Data'] = pd.to_datetime(df['Data'])
df['ano'] = df['Data'].dt.year

# Renomear colunas para minúsculas
df = df.rename(columns={'Ticker': 'ticker', 'Valor': 'dividendo', 'Data': 'data'})

# Somar os dividendos por ano e ticker
soma_por_ano_ticker = df.groupby(['ano', 'ticker'])['dividendo'].sum().reset_index()

# Salvar o resultado em um CSV
soma_por_ano_ticker.to_csv('../data/dividendos_ano.csv', index=False)
print("Arquivo 'dividendos_ano.csv' gerado com sucesso!")