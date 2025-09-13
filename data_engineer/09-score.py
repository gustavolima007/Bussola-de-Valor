# -*- coding: utf-8 -*-
"""
🏆 Script para Geração de Score de Qualidade de Ativos

Este script consolida múltiplos indicadores financeiros para calcular um score
quantitativo que avalia a "qualidade" de cada ativo. O objetivo é fornecer
uma métrica única que ajude a comparar diferentes ações e fundos.

Etapas do Processo:
1.  Carrega os dados de três fontes: indicadores, dividend yield e preço teto.
2.  Normaliza e junta os dados em um único DataFrame.
3.  Aplica uma série de funções de pontuação para cada indicador relevante:
    - Dividend Yield (12 meses e 5 anos)
    - Payout Ratio
    - ROE (com diferenciação por setor)
    - P/L e P/VP
    - Níveis de endividamento (Dívida/Market Cap e Dívida/EBITDA)
    - Crescimento do preço
    - Sentimento do mercado
4.  Soma as pontuações individuais para gerar um `score_total`.
5.  Salva o resultado, incluindo os scores parciais e o total, em 'data/scores.csv'.
"""

from pathlib import Path
import pandas as pd
from tqdm.auto import tqdm

# --- Configuração de Caminhos ---
BASE = Path(__file__).resolve().parent.parent / "data"
FN_INDICADORES = BASE / "indicadores.csv"
FN_DY = BASE / "dividend_yield.csv"
FN_PRECO_TETO = BASE / "preco_teto.csv"
FN_OUT = BASE / "scores.csv"

# --- Funções de Carregamento e Preparação ---
def load_and_prepare_data() -> pd.DataFrame:
    """Carrega, normaliza e junta os arquivos de dados necessários."""
    print("Carregando e preparando os dados...")
    indicadores = pd.read_csv(FN_INDICADORES)
    dy = pd.read_csv(FN_DY)
    preco_teto = pd.read_csv(FN_PRECO_TETO)

    # Normaliza os tickers para a junção
    for df in [indicadores, dy, preco_teto]:
        df['ticker_base'] = df['ticker'].str.strip().str.upper()

    # Junta os DataFrames
    df_merged = pd.merge(indicadores, dy, on='ticker_base', how='left', suffixes=('', '_dy'))
    df_merged = pd.merge(df_merged, preco_teto, on='ticker_base', how='left', suffixes=('', '_teto'))

    # Converte colunas para numérico, tratando erros
    num_cols = [
        'p_l', 'p_vp', 'payout_ratio', 'crescimento_preco_5a', 'roe',
        'divida_total', 'market_cap', 'divida_ebitda', 'sentimento_gauge',
        'DY12M', 'DY5anos'
    ]
    for col in num_cols:
        if col in df_merged.columns:
            df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')
            
    return df_merged.drop(columns=['ticker_dy', 'ticker_teto'], errors='ignore')

# --- Funções de Pontuação (Score) ---
# Cada função atribui pontos com base em critérios predefinidos para um indicador.

def score_dy(dy_12m, dy_5a):
    """Pontuação baseada no Dividend Yield."""
    score = 0
    if pd.notna(dy_12m):
        if dy_12m > 5: score += 20
        elif dy_12m > 3.5: score += 15
        elif dy_12m > 2: score += 10
        elif dy_12m < 2 and dy_12m > 0: score -= 5
    if pd.notna(dy_5a):
        if dy_5a > 8: score += 25
        elif dy_5a > 6: score += 20
        elif dy_5a > 4: score += 10
    return score

def score_payout(payout):
    """Pontuação para o Payout Ratio."""
    if pd.isna(payout): return 0
    if 30 <= payout <= 60: return 10
    if 60 < payout <= 80: return 5
    if (payout > 0 and payout < 20) or payout > 80: return -5
    return 0

def score_roe(roe, setor):
    """Pontuação para o ROE, com lógica diferente para o setor financeiro."""
    if pd.isna(roe): return 0
    is_finance = 'finance' in str(setor).lower()
    if is_finance:
        if roe > 15: return 25
        if roe > 12: return 20
        if roe > 8: return 10
    else:
        if roe > 12: return 15
        if roe > 8: return 5
    return 0

def score_pl_pvp(pl, pvp):
    """Pontuação combinada para P/L e P/VP."""
    score = 0
    if pd.notna(pl) and pl > 0:
        if pl < 12: score += 15
        elif pl < 18: score += 10
        elif pl > 25: score -= 5
    if pd.notna(pvp) and pvp > 0:
        if pvp < 0.66: score += 20
        elif pvp < 1.5: score += 10
        elif pvp < 2.5: score += 5
        elif pvp > 4: score -= 5
    return score

def score_divida(div_mc, div_ebitda, subsetor):
    """Pontuação para os indicadores de endividamento."""
    if 'finance' in str(subsetor).lower(): return 0
    score = 0
    if pd.notna(div_mc):
        if div_mc < 0.5: score += 10
        elif div_mc < 1.0: score += 5
        elif div_mc > 2.0: score -= 5
    if pd.notna(div_ebitda) and div_ebitda > 0:
        if div_ebitda < 1: score += 10
        elif div_ebitda < 2: score += 5
        elif div_ebitda > 6: score -= 5
    return score

def score_crescimento_sentimento(crescimento, sentimento):
    """Pontuação para crescimento de preço e sentimento de mercado."""
    score = 0
    if pd.notna(crescimento):
        if crescimento > 15: score += 15
        elif crescimento > 10: score += 10
        elif crescimento > 5: score += 5
        elif crescimento < 0: score -= 5
    if pd.notna(sentimento):
        score += ((sentimento - 50) / 50.0) * (10 if sentimento >= 50 else 5)
    return score

# --- Função Principal de Execução ---
def main():
    """Orquestra a execução do script: carrega, processa e salva os scores."""
    df = load_and_prepare_data()

    # Aplica as funções de score
    tqdm.pandas(desc="Calculando Scores")
    
    scores_data = []
    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Calculando Scores"):
        setor = row.get('setor_brapi', 'N/A')
        div_mc = row['divida_total'] / row['market_cap'] if pd.notna(row['market_cap']) and row['market_cap'] > 0 else None

        s_dy = score_dy(row.get('DY12M'), row.get('DY5anos'))
        s_payout = score_payout(row.get('payout_ratio'))
        s_roe = score_roe(row.get('roe'), setor)
        s_pl_pvp = score_pl_pvp(row.get('p_l'), row.get('p_vp'))
        s_divida = score_divida(div_mc, row.get('divida_ebitda'), setor)
        s_cresc_sent = score_crescimento_sentimento(row.get('crescimento_preco_5a'), row.get('sentimento_gauge'))
        
        score_total = s_dy + s_payout + s_roe + s_pl_pvp + s_divida + s_cresc_sent
        
        scores_data.append({
            'ticker_base': row['ticker_base'],
            'score_dy': s_dy,
            'score_payout': s_payout,
            'score_roe': s_roe,
            'score_pl_pvp': s_pl_pvp,
            'score_divida': s_divida,
            'score_crescimento_sentimento': s_cresc_sent,
            'score_total': max(0, min(200, score_total)) # Clamping entre 0 e 200
        })

    scores_df = pd.DataFrame(scores_data).round(2)
    
    # Ordena pelo score total e salva
    scores_df = scores_df.sort_values(by='score_total', ascending=False)
    scores_df.to_csv(FN_OUT, index=False, float_format='%.2f')
    
    print(f"\n✅ Arquivo de scores salvo com sucesso em: {FN_OUT}")

if __name__ == '__main__':
    main()
