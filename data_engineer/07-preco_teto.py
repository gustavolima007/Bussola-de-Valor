# -*- coding: utf-8 -*-
"""
🎯 Script para Cálculo do Preço Teto (Método de Bazin)

Este script calcula o "Preço Teto" de ações com base na metodologia de
Décio Bazin, que utiliza a média dos dividendos dos últimos 5 anos e uma
rentabilidade mínima desejada (6%).

Etapas do Processo:
1.  Define a rentabilidade alvo (6%).
2.  Lê os arquivos Parquet com o resumo de dividendos e os preços atuais.
3.  Junta as informações de dividendos e preços.
4.  Calcula o Preço Teto: (Média dos dividendos dos últimos 5 anos) / 0.06.
5.  Calcula a margem de segurança (diferença percentual).
6.  Salva o resultado em formato Parquet.
"""

import pandas as pd
from pathlib import Path

# Importa as utilidades comuns do pipeline
from common import LAND_DW_DIR, save_to_parquet

# --- Configurações ---
RENTABILIDADE_ALVO = 0.06

# --- Configuração de Caminhos ---
resumo_dividendos_path = LAND_DW_DIR / "dividendos_ano_resumo.parquet"
precos_path = LAND_DW_DIR / "precos_acoes.parquet"

# --- Leitura dos Dados ---
print(f"Lendo dividendos: {resumo_dividendos_path.name}")
try:
    resumo_df = pd.read_parquet(resumo_dividendos_path)
except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado: '{resumo_dividendos_path}'.")
    print("Execute '04-dividendos_ano_resumo.py' antes de continuar.")
    exit()

print(f"Lendo preços: {precos_path.name}")
try:
    precos_df = pd.read_parquet(precos_path)
except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado: '{precos_path}'.")
    print("Execute '05-preco_acoes.py' antes de continuar.")
    exit()

# --- Preparação dos Dados ---
print("Preparando dados...")
resumo_df['valor_5anos'] = pd.to_numeric(resumo_df['valor_5anos'], errors='coerce')
precos_df['fechamento_atual'] = pd.to_numeric(precos_df['fechamento_atual'], errors='coerce')

# --- Consolidação dos Dados ---
dados_consolidados = pd.merge(resumo_df, precos_df, on='ticker', how='left')

# --- Cálculo do Preço Teto e da Margem de Segurança ---
print("Calculando Preço Teto e margem de segurança...")
media_dividendos_5a = dados_consolidados['valor_5anos'] / 5
dados_consolidados['preco_teto_5anos'] = (media_dividendos_5a / RENTABILIDADE_ALVO).round(2)

def calcular_diferenca(row):
    if pd.notna(row['preco_teto_5anos']) and pd.notna(row['fechamento_atual']) and row['fechamento_atual'] > 0:
        return round(((row['preco_teto_5anos'] - row['fechamento_atual']) / row['fechamento_atual'] * 100), 2)
    return None

dados_consolidados['diferenca_percentual'] = dados_consolidados.apply(calcular_diferenca, axis=1)

# --- Finalização e Salvamento ---
resultado_final = dados_consolidados[['ticker', 'preco_teto_5anos', 'diferenca_percentual']]

save_to_parquet(resultado_final, 'preco_teto')

print("Cálculo de Preço Teto concluído.")
