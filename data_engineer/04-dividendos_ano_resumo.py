# -*- coding: utf-8 -*-
"""
📊 Script para Resumo de Dividendos em Janelas de Tempo

Este script calcula a soma de dividendos para cada ticker em duas janelas
de tempo específicas: os últimos 5 anos e os últimos 12 meses.

Etapas do Processo:
1.  Lê o arquivo Parquet com os totais anuais de dividendos.
2.  Identifica o ano mais recente presente nos dados.
3.  Calcula a soma dos dividendos dos últimos 5 anos para cada ticker.
4.  Calcula a soma dos dividendos do último ano (últimos 12 meses).
5.  Junta os resultados em um único DataFrame.
6.  Salva o resumo consolidado em formato Parquet.
"""

import pandas as pd
from pathlib import Path

# Importa as utilidades comuns do pipeline
from common import LAND_DW_DIR, save_to_parquet

# --- Configuração de Caminhos ---
input_path = LAND_DW_DIR / 'dividendos_ano.parquet'

# --- Leitura dos Dados ---
print(f"ℹ️ Lendo: {input_path.name}")
try:
    df = pd.read_parquet(input_path)
except FileNotFoundError:
    print(f"❌ Erro: Arquivo não encontrado: '{input_path}'.")
    print("➡️ Execute '03-dividendos_por_ano.py' antes de continuar.")
    exit()

if df.empty:
    print("⚠️ Arquivo de entrada vazio. Nenhum dado a processar.")
    exit()

# --- Cálculos de Janelas de Tempo ---
# Encontra o ano mais recente no conjunto de dados
ultimo_ano = df['ano'].max()
print(f"🗓️ Ano de referência: {ultimo_ano}")

# 1. Soma de dividendos nos últimos 5 anos
print("🔄 Calculando dividendos (5 anos)...")
div_5anos = df[df['ano'] >= ultimo_ano - 4]
soma_5anos = div_5anos.groupby('ticker')['dividendo'].sum().reset_index()
soma_5anos = soma_5anos.rename(columns={'dividendo': 'valor_5anos'})

# 2. Soma de dividendos nos últimos 12 meses (equivalente ao último ano completo)
print("🔄 Calculando dividendos (12 meses)...")
div_12m = df[df['ano'] == ultimo_ano]
soma_12m = div_12m[['ticker', 'dividendo']].rename(columns={'dividendo': 'valor_12m'})

# --- Consolidação e Salvamento ---
print("📊 Consolidando resultados...")
# Junta os dois DataFrames (5 anos e 12 meses) usando o ticker como chave
resumo = pd.merge(soma_5anos, soma_12m, on='ticker', how='outer').fillna(0)

# Reorganiza as colunas para o formato final
resumo = resumo[['ticker', 'valor_5anos', 'valor_12m']]

# Salva o DataFrame de resumo em um novo arquivo Parquet
save_to_parquet(resumo, 'dividendos_ano_resumo')

print(f"✅ Resumo de dividendos concluído.")
