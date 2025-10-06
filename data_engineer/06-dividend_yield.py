# -*- coding: utf-8 -*-
"""
💸 Script para Cálculo de Dividend Yield (DY)

Este script calcula o Dividend Yield para duas janelas de tempo:
- DY projetivo dos últimos 5 anos (média anual).
- DY dos últimos 12 meses.

Etapas do Processo:
1.  Lê os arquivos Parquet de preços ('precos_acoes.parquet') e de dividendos
    ('dividendos_ano_resumo.parquet').
2.  Junta as informações de preço e dividendos em um único DataFrame.
3.  Calcula o 'DY5anos' (média dos dividendos dos últimos 5 anos / preço atual).
4.  Calcula o 'DY12M' (dividendos dos últimos 12 meses / preço atual).
5.  Formata e arredonda os resultados.
6.  Salva o DataFrame final em formato Parquet.
"""

import pandas as pd
from pathlib import Path

# Importa as utilidades comuns do pipeline
from common import LAND_DW_DIR, save_to_parquet

# --- Configuração de Caminhos ---
precos_path = LAND_DW_DIR / "precos_acoes.parquet"
dividendos_path = LAND_DW_DIR / "dividendos_ano_resumo.parquet"

# --- Leitura dos Dados ---
print(f"Lendo preços: {precos_path.name}")
try:
    precos = pd.read_parquet(precos_path)
except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado: '{precos_path}'.")
    print("Execute '05-preco_acoes.py' antes de continuar.")
    exit()

print(f"Lendo dividendos: {dividendos_path.name}")
try:
    div = pd.read_parquet(dividendos_path)
except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado: '{dividendos_path}'.")
    print("Execute '04-dividendos_ano_resumo.py' antes de continuar.")
    exit()

# --- Preparação e Limpeza dos Dados ---
print("Normalizando dados...")

# Converte as colunas para tipo numérico, tratando erros
precos["fechamento_atual"] = pd.to_numeric(precos["fechamento_atual"], errors="coerce")
div["valor_5anos"] = pd.to_numeric(div["valor_5anos"], errors="coerce")
div["valor_12m"] = pd.to_numeric(div["valor_12m"], errors="coerce")

# --- Consolidação dos Dados ---
# Junta os DataFrames de preços e dividendos usando o ticker
df = pd.merge(precos, div, on="ticker", how="left")

# --- Cálculo do Dividend Yield ---
print("Calculando Dividend Yield (5a e 12m)...")
# Calcula o DY dos últimos 5 anos (média anual)
df["DY5anos"] = (((df["valor_5anos"] / 5) / df["fechamento_atual"]) * 100).where(df["fechamento_atual"] > 0)

# Calcula o DY dos últimos 12 meses
df["DY12m"] = ((df["valor_12m"] / df["fechamento_atual"]) * 100).where(df["fechamento_atual"] > 0)

# Arredonda os resultados para duas casas decimais
df["DY5anos"] = df["DY5anos"].round(2)
df["DY12m"] = df["DY12m"].round(2)

# --- Finalização e Salvamento ---
# Seleciona e reordena as colunas finais
df_final = df[["ticker", "DY5anos", "DY12m"]]

# Salva o resultado em um arquivo Parquet
save_to_parquet(df_final, "dividend_yield")

print(f"Cálculo de Dividend Yield concluído.")