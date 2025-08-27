# -*- coding: utf-8 -*-
"""
🎯 Script para Cálculo do Preço Teto (Método de Bazin)

Este script calcula o "Preço Teto" de ações com base na metodologia de
Décio Bazin, que utiliza a média dos dividendos dos últimos 5 anos e uma
rentabilidade mínima desejada (6%).

Etapas do Processo:
1.  Define a rentabilidade alvo (6%) para o cálculo.
2.  Lê os arquivos com o resumo de dividendos ('data/dividendos_ano_resumo.csv')
    e os preços atuais das ações ('data/precos_acoes.csv').
3.  Normaliza os tickers e garante que os tipos de dados estejam corretos.
4.  Junta as informações de dividendos e preços.
5.  Calcula o Preço Teto: (Média dos dividendos dos últimos 5 anos) / 0.06.
6.  Calcula a diferença percentual entre o Preço Teto e o preço atual.
7.  Salva o resultado em 'data/preco_teto.csv'.
"""

import pandas as pd
from pathlib import Path

# --- Configurações ---
# Define a rentabilidade mínima desejada (6% ao ano)
# O cálculo (100 / 6) resulta no fator multiplicador para a média de dividendos
RENTABILIDADE_ALVO = 0.06

# --- Configuração de Caminhos ---
BASE = Path(__file__).resolve().parent.parent / 'data'
resumo_dividendos_path = BASE / "dividendos_ano_resumo.csv"
precos_path = BASE / "precos_acoes.csv"
output_path = BASE / "preco_teto.csv"

# --- Leitura dos Dados ---
print(f"Lendo resumo de dividendos de: {resumo_dividendos_path}")
resumo_df = pd.read_csv(resumo_dividendos_path)

print(f"Lendo preços de: {precos_path}")
precos_df = pd.read_csv(precos_path)

# --- Preparação e Limpeza dos Dados ---
print("Normalizando e preparando os dados...")
# Garante que as colunas numéricas sejam tratadas como tal
resumo_df['valor_5anos'] = pd.to_numeric(resumo_df['valor_5anos'], errors='coerce')
precos_df['fechamento_atual'] = pd.to_numeric(precos_df['fechamento_atual'], errors='coerce')

# Padroniza os tickers para garantir a correspondência correta
resumo_df['ticker'] = resumo_df['ticker'].astype(str).str.upper().str.strip()
precos_df['ticker'] = precos_df['ticker'].astype(str).str.upper().str.strip()

# --- Consolidação dos Dados ---
# Junta os dois DataFrames com base no ticker
dados_consolidados = pd.merge(resumo_df, precos_df, on='ticker', how='left')

# --- Cálculo do Preço Teto e da Margem de Segurança ---
print("Calculando o Preço Teto e a margem de segurança...")
# Calcula a média de dividendos dos últimos 5 anos
media_dividendos_5a = dados_consolidados['valor_5anos'] / 5

# Calcula o Preço Teto de Bazin
dados_consolidados['preco_teto_5anos'] = (media_dividendos_5a / RENTABILIDADE_ALVO).round(2)

# Calcula a diferença percentual (margem de segurança)
# ((Preço Teto - Preço Atual) / Preço Atual) * 100
def calcular_diferenca(row):
    if pd.notna(row['preco_teto_5anos']) and pd.notna(row['fechamento_atual']) and row['fechamento_atual'] > 0:
        return round(((row['preco_teto_5anos'] - row['fechamento_atual']) / row['fechamento_atual'] * 100), 2)
    return float('nan')

dados_consolidados['diferenca_percentual'] = dados_consolidados.apply(calcular_diferenca, axis=1)

# --- Finalização e Salvamento ---
# Seleciona as colunas relevantes para o resultado final
resultado_final = dados_consolidados[['ticker', 'preco_teto_5anos', 'diferenca_percentual']]

# Salva o resultado em um arquivo CSV
resultado_final.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n✅ Arquivo 'preco_teto.csv' gerado com sucesso em: {output_path}")
print("\nAmostra dos dados gerados:")
print(resultado_final.head())