# -*- coding: utf-8 -*-
"""
Avaliação de desempenho por Setor e Subsetor (padrão B3)
"""

from pathlib import Path
import pandas as pd
import numpy as np

from common import DATA_DIR

# --- Funções de Cálculo de Score por Critério ---

def calcular_score_dy(dy_5a_medio):
    if dy_5a_medio >= 10: return 150
    if 8 <= dy_5a_medio < 10: return 120
    if 6 <= dy_5a_medio < 8: return 90
    if 4 <= dy_5a_medio < 6: return 60
    if 2 <= dy_5a_medio < 4: return -30
    if dy_5a_medio < 2: return -60
    if dy_5a_medio < 1: return -90
    return 0

def calcular_score_roe(roe_medio):
    if roe_medio > 25: return 75
    if 20 <= roe_medio <= 25: return 55
    if 15 <= roe_medio < 20: return 35
    if 10 <= roe_medio < 15: return 20
    return 0

def calcular_score_beta(beta_medio):
    if beta_medio < 0.8: return 35
    if 0.8 <= beta_medio <= 1.2: return 20
    if beta_medio > 1.5: return -20
    return 0

def calcular_score_payout(payout_medio):
    if 30 <= payout_medio <= 60: return 35
    if (20 <= payout_medio < 30) or (60 < payout_medio <= 80): return 20
    return 0

def calcular_score_empresas_boas(contagem):
    if contagem >= 8: return 75
    if 6 <= contagem < 8: return 55
    if 3 <= contagem <= 5: return 35
    if 1 <= contagem <= 2: return 20
    return 0

def calcular_penalidade_empresas_ruins(contagem):
    if contagem >= 6: return -60
    if 3 <= contagem <= 5: return -40
    if 1 <= contagem <= 2: return -20
    return 0

def calcular_score_graham(margem_media):
    if margem_media > 150: return 55
    if 100 <= margem_media <= 150: return 35
    if 50 <= margem_media < 100: return 20
    return 0

