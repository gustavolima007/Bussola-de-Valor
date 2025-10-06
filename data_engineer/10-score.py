# -*- coding: utf-8 -*-
"""
>> Script para Geração de Score de Qualidade de Ativos

Este script consolida múltiplos indicadores financeiros para calcular um score
quantitativo que avalia a "qualidade" de cada ativo.
"""

from pathlib import Path
import pandas as pd
from tqdm.auto import tqdm
from common import LAND_DW_DIR, save_to_parquet

# --- Configuração de Caminhos ---
FN_INDICADORES = LAND_DW_DIR / "indicadores.parquet"
FN_DY = LAND_DW_DIR / "dividend_yield.parquet"
FN_PRECO_TETO = LAND_DW_DIR / "preco_teto.parquet"

# --- Funções de Carregamento e Preparação ---
def load_and_prepare_data() -> pd.DataFrame:
    """Carrega, normaliza e junta os arquivos de dados necessários."""
    print("i Carregando e preparando dados...")
    try:
        indicadores = pd.read_parquet(FN_INDICADORES)
        dy = pd.read_parquet(FN_DY)
        preco_teto = pd.read_parquet(FN_PRECO_TETO)
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo não encontrado - {e}. Verifique as execuções anteriores.")
        exit()

    # Junta os DataFrames
    df_merged = pd.merge(indicadores, dy, on='ticker', how='left')
    df_merged = pd.merge(df_merged, preco_teto, on='ticker', how='left')

    # Renomeia colunas para consistência (minúsculas)
    df_merged.rename(columns={'DY12m': 'dy12m', 'DY5anos': 'dy5anos'}, inplace=True)

    num_cols = [
        'p_l', 'p_vp', 'payout_ratio', 'crescimento_preco_5a', 'roe',
        'divida_total', 'market_cap', 'divida_ebitda', 'sentimento_gauge',
        'dy12m', 'dy5anos', 'preco_atual', 'lpa', 'vpa', 'beta', 'current_ratio',
        'liquidez_media_diaria', 'fcf_yield'
    ]
    for col in num_cols:
        if col in df_merged.columns:
            df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')
            
    return df_merged

# --- Funções de Pontuação (Score) ---
def score_dy(dy_12m, dy_5a):
    score = 0
    if pd.notna(dy_12m):
        if dy_12m > 5: score += 60
        elif dy_12m > 3.5: score += 45
        elif dy_12m > 2: score += 30
        elif dy_12m < 2 and dy_12m > 0: score -= 20
    if pd.notna(dy_5a):
        if dy_5a > 10: score += 120
        elif dy_5a > 8: score += 100
        elif dy_5a > 6: score += 80
        elif dy_5a > 4: score += 40
        elif dy_5a < 3 and dy_5a > 1: score -= 20
        elif dy_5a <= 1: score -= 30
    return score

def score_payout(payout):
    if pd.isna(payout): return 0
    if 30 <= payout <= 60: return 30
    if 60 < payout <= 80: return 15
    if (payout > 0 and payout < 20) or payout > 80: return -15
    return 0

def score_roe(roe, setor):
    if pd.isna(roe): return 0
    is_finance = 'finance' in str(setor).lower()
    if is_finance:
        if roe > 15: return 80
        if roe > 12: return 60
        if roe > 8: return 30
    else:
        if roe > 12: return 45
        if roe > 8: return 15
    return 0

def score_pl_pvp(pl, pvp):
    score = 0
    if pd.notna(pl) and pl > 0:
        if pl < 12: score += 45
        elif pl < 18: score += 30
        elif pl > 25: score -= 15
    if pd.notna(pvp) and pvp > 0:
        if pvp < 0.50: score += 135
        elif pvp < 0.66: score += 120
        elif pvp < 1.00: score += 90
        elif pvp < 1.50: score += 45
        elif pvp < 2.50: score += 15
        elif pvp > 4.00: score -= 30
    return score

def score_divida(div_mc, div_ebitda, current_ratio, subsetor):
    if 'finance' in str(subsetor).lower(): return 0
    score = 0
    if pd.notna(div_mc):
        if div_mc < 0.3: score += 45
        elif div_mc < 0.7: score += 30
        elif div_mc > 1.5: score -= 30
    if pd.notna(div_ebitda) and div_ebitda > 0:
        if div_ebitda < 1: score += 45
        elif div_ebitda < 3: score += 15
        elif div_ebitda > 5: score -= 30
    if pd.notna(current_ratio):
        if current_ratio > 2: score += 40
        elif current_ratio > 1: score += 20
        else: score -= 15
    return score

