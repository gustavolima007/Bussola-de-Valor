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
    # DY 12 meses: >5% (+33 pts), 3.5%-5% (+25 pts), 2%-3.5% (+17 pts), <2% (-8 pts)
    if pd.notna(dy_12m):
        if dy_12m > 5: score += 33
        elif dy_12m > 3.5: score += 25
        elif dy_12m > 2: score += 17
        elif dy_12m < 2 and dy_12m > 0: score -= 8
    # DY média 5 anos: >10% (+50 pts), 8%-10% (+42 pts), 6%-8% (+33 pts), 4%-6% (+17 pts)
    if pd.notna(dy_5a):
        if dy_5a > 10: score += 50
        elif dy_5a > 8: score += 42
        elif dy_5a > 6: score += 33
        elif dy_5a > 4: score += 17
    return score

def score_payout(payout):
    """Pontuação para o Payout Ratio."""
    # Payout: 30%-60% (+17 pts), 60%-80% (+8 pts), <20% ou >80% (-8 pts)
    if pd.isna(payout): return 0
    if 30 <= payout <= 60: return 17
    if 60 < payout <= 80: return 8
    if (payout > 0 and payout < 20) or payout > 80: return -8
    return 0

def score_roe(roe, setor):
    """Pontuação para o ROE, com lógica diferente para o setor financeiro."""
    if pd.isna(roe): return 0
    is_finance = 'finance' in str(setor).lower()
    # ROE (Setor Financeiro): >15% (+42 pts), 12%-15% (+33 pts), 8%-12% (+17 pts)
    if is_finance:
        if roe > 15: return 42
        if roe > 12: return 33
        if roe > 8: return 17
    # ROE (Outros Setores): >12% (+25 pts), 8%-12% (+8 pts)
    else:
        if roe > 12: return 25
        if roe > 8: return 8
    return 0

def score_pl_pvp(pl, pvp):
    """Pontuação combinada para P/L e P/VP."""
    score = 0
    # P/L: <12 (+25 pts), 12-18 (+17 pts), >25 (-8 pts)
    if pd.notna(pl) and pl > 0:
        if pl < 12: score += 25
        elif pl < 18: score += 17
        elif pl > 25: score -= 8
    # P/VP: <0.50 (+75 pts), 0.50-0.66 (+67 pts), 0.66-1.00 (+50 pts), 1.00-1.50 (+25 pts), 1.50-2.50 (+8 pts), >4.00 (-17 pts)
    if pd.notna(pvp) and pvp > 0:
        if pvp < 0.50: score += 75
        elif pvp < 0.66: score += 67
        elif pvp < 1.00: score += 50
        elif pvp < 1.50: score += 25
        elif pvp < 2.50: score += 8
        elif pvp > 4.00: score -= 17
    return score

def score_divida(div_mc, div_ebitda, current_ratio, subsetor):
    """Pontuação para os indicadores de endividamento."""
    if 'finance' in str(subsetor).lower(): return 0
    score = 0
    # Dívida/Market Cap: <0.3 (+25 pts), 0.3-0.7 (+17 pts), >1.5 (-17 pts)
    if pd.notna(div_mc):
        if div_mc < 0.3: score += 25
        elif div_mc < 0.7: score += 17
        elif div_mc > 1.5: score -= 17
    # Dívida/EBITDA: <1 (+25 pts), 1-3 (+8 pts), >5 (-17 pts)
    if pd.notna(div_ebitda) and div_ebitda > 0:
        if div_ebitda < 1: score += 25
        elif div_ebitda < 3: score += 8
        elif div_ebitda > 5: score -= 17
    # Current Ratio: >2 (+17 pts), 1-2 (+8 pts), <1 (-8 pts)
    if pd.notna(current_ratio):
        if current_ratio > 2: score += 17
        elif current_ratio > 1: score += 8
        else: score -= 8
    return score

