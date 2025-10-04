# -*- coding: utf-8 -*-
"""
📅 Script para Agregação Anual de Dividendos

Este script processa o histórico de dividendos e calcula o valor total
pago por cada ativo em cada ano.

Etapas do Processo:
1.  Lê o arquivo Parquet com o histórico detalhado de dividendos.
2.  Converte a coluna de data para o formato datetime.
3.  Extrai o ano de cada registro de dividendo.
4.  Agrupa os dados por ticker e ano, somando os valores dos dividendos.
5.  Renomeia as colunas para um padrão consistente.
6.  Salva o resultado agregado em formato Parquet.
"""

import pandas as pd
from pathlib import Path

# Importa as utilidades comuns do pipeline
from common import LAND_DW_DIR, save_to_parquet

# --- Configuração de Caminhos ---
input_path = LAND_DW_DIR / 'todos_dividendos.parquet'

# --- Leitura e Processamento dos Dados ---
print(f"ℹ️ Lendo: {input_path.name}")
try:
    df = pd.read_parquet(input_path)
except FileNotFoundError:
    print(f"❌ Erro: Arquivo não encontrado: '{input_path}'.")
    print("➡️ Execute '02-dividendos.py' antes de continuar.")
    exit()


# Converte a coluna 'data' para o formato datetime e extrai o ano
print("🔄 Agregando dividendos por ano...")
df['data'] = pd.to_datetime(df['data'])
df['ano'] = df['data'].dt.year

# Renomeia a coluna de valor para clareza
df = df.rename(columns={'valor': 'dividendo'})

# Agrupa por 'ano' e 'ticker' e soma os dividendos anuais
soma_por_ano_ticker = df.groupby(['ano', 'ticker'])['dividendo'].sum().reset_index()

# --- Salvamento do Resultado ---
save_to_parquet(soma_por_ano_ticker, 'dividendos_ano')
print(f"✅ Agregação anual concluída.")