def score_crescimento_sentimento(crescimento, sentimento):
    score = 0
    if pd.notna(crescimento):
        if crescimento > 15: score += 50
        elif crescimento > 10: score += 35
        elif crescimento > 5: score += 20
        elif crescimento < 0: score -= 20
    if pd.notna(sentimento):
        score += (sentimento / 100.0) * 60 - 20
    return score

def score_ciclo_mercado(status_ciclo):
    if pd.isna(status_ciclo): return 0
    if status_ciclo == 'Compra': return 70
    if status_ciclo == 'Venda': return -70
    return 0

def score_graham(preco_atual, lpa, vpa):
    if pd.isna(preco_atual) or pd.isna(lpa) or pd.isna(vpa) or lpa <= 0 or vpa <= 0 or preco_atual <= 0:
        return 0
    try:
        numero_graham = (22.5 * lpa * vpa) ** 0.5
        margem_seguranca = (numero_graham / preco_atual) - 1
    except (ValueError, TypeError):
        return 0
    if margem_seguranca > 2.0: return 150
    if margem_seguranca > 1.5: return 130
    if margem_seguranca > 1.0: return 110
    if margem_seguranca > 0.5: return 70
    if margem_seguranca > 0.2: return 35
    if margem_seguranca > 0: return 20
    return -70

def score_beta(beta):
    if pd.isna(beta): return 0
    if beta < 1.0: return 35
    if beta > 1.5: return -35
    return 0

def score_market_cap(market_cap):
    if pd.isna(market_cap): return 0
    if market_cap > 50_000_000_000: return 35
    if market_cap > 10_000_000_000: return 25
    if market_cap > 2_000_000_000:  return 15
    return 0

def score_liquidez(liquidez):
    if pd.isna(liquidez): return 0
    if liquidez > 50_000_000: return 35
    if liquidez > 20_000_000: return 25
    if liquidez > 5_000_000:  return 15
    return 0

def score_fcf_yield(fcf_yield):
    if pd.isna(fcf_yield): return 0
    if fcf_yield > 8: return 35
    if fcf_yield > 5: return 20
    return 0

# --- Função Principal de Execução ---
def main():
    """Orquestra a execução do script: carrega, processa e salva os scores."""
    df = load_and_prepare_data()

    scores_data = []
    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Calculando Scores"):
        setor = row.get('subsetor_b3', 'N/A')
        div_mc = row['divida_total'] / row['market_cap'] if pd.notna(row['market_cap']) and row['market_cap'] > 0 else None

        s_dy = score_dy(row.get('dy12m'), row.get('dy5anos'))
        s_payout = score_payout(row.get('payout_ratio'))
        s_roe = score_roe(row.get('roe'), setor)
        s_pl_pvp = score_pl_pvp(row.get('p_l'), row.get('p_vp'))
        s_divida = score_divida(div_mc, row.get('divida_ebitda'), row.get('current_ratio'), setor)
        s_cresc_sent = score_crescimento_sentimento(row.get('crescimento_preco_5a'), row.get('sentimento_gauge'))
        s_ciclo = score_ciclo_mercado(row.get('status_ciclo'))
        s_graham = score_graham(row.get('preco_atual'), row.get('lpa'), row.get('vpa'))
        s_beta = score_beta(row.get('beta'))
        s_mcap = score_market_cap(row.get('market_cap'))
        s_liquidez = score_liquidez(row.get('liquidez_media_diaria'))
        s_fcf = score_fcf_yield(row.get('fcf_yield'))
        
        score_total = s_dy + s_payout + s_roe + s_pl_pvp + s_divida + s_cresc_sent + s_ciclo + s_graham + s_beta + s_mcap + s_liquidez + s_fcf
        
        scores_data.append({
            'ticker': row['ticker'],
            'score_dy': s_dy,
            'score_payout': s_payout,
            'score_roe': s_roe,
            'score_pl_pvp': s_pl_pvp,
            'score_divida': s_divida,
            'score_crescimento_sentimento': s_cresc_sent,
            'score_ciclo_mercado': s_ciclo,
            'score_graham': s_graham,
            'score_beta': s_beta,
            'score_market_cap': s_mcap,
            'score_liquidez': s_liquidez,
            'score_fcf_yield': s_fcf,
            'score_total': max(0, score_total)
        })

    scores_df = pd.DataFrame(scores_data).round(2)
    scores_df = scores_df.sort_values(by='score_total', ascending=False)
    
    save_to_parquet(scores_df, "scores")
    
    print(f"\nCálculo de scores concluído.")

if __name__ == '__main__':
    main()