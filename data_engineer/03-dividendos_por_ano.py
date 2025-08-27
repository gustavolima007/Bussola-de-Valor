# -*- coding: utf-8 -*-
"""
📅 Script para Agregação Anual de Dividendos

Este script processa o histórico de dividendos e calcula o valor total
pago por cada ativo em cada ano.

Etapas do Processo:
1.  Lê o arquivo 'data/todos_dividendos.csv' que contém o histórico detalhado.
2.  Converte a coluna de data para o formato datetime.
3.  Extrai o ano de cada registro de dividendo.
4.  Agrupa os dados por ticker e ano, somando os valores dos dividendos.
5.  Renomeia as colunas para um padrão consistente (minúsculas).
6.  Salva o resultado agregado no arquivo 'data/dividendos_ano.csv'.
"""

import pandas as pd
from pathlib import Path

# --- Configuração de Caminhos ---
# Define o diretório base 'data' para leitura e escrita dos arquivos
BASE = Path(__file__).resolve().parent.parent / 'data'
input_path = BASE / 'todos_dividendos.csv'
output_path = BASE / 'dividendos_ano.csv'

# --- Leitura e Processamento dos Dados ---
print(f"Lendo dados de dividendos de: {input_path}")
df = pd.read_csv(input_path)

# Converte a coluna 'Data' para o formato datetime e extrai o ano
print("Processando datas e agregando dividendos por ano...")
df['Data'] = pd.to_datetime(df['Data'])
df['ano'] = df['Data'].dt.year

# Renomeia as colunas para um padrão em minúsculas para consistência
df = df.rename(columns={'Ticker': 'ticker', 'Valor': 'dividendo', 'Data': 'data'})

# Agrupa por 'ano' e 'ticker' e soma os dividendos anuais
soma_por_ano_ticker = df.groupby(['ano', 'ticker'])['dividendo'].sum().reset_index()

# --- Salvamento do Resultado ---
soma_por_ano_ticker.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"✅ Arquivo 'dividendos_ano.csv' gerado com sucesso em: {output_path}")