def main() -> None:
    # --- Paths ---
    indicadores_path = DATA_DIR / "indicadores.csv"
    dy_path = DATA_DIR / "dividend_yield.csv"
    scores_path = DATA_DIR / "scores.csv"
    rj_path = DATA_DIR / "rj.csv"
    acoes_path = DATA_DIR / "acoes_e_fundos.csv"
    output_path = DATA_DIR / "avaliacao_setor.csv"

    print("Iniciando avaliação de setores...")
    try:
        indicadores_df = pd.read_csv(indicadores_path)
        dy_df = pd.read_csv(dy_path)
        scores_df = pd.read_csv(scores_path)
        rj_df = pd.read_csv(rj_path)
        acoes_df = pd.read_csv(acoes_path)
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}. Abortando.")
        return


    # --- Preparação e Merge ---
    # Normaliza tickers
    for df in [indicadores_df, dy_df, scores_df, acoes_df]:
        if 'ticker' in df.columns:
            df["ticker_base"] = df["ticker"].astype(str).str.upper().str.strip()
        elif 'ticker_base' in df.columns:
             df["ticker_base"] = df["ticker_base"].astype(str).str.upper().str.strip()


    # Merge principal
    indicadores_df = indicadores_df.drop(columns=['setor_b3', 'subsetor_b3'], errors='ignore')
    merged_df = pd.merge(
        indicadores_df,
        acoes_df[['ticker_base', 'setor_b3', 'subsetor_b3']].drop_duplicates(),
        on="ticker_base",
        how="left"
    )
    merged_df = pd.merge(
        merged_df,
        dy_df[['ticker_base', 'DY5anos']],
        on="ticker_base",
        how="left"
    )
    merged_df = pd.merge(
        merged_df,
        scores_df[['ticker_base', 'score_total']],
        on="ticker_base",
        how="left"
    )
    
    # Limpa e converte tipos
    merged_df = merged_df.dropna(subset=[col for col in ['setor_b3', 'subsetor_b3'] if col in merged_df.columns])
    numeric_cols = ['roe', 'beta', 'payout_ratio', 'margem_seguranca_percent', 'DY5anos', 'score_total']
    for col in numeric_cols:
        merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')
    merged_df = merged_df.fillna(0)


    # --- Agregação por Subsetor ---
    subsetor_stats = merged_df.groupby('subsetor_b3').agg(
        roe_medio=('roe', 'mean'),
        beta_medio=('beta', 'mean'),
        payout_medio=('payout_ratio', 'mean'),
        dy_5a_medio=('DY5anos', 'mean'),
        margem_graham_media=('margem_seguranca_percent', 'mean'),
        score_original=('score_total', 'mean')
    ).reset_index()

    # Contagem de empresas com score > 300
    boas = merged_df[merged_df['score_total'] > 300].groupby('subsetor_b3').size().reset_index(name='empresas_boas_contagem')
    subsetor_stats = pd.merge(subsetor_stats, boas, on='subsetor_b3', how='left')

    # Contagem de empresas com score < 100
    ruins = merged_df[merged_df['score_total'] < 100].groupby('subsetor_b3').size().reset_index(name='empresas_ruins_contagem')
    subsetor_stats = pd.merge(subsetor_stats, ruins, on='subsetor_b3', how='left')

    # Contagem de empresas em RJ
    rj_df['setor'] = rj_df['setor'].str.strip()
    rj_counts = rj_df[rj_df['data_saida_rj'].isnull()].groupby('setor').size().reset_index(name='ocorrencias_rj')
    subsetor_stats = pd.merge(subsetor_stats, rj_counts, left_on='subsetor_b3', right_on='setor', how='left').drop(columns='setor')
    
    subsetor_stats = subsetor_stats.fillna(0)

    # --- Cálculo das Pontuações por Critério ---
    subsetor_stats['score_original'] = (subsetor_stats['score_original'] / 1000) * 550 # Ajusta o score original para o peso de 55%
    subsetor_stats['score_dy'] = subsetor_stats['dy_5a_medio'].apply(calcular_score_dy)
    subsetor_stats['score_roe'] = subsetor_stats['roe_medio'].apply(calcular_score_roe)
    subsetor_stats['score_beta'] = subsetor_stats['beta_medio'].apply(calcular_score_beta)
    subsetor_stats['score_payout'] = subsetor_stats['payout_medio'].apply(calcular_score_payout)
    subsetor_stats['score_empresas_boas'] = subsetor_stats['empresas_boas_contagem'].apply(calcular_score_empresas_boas)
    subsetor_stats['penalidade_empresas_ruins'] = subsetor_stats['empresas_ruins_contagem'].apply(calcular_penalidade_empresas_ruins)
    subsetor_stats['score_graham'] = subsetor_stats['margem_graham_media'].apply(calcular_score_graham)

    # Cálculo da Penalidade de RJ (normalizada)
    max_ocorrencias = subsetor_stats['ocorrencias_rj'].max()
    if max_ocorrencias > 0:
        subsetor_stats['penalidade_rj'] = -(subsetor_stats['ocorrencias_rj'] / max_ocorrencias * 80)
    else:
        subsetor_stats['penalidade_rj'] = 0

    # --- Pontuação Final ---
    positive_score_cols = [
        'score_original', 'score_dy', 'score_roe', 'score_beta', 'score_payout', 
        'score_empresas_boas', 'score_graham'
    ]
    subsetor_stats['pontuacao_positiva'] = subsetor_stats[positive_score_cols].sum(axis=1)
    subsetor_stats['pontuacao_positiva'] = subsetor_stats['pontuacao_positiva'].apply(lambda x: min(x, 1000))

    penalty_cols = ['penalidade_empresas_ruins', 'penalidade_rj']
    subsetor_stats['pontuacao_final'] = subsetor_stats['pontuacao_positiva'] + subsetor_stats[penalty_cols].sum(axis=1)

    # --- Agregação para o Setor Principal ---
    # Garante que cada subsetor está mapeado para um setor_b3
    setor_mapping = acoes_df[['setor_b3', 'subsetor_b3']].drop_duplicates()
    resultado_final = pd.merge(subsetor_stats, setor_mapping, on='subsetor_b3', how='left')
    
    # Calcula a pontuação média do setor
    pontuacao_setor_media = resultado_final.groupby('setor_b3')['pontuacao_final'].mean().reset_index()
    pontuacao_setor_media = pontuacao_setor_media.rename(columns={'pontuacao_final': 'pontuacao_setor'})
    
    resultado_final = pd.merge(resultado_final, pontuacao_setor_media, on='setor_b3', how='left')

    # --- Finalização e Salvamento ---
    # Ordena e seleciona colunas
    colunas_finais = [
        'setor_b3', 'pontuacao_setor', 'subsetor_b3', 'pontuacao_final',
        'score_dy', 'score_roe', 'score_beta', 'score_payout',
        'score_empresas_boas', 'penalidade_empresas_ruins', 'score_graham', 'penalidade_rj',
        'dy_5a_medio', 'roe_medio', 'beta_medio', 'payout_medio', 'margem_graham_media', 'score_original',
        'empresas_boas_contagem', 'empresas_ruins_contagem', 'ocorrencias_rj'
    ]
    resultado_final = resultado_final[colunas_finais]
    resultado_final = resultado_final.sort_values(by=['pontuacao_setor', 'pontuacao_final'], ascending=[False, False])
    
    # Arredonda valores para melhor visualização
    for col in resultado_final.columns:
        if pd.api.types.is_numeric_dtype(resultado_final[col]):
            resultado_final[col] = resultado_final[col].round(2)

    resultado_final.to_csv(output_path, index=False, float_format="%.2f")
    print(f"OK. Novo arquivo de avaliação de setores salvo em: {output_path}")


if __name__ == "__main__":
    main()