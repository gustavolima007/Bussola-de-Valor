# -*- coding: utf-8 -*-
"""
💸 Script para Cálculo de Dividend Yield (DY)

Este script calcula o Dividend Yield para duas janelas de tempo:
- DY projetivo dos últimos 5 anos (média anual).
- DY dos últimos 12 meses.

Etapas do Processo:
1.  Lê os arquivos de preços ('data/precos_acoes.csv') e de dividendos
    ('data/dividendos_ano_resumo.csv').
2.  Normaliza os tickers em ambos os DataFrames para garantir a consistência
    antes de uni-los.
3.  Junta as informações de preço e dividendos em um único DataFrame.
4.  Calcula o 'DY5anos' (média dos dividendos dos últimos 5 anos / preço atual).
5.  Calcula o 'DY12M' (dividendos dos últimos 12 meses / preço atual).
6.  Formata e arredonda os resultados.
7.  Salva o DataFrame final em 'data/dividend_yield.csv'.
"""

import pandas as pd
from pathlib import Path

# --- Configuração de Caminhos ---
# Define o diretório base 'data' para leitura e escrita dos arquivos
BASE = Path(__file__).resolve().parent.parent / 'data'
precos_path = BASE / "precos_acoes.csv"
dividendos_path = BASE / "dividendos_ano_resumo.csv"
output_path = BASE / "dividend_yield.csv"

# --- Leitura dos Dados ---
print(f"Lendo dados de preços de: {precos_path}")
precos = pd.read_csv(precos_path)

print(f"Lendo resumo de dividendos de: {dividendos_path}")
div = pd.read_csv(dividendos_path)

# --- Preparação e Limpeza dos Dados ---
print("Normalizando e preparando os dados para o cálculo...")
# Normaliza os tickers para garantir a correspondência, removendo '.SA' e espaços
precos["ticker_base"] = (
    precos["ticker"].astype(str).str.upper().str.strip().str.replace(".SA", "", regex=False)
)
div["ticker_base"] = div["ticker"].astype(str).str.upper().str.strip()

# Converte as colunas para tipo numérico, tratando erros que possam surgir
precos["fechamento_atual"] = pd.to_numeric(precos["fechamento_atual"], errors="coerce")
div["valor_5anos"] = pd.to_numeric(div["valor_5anos"], errors="coerce")
div["valor_12m"] = pd.to_numeric(div["valor_12m"], errors="coerce")

# --- Consolidação dos Dados ---
# Junta os DataFrames de preços e dividendos usando o ticker normalizado
# 'how=left' garante que todos os tickers do arquivo de preços sejam mantidos
df = precos.merge(div[["ticker_base", "valor_5anos", "valor_12m"]], on="ticker_base", how="left")

# --- Cálculo do Dividend Yield ---
print("Calculando o Dividend Yield (5 anos e 12 meses)...")
# Calcula o DY dos últimos 5 anos (média anual)
# A cláusula .where() evita divisão por zero
df["DY5anos"] = (((df["valor_5anos"] / 5) / df["fechamento_atual"]) * 100).where(df["fechamento_atual"] > 0)

# Calcula o DY dos últimos 12 meses
df["DY12M"] = ((df["valor_12m"] / df["fechamento_atual"]) * 100).where(df["fechamento_atual"] > 0)

# Arredonda os resultados para duas casas decimais
df["DY5anos"] = df["DY5anos"].round(2)
df["DY12M"] = df["DY12M"].round(2)

# --- Finalização e Salvamento ---
# Seleciona e reordena as colunas finais
df_final = df[["ticker", "DY5anos", "DY12M"]]

# Garante que o diretório de saída exista
BASE.mkdir(parents=True, exist_ok=True)

# Salva o resultado em um arquivo CSV
df_final.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\nArquivo 'dividend_yield.csv' salvo com sucesso em: {output_path}")