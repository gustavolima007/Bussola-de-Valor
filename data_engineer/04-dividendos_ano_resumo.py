# -*- coding: utf-8 -*-
"""
📊 Script para Resumo de Dividendos em Janelas de Tempo

Este script calcula a soma de dividendos para cada ticker em duas janelas
de tempo específicas: os últimos 5 anos e os últimos 12 meses.

Etapas do Processo:
1.  Lê o arquivo 'data/dividendos_ano.csv', que contém os totais anuais.
2.  Identifica o ano mais recente presente nos dados.
3.  Calcula a soma dos dividendos dos últimos 5 anos para cada ticker.
4.  Calcula a soma dos dividendos do último ano (últimos 12 meses).
5.  Junta os resultados em um único DataFrame.
6.  Salva o resumo consolidado em 'data/dividendos_ano_resumo.csv'.
"""

import pandas as pd
from pathlib import Path

# --- Configuração de Caminhos ---
# Define o diretório base 'data' para leitura e escrita dos arquivos
BASE = Path(__file__).resolve().parent.parent / 'data'
input_path = BASE / 'dividendos_ano.csv'
output_path = BASE / 'dividendos_ano_resumo.csv'

# --- Leitura dos Dados ---
print(f"Lendo dados anuais de dividendos de: {input_path}")
df = pd.read_csv(input_path)

# --- Cálculos de Janelas de Tempo ---
# Encontra o ano mais recente no conjunto de dados
ultimo_ano = df['ano'].max()
print(f"Último ano de referência encontrado: {ultimo_ano}")

# 1. Soma de dividendos nos últimos 5 anos
print("Calculando a soma de dividendos dos últimos 5 anos...")
div_5anos = df[df['ano'] >= ultimo_ano - 4]
soma_5anos = div_5anos.groupby('ticker')['dividendo'].sum().reset_index()
soma_5anos = soma_5anos.rename(columns={'dividendo': 'valor_5anos'})

# 2. Soma de dividendos nos últimos 12 meses (equivalente ao último ano completo)
print("Calculando a soma de dividendos dos últimos 12 meses...")
div_12m = df[df['ano'] == ultimo_ano]
soma_12m = div_12m[['ticker', 'dividendo']].rename(columns={'dividendo': 'valor_12m'})

# --- Consolidação e Salvamento ---
print("Consolidando os resultados...")
# Junta os dois DataFrames (5 anos e 12 meses) usando o ticker como chave
resumo = pd.merge(soma_5anos, soma_12m, on='ticker', how='outer').fillna(0)

# Reorganiza as colunas para o formato final
resumo = resumo[['ticker', 'valor_5anos', 'valor_12m']]

# Salva o DataFrame de resumo em um novo arquivo CSV
resumo.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n✅ Arquivo 'dividendos_ano_resumo.csv' gerado com sucesso em: {output_path}")
print("\nAmostra dos dados gerados:")
print(resumo.head())
print(f"\nTotal de tickers processados: {resumo.shape[0]}")