# -*- coding: utf-8 -*-
"""
📊 Avaliação de desempenho por Setor e Subsetor (padrão B3)
"""

from pathlib import Path
import pandas as pd
import numpy as np

from common import LAND_DW_DIR, save_to_parquet

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
    indicadores_path = LAND_DW_DIR / "indicadores.parquet"
    dy_path = LAND_DW_DIR / "dividend_yield.parquet"
    scores_path = LAND_DW_DIR / "scores.parquet"
    rj_path = LAND_DW_DIR / "rj.parquet"
    acoes_path = LAND_DW_DIR / "acoes_e_fundos.parquet"

    print("📊 Iniciando avaliação de setores...")
    try:
        indicadores_df = pd.read_parquet(indicadores_path)
        dy_df = pd.read_parquet(dy_path)
        scores_df = pd.read_parquet(scores_path)
        rj_df = pd.read_parquet(rj_path)
        acoes_df = pd.read_parquet(acoes_path)
    except FileNotFoundError as e:
        print(f"❌ Erro: Arquivo não encontrado - {e}. Verifique as execuções anteriores. Abortando.")
        return

    # --- Preparação e Merge ---
    indicadores_df = indicadores_df.drop(columns=['setor_b3', 'subsetor_b3'], errors='ignore')
    merged_df = pd.merge(indicadores_df, acoes_df[['ticker', 'setor_b3', 'subsetor_b3']].drop_duplicates(), on="ticker", how="left")
    dy_df.rename(columns={'DY5anos': 'dy5anos'}, inplace=True)
    merged_df = pd.merge(merged_df, dy_df[['ticker', 'dy5anos']], on="ticker", how="left")
    merged_df = pd.merge(merged_df, scores_df[['ticker', 'score_total']], on="ticker", how="left")
    
    merged_df = merged_df.dropna(subset=['setor_b3', 'subsetor_b3'])
    numeric_cols = ['roe', 'beta', 'payout_ratio', 'margem_seguranca_percent', 'dy5anos', 'score_total']
    for col in numeric_cols:
        merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')
    merged_df = merged_df.fillna(0)

    # --- Agregação por Subsetor ---
    subsetor_stats = merged_df.groupby('subsetor_b3').agg(
        roe_medio=('roe', 'mean'),
        beta_medio=('beta', 'mean'),
        payout_medio=('payout_ratio', 'mean'),
        dy_5a_medio=('dy5anos', 'mean'),
        margem_graham_media=('margem_seguranca_percent', 'mean'),
        score_original=('score_total', 'mean')
    ).reset_index()

    boas = merged_df[merged_df['score_total'] > 300].groupby('subsetor_b3').size().reset_index(name='empresas_boas_contagem')
    subsetor_stats = pd.merge(subsetor_stats, boas, on='subsetor_b3', how='left')

    ruins = merged_df[merged_df['score_total'] < 100].groupby('subsetor_b3').size().reset_index(name='empresas_ruins_contagem')
    subsetor_stats = pd.merge(subsetor_stats, ruins, on='subsetor_b3', how='left')

    rj_df['setor'] = rj_df['setor'].str.strip()
    rj_counts = rj_df[rj_df['data_saida_rj'].isnull()].groupby('setor').size().reset_index(name='ocorrencias_rj')
    subsetor_stats = pd.merge(subsetor_stats, rj_counts, left_on='subsetor_b3', right_on='setor', how='left').drop(columns='setor')
    
    subsetor_stats = subsetor_stats.fillna(0)

    # --- Cálculo das Pontuações por Critério ---
    score_original_scaled = subsetor_stats['score_original']
    subsetor_stats['score_dy'] = subsetor_stats['dy_5a_medio'].apply(calcular_score_dy)
    subsetor_stats['score_roe'] = subsetor_stats['roe_medio'].apply(calcular_score_roe)
    subsetor_stats['score_beta'] = subsetor_stats['beta_medio'].apply(calcular_score_beta)
    subsetor_stats['score_payout'] = subsetor_stats['payout_medio'].apply(calcular_score_payout)
    subsetor_stats['score_empresas_boas'] = subsetor_stats['empresas_boas_contagem'].apply(calcular_score_empresas_boas)
    subsetor_stats['penalidade_empresas_ruins'] = subsetor_stats['empresas_ruins_contagem'].apply(calcular_penalidade_empresas_ruins)
    subsetor_stats['score_graham'] = subsetor_stats['margem_graham_media'].apply(calcular_score_graham)

    max_ocorrencias = subsetor_stats['ocorrencias_rj'].max()
    if max_ocorrencias > 0:
        subsetor_stats['penalidade_rj'] = -(subsetor_stats['ocorrencias_rj'] / max_ocorrencias * 80)
    else:
        subsetor_stats['penalidade_rj'] = 0

    # --- Pontuação Final ---
    positive_score_cols = ['score_dy', 'score_roe', 'score_beta', 'score_payout', 'score_empresas_boas', 'score_graham']
    subsetor_stats['pontuacao_positiva'] = subsetor_stats[positive_score_cols].sum(axis=1) + score_original_scaled

    penalty_cols = ['penalidade_empresas_ruins', 'penalidade_rj']
    subsetor_stats['pontuacao_final'] = subsetor_stats['pontuacao_positiva'] + subsetor_stats[penalty_cols].sum(axis=1)

    # --- Agregação para o Setor Principal ---
    setor_mapping = acoes_df[['setor_b3', 'subsetor_b3']].drop_duplicates()
    resultado_final = pd.merge(subsetor_stats, setor_mapping, on='subsetor_b3', how='left')
    
    pontuacao_setor_media = resultado_final.groupby('setor_b3')['pontuacao_final'].mean().reset_index()
    pontuacao_setor_media = pontuacao_setor_media.rename(columns={'pontuacao_final': 'pontuacao_setor'})
    
    resultado_final = pd.merge(resultado_final, pontuacao_setor_media, on='setor_b3', how='left')

    # --- Finalização e Salvamento ---
    colunas_finais = [
        'setor_b3', 'pontuacao_setor', 'subsetor_b3', 'pontuacao_final',
        'score_dy', 'score_roe', 'score_beta', 'score_payout',
        'score_empresas_boas', 'penalidade_empresas_ruins', 'score_graham', 'penalidade_rj',
        'dy_5a_medio', 'roe_medio', 'beta_medio', 'payout_medio', 'margem_graham_media', 'score_original',
        'empresas_boas_contagem', 'empresas_ruins_contagem', 'ocorrencias_rj'
    ]
    resultado_final = resultado_final[colunas_finais]
    resultado_final = resultado_final.sort_values(by=['pontuacao_setor', 'pontuacao_final'], ascending=[False, False])
    
    for col in resultado_final.columns:
        if pd.api.types.is_numeric_dtype(resultado_final[col]):
            resultado_final[col] = resultado_final[col].round(2)

    save_to_parquet(resultado_final, "avaliacao_setor")
    print(f"✅ Avaliação de setores concluída.")


if __name__ == "__main__":
    main()