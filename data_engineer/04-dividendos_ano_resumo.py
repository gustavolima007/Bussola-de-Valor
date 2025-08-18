import pandas as pd
from tqdm.auto import tqdm
# Consolida dividendos por ticker em duas janelas: soma dos últimos 5 anos e dos últimos 12 meses,
# a partir de ../data/dividendos_ano.csv, e salva em ../data/dividendos_ano_resumo.csv.


from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / 'data'

# Carregar os dividendos por ano e ticker
df = pd.read_csv(BASE / 'dividendos_ano.csv')

# Descobrir o último ano disponível
ultimo_ano = df['ano'].max()

# Dividendos dos últimos 5 anos
div_5anos = df[df['ano'] >= ultimo_ano - 4]
soma_5anos = div_5anos.groupby('ticker')['dividendo'].sum().reset_index()
soma_5anos = soma_5anos.rename(columns={'dividendo': 'valor_5anos'})

# Dividendos dos últimos 12 meses
div_12m = df[df['ano'] == ultimo_ano]
soma_12m = div_12m[['ticker', 'dividendo']].rename(columns={'dividendo': 'valor_12m'})

# Juntar os dois
resumo = pd.merge(soma_5anos, soma_12m, on='ticker', how='outer').fillna(0)

# Reorganizar colunas
resumo = resumo[['ticker', 'valor_5anos', 'valor_12m']]

# Salvar resultado
resumo.to_csv(BASE / 'dividendos_ano_resumo.csv', index=False)
print(f"Arquivo 'dividendos_ano_resumo.csv' gerado com sucesso em: {BASE / 'dividendos_ano_resumo.csv'}")
print(resumo.head())
print(resumo.shape)