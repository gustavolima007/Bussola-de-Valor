import pandas as pd
from tqdm.auto import tqdm

# Calcula o Preço Teto a partir de dividendos dos últimos 5 anos (Bazin):
# junta dividendos_ano_resumo.csv com precos_acoes.csv, calcula preco_teto_5anos
# e diferenca_percentual versus o preço atual, salvando em ../data/preco_teto.csv.

# Definir a porcentagem de dividendo para cálculo do preço teto
dividendo_porcentagem = 100 / 6

from pathlib import Path
BASE = Path(__file__).resolve().parent.parent / 'data'

# Carregar os dados dos CSVs
resumo = pd.read_csv(BASE / "dividendos_ano_resumo.csv")
preco_acoes = pd.read_csv(BASE / "precos_acoes.csv")

# Adicionar o sufixo .SA aos tickers de dividendos_ano_resumo.csv
resumo['ticker'] = resumo['ticker'] + '.SA'

# Fazer o merge dos dados com base no ticker
dados = resumo.merge(preco_acoes, on='ticker', how='left')

# Calcular o preço teto
# Preço teto 5 anos = (valor_5anos / 5) * dividendo_porcentagem
dados['preco_teto_5anos'] = ((dados['valor_5anos'] / 5) * dividendo_porcentagem).round(2)

# Calcular a diferença percentual: ((preco_teto_5anos - fechamento_atual) / fechamento_atual) * 100
# Evitar divisão por zero e lidar com NaN
dados['diferenca_percentual'] = dados.apply(
    lambda row: round(((row['preco_teto_5anos'] - row['fechamento_atual']) / row['fechamento_atual'] * 100), 2)
    if pd.notnull(row['preco_teto_5anos']) and pd.notnull(row['fechamento_atual']) and row['fechamento_atual'] != 0
    else float('nan'),
    axis=1
)

# Selecionar apenas as colunas necessárias
resultado = dados[['ticker', 'preco_teto_5anos', 'diferenca_percentual']]

# Salvar o resultado em um novo CSV
resultado.to_csv(BASE / 'preco_teto.csv', index=False)
print("Arquivo 'preco_teto.csv' gerado com sucesso!")

# Mostrar as 5 primeiras linhas do resultado
print(resultado.head(5))