def score_crescimento_sentimento(crescimento, sentimento):
    """Pontuação para crescimento de preço e sentimento de mercado."""
    score = 0
    # Crescimento Preço 5 Anos: >15% (+25 pts), 10%-15% (+17 pts), 5%-10% (+8 pts), <0% (-8 pts)
    if pd.notna(crescimento):
        if crescimento > 15: score += 25
        elif crescimento > 10: score += 17
        elif crescimento > 5: score += 8
        elif crescimento < 0: score -= 8
    # Sentimento do Mercado: -8 a +17 pts (proporcional)
    if pd.notna(sentimento):
        # Mapeia o sentimento (0-100) para o intervalo de pontos (-8 a +17)
        score += (sentimento / 100.0) * 25 - 8
    return score

def score_ciclo_mercado(status_ciclo):
    """Pontuação baseada no status do ciclo de mercado."""
    if pd.isna(status_ciclo): return 0
    # Compra (Pânico / Medo Extremo): +33 pontos
    if status_ciclo == 'Compra': return 33
    # Venda (Euforia / Ganância Extrema): -33 pontos
    if status_ciclo == 'Venda': return -33
    # 'Observação' ou qualquer outro valor
    return 0

def score_graham(preco_atual, lpa, vpa):
    """Pontuação baseada na Margem de Segurança da Fórmula de Graham."""
    # A fórmula só é válida para empresas lucrativas (LPA > 0) e com patrimônio positivo (VPA > 0)
    if pd.isna(preco_atual) or pd.isna(lpa) or pd.isna(vpa) or lpa <= 0 or vpa <= 0 or preco_atual <= 0:
        return 0

    try:
        # Fórmula de Graham: Valor Intrínseco = Raiz(22.5 * LPA * VPA)
        numero_graham = (22.5 * lpa * vpa) ** 0.5
        # Margem de Segurança = (Valor Intrínseco / Preço Atual) - 1
        margem_seguranca = (numero_graham / preco_atual) - 1
    except (ValueError, TypeError):
        return 0

    # Margem > 200%: +67 pontos
    if margem_seguranca > 2.0: return 67
    # Margem 150% a 200%: +58 pontos
    if margem_seguranca > 1.5: return 58
    # Margem 100% a 150%: +50 pontos
    if margem_seguranca > 1.0: return 50
    # Margem 50% a 100%: +33 pontos
    if margem_seguranca > 0.5: return 33
    # Margem 20% a 50%: +17 pontos
    if margem_seguranca > 0.2: return 17
    # Margem 0% a 20%: +8 pontos
    if margem_seguranca > 0: return 8
    # Margem < 0%: -33 pontos
    return -33

def score_beta(beta):
    """Pontuação baseada na volatilidade (Beta)."""
    if pd.isna(beta): return 0
    # Beta < 1: +17 pontos
    if beta < 1.0: return 17
    # Beta > 1.5: -17 pontos
    if beta > 1.5: return -17
    return 0

def score_market_cap(market_cap):
    """Pontuação baseada na Capitalização de Mercado."""
    if pd.isna(market_cap): return 0
    # Blue Cap: +17 pts
    if market_cap > 50_000_000_000: return 17
    # Mid Cap: +12 pts
    if market_cap > 10_000_000_000: return 12
    # Small Cap: +7 pts
    if market_cap > 2_000_000_000:  return 7
    return 0

def score_liquidez(liquidez):
    """Pontuação baseada na Liquidez Média Diária."""
    if pd.isna(liquidez): return 0
    # > R$ 50 milhões/dia: +17 pts
    if liquidez > 50_000_000: return 17
    # R$ 20M – R$ 50M/dia: +12 pts
    if liquidez > 20_000_000: return 12
    # R$ 5M – R$ 20M/dia: +7 pts
    if liquidez > 5_000_000:  return 7
    return 0

def score_fcf_yield(fcf_yield):
    """Pontuação baseada no Free Cash Flow Yield."""
    if pd.isna(fcf_yield): return 0
    # > 8%: +17 pontos
    if fcf_yield > 8: return 17
    # 5%–8%: +8 pontos
    if fcf_yield > 5: return 8
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
