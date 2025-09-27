# -*- coding: utf-8 -*-
"""
Script para Geração de Score de Qualidade de Ativos

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
FN_CICLO_MERCADO = BASE / "ciclo_mercado.csv"
FN_OUT = BASE / "scores.csv"

# --- Funções de Carregamento e Preparação ---
def load_and_prepare_data() -> pd.DataFrame:
    """Carrega, normaliza e junta os arquivos de dados necessários."""
    print("Carregando e preparando os dados...")
    indicadores = pd.read_csv(FN_INDICADORES)
    dy = pd.read_csv(FN_DY)
    preco_teto = pd.read_csv(FN_PRECO_TETO)
    ciclo_mercado = pd.read_csv(FN_CICLO_MERCADO)

    # Normaliza os tickers para a junção
    for df in [indicadores, dy, preco_teto, ciclo_mercado]:
        df['ticker_base'] = df['ticker'].str.strip().str.upper()

    # Junta os DataFrames
    df_merged = pd.merge(indicadores, dy, on='ticker_base', how='left', suffixes=('', '_dy'))
    df_merged = pd.merge(df_merged, preco_teto, on='ticker_base', how='left', suffixes=('', '_teto'))
    df_merged = pd.merge(df_merged, ciclo_mercado, on='ticker_base', how='left', suffixes=('', '_ciclo'))

    # Converte colunas para numérico, tratando erros
    num_cols = [
        'p_l', 'p_vp', 'payout_ratio', 'crescimento_preco_5a', 'roe',
        'divida_total', 'market_cap', 'divida_ebitda', 'sentimento_gauge',
        'DY12M', 'DY5anos', 'preco_atual', 'lpa', 'vpa', 'beta', 'current_ratio',
        'liquidez_media_diaria', 'fcf_yield'
    ]
    for col in num_cols:
        if col in df_merged.columns:
            df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')
            
    return df_merged.drop(columns=['ticker_dy', 'ticker_teto', 'ticker_ciclo'], errors='ignore')

# --- Funções de Pontuação (Score) ---
# Cada função atribui pontos com base em critérios predefinidos para um indicador.

def score_dy(dy_12m, dy_5a):
    """Pontuação baseada no Dividend Yield."""
    score = 0
    # DY 12 meses: >5% (+60 pts), 3.5%-5% (+45 pts), 2%-3.5% (+30 pts), <2% (-20 pts)
    if pd.notna(dy_12m):
        if dy_12m > 5: score += 60
        elif dy_12m > 3.5: score += 45
        elif dy_12m > 2: score += 30
        elif dy_12m < 2 and dy_12m > 0: score -= 20
    # DY média 5 anos: >10% (+120 pts), 8%-10% (+100 pts), 6%-8% (+80 pts), 4%-6% (+40 pts), <3% (-20 pts), <1% (-30 pts)
    if pd.notna(dy_5a):
        if dy_5a > 10: score += 120
        elif dy_5a > 8: score += 100
        elif dy_5a > 6: score += 80
        elif dy_5a > 4: score += 40
        elif dy_5a < 3 and dy_5a > 1: score -= 20
        elif dy_5a <= 1: score -= 30
    return score

def score_payout(payout):
    """Pontuação para o Payout Ratio."""
    # Payout: 30%-60% (+30 pts), 60%-80% (+15 pts), <20% ou >80% (-15 pts)
    if pd.isna(payout): return 0
    if 30 <= payout <= 60: return 30
    if 60 < payout <= 80: return 15
    if (payout > 0 and payout < 20) or payout > 80: return -15
    return 0

def score_roe(roe, setor):
    """Pontuação para o ROE, com lógica diferente para o setor financeiro."""
    if pd.isna(roe): return 0
    is_finance = 'finance' in str(setor).lower()
    # ROE (Setor Financeiro): >15% (+80 pts), 12%-15% (+60 pts), 8%-12% (+30 pts)
    if is_finance:
        if roe > 15: return 80
        if roe > 12: return 60
        if roe > 8: return 30
    # ROE (Outros Setores): >12% (+45 pts), 8%-12% (+15 pts)
    else:
        if roe > 12: return 45
        if roe > 8: return 15
    return 0

def score_pl_pvp(pl, pvp):
    """Pontuação combinada para P/L e P/VP."""
    score = 0
    # P/L: <12 (+45 pts), 12-18 (+30 pts), >25 (-15 pts)
    if pd.notna(pl) and pl > 0:
        if pl < 12: score += 45
        elif pl < 18: score += 30
        elif pl > 25: score -= 15
    # P/VP: <0.50 (+135 pts), 0.50-0.66 (+120 pts), 0.66-1.00 (+90 pts), 1.00-1.50 (+45 pts), 1.50-2.50 (+15 pts), >4.00 (-30 pts)
    if pd.notna(pvp) and pvp > 0:
        if pvp < 0.50: score += 135
        elif pvp < 0.66: score += 120
        elif pvp < 1.00: score += 90
        elif pvp < 1.50: score += 45
        elif pvp < 2.50: score += 15
        elif pvp > 4.00: score -= 30
    return score

def score_divida(div_mc, div_ebitda, current_ratio, subsetor):
    """Pontuação para os indicadores de endividamento."""
    if 'finance' in str(subsetor).lower(): return 0
    score = 0
    # Dívida/Market Cap: <0.3 (+45 pts), 0.3-0.7 (+30 pts), >1.5 (-30 pts)
    if pd.notna(div_mc):
        if div_mc < 0.3: score += 45
        elif div_mc < 0.7: score += 30
        elif div_mc > 1.5: score -= 30
    # Dívida/EBITDA: <1 (+45 pts), 1-3 (+15 pts), >5 (-30 pts)
    if pd.notna(div_ebitda) and div_ebitda > 0:
        if div_ebitda < 1: score += 45
        elif div_ebitda < 3: score += 15
        elif div_ebitda > 5: score -= 30
    # Current Ratio: >2 (+40 pts), 1-2 (+20 pts), <1 (-15 pts)
    if pd.notna(current_ratio):
        if current_ratio > 2: score += 40
        elif current_ratio > 1: score += 20
        else: score -= 15
    return score

def score_crescimento_sentimento(crescimento, sentimento):
    """Pontuação para crescimento de preço e sentimento de mercado."""
    score = 0
    # Crescimento Preço 5 Anos: >15% (+50 pts), 10%-15% (+35 pts), 5%-10% (+20 pts), <0% (-20 pts)
    if pd.notna(crescimento):
        if crescimento > 15: score += 50
        elif crescimento > 10: score += 35
        elif crescimento > 5: score += 20
        elif crescimento < 0: score -= 20
    # Sentimento do Mercado: -20 a +40 pts (proporcional)
    if pd.notna(sentimento):
        # Mapeia o sentimento (0-100) para o intervalo de pontos (-20 a +40)
        score += (sentimento / 100.0) * 60 - 20
    return score

def score_ciclo_mercado(status_ciclo):
    """Pontuação baseada no status do ciclo de mercado."""
    if pd.isna(status_ciclo): return 0
    # Compra (Pânico / Medo Extremo): +70 pontos
    if status_ciclo == 'Compra': return 70
    # Venda (Euforia / Ganância Extrema): -70 pontos
    if status_ciclo == 'Venda': return -70
    return 0

def score_graham(preco_atual, lpa, vpa):
    """Pontuação baseada na Margem de Segurança da Fórmula de Graham."""
    if pd.isna(preco_atual) or pd.isna(lpa) or pd.isna(vpa) or lpa <= 0 or vpa <= 0 or preco_atual <= 0:
        return 0

    try:
        numero_graham = (22.5 * lpa * vpa) ** 0.5
        margem_seguranca = (numero_graham / preco_atual) - 1
    except (ValueError, TypeError):
        return 0

    # Margem > 200%: +150 pontos
    if margem_seguranca > 2.0: return 150
    # Margem 150% a 200%: +130 pontos
    if margem_seguranca > 1.5: return 130
    # Margem 100% a 150%: +110 pontos
    if margem_seguranca > 1.0: return 110
    # Margem 50% a 100%: +70 pontos
    if margem_seguranca > 0.5: return 70
    # Margem 20% a 50%: +35 pontos
    if margem_seguranca > 0.2: return 35
    # Margem 0% a 20%: +20 pontos
    if margem_seguranca > 0: return 20
    # Margem < 0%: -70 pontos
    return -70

def score_beta(beta):
    """Pontuação baseada na volatilidade (Beta)."""
    if pd.isna(beta): return 0
    # Beta < 1: +35 pontos
    if beta < 1.0: return 35
    # Beta > 1.5: -35 pontos
    if beta > 1.5: return -35
    return 0

def score_market_cap(market_cap):
    """Pontuação baseada na Capitalização de Mercado."""
    if pd.isna(market_cap): return 0
    # Blue Cap: +35 pts
    if market_cap > 50_000_000_000: return 35
    # Mid Cap: +25 pts
    if market_cap > 10_000_000_000: return 25
    # Small Cap: +15 pts
    if market_cap > 2_000_000_000:  return 15
    return 0

def score_liquidez(liquidez):
    """Pontuação baseada na Liquidez Média Diária."""
    if pd.isna(liquidez): return 0
    # > R$ 50 milhões/dia: +35 pts
    if liquidez > 50_000_000: return 35
    # R$ 20M – R$ 50M/dia: +25 pts
    if liquidez > 20_000_000: return 25
    # R$ 5M – R$ 20M/dia: +15 pts
    if liquidez > 5_000_000:  return 15
    return 0

def score_fcf_yield(fcf_yield):
    """Pontuação baseada no Free Cash Flow Yield."""
    if pd.isna(fcf_yield): return 0
    # > 8%: +35 pontos
    if fcf_yield > 8: return 35
    # 5%–8%: +20 pontos
    if fcf_yield > 5: return 20
    return 0

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
        s_divida = score_divida(div_mc, row.get('divida_ebitda'), row.get('current_ratio'), setor)
        s_cresc_sent = score_crescimento_sentimento(row.get('crescimento_preco_5a'), row.get('sentimento_gauge'))
        s_ciclo = score_ciclo_mercado(row.get('Status 🟢🔴'))
        s_graham = score_graham(row.get('preco_atual'), row.get('lpa'), row.get('vpa'))
        s_beta = score_beta(row.get('beta'))
        s_mcap = score_market_cap(row.get('market_cap'))
        s_liquidez = score_liquidez(row.get('liquidez_media_diaria'))
        s_fcf = score_fcf_yield(row.get('fcf_yield'))
        
        score_total = s_dy + s_payout + s_roe + s_pl_pvp + s_divida + s_cresc_sent + s_ciclo + s_graham + s_beta + s_mcap + s_liquidez + s_fcf
        
        scores_data.append({
            'ticker_base': row['ticker_base'],
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
            'score_total': max(0, score_total) # Clamping em 0
        })

    scores_df = pd.DataFrame(scores_data).round(2)
    
    # Ordena pelo score total e salva
    scores_df = scores_df.sort_values(by='score_total', ascending=False)
    scores_df.to_csv(FN_OUT, index=False, float_format='%.2f')
    
    print(f"\nArquivo de scores salvo com sucesso em: {FN_OUT}")

if __name__ == '__main__':
    main()
