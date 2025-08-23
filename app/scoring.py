# app/scoring.py
import pandas as pd

def calculate_score_and_details(row: pd.Series) -> tuple[float, list[str]]:
    """
    Calcula o Score Total (0 a 200) e retorna as justificativas por critério.
    Esta é a lógica de fallback caso scores.csv não seja encontrado.
    """
    score = 0
    details = []
    # Critério: Dividend Yield (12 meses)
    dy_12m = row.get('DY (Taxa 12m, %)', 0)
    if dy_12m > 5: score += 20; details.append(f"DY 12m ({dy_12m:.1f}%) > 5%: **+20**")
    elif dy_12m > 3.5: score += 15; details.append(f"DY 12m ({dy_12m:.1f}%) > 3.5%: **+15**")
    elif dy_12m > 2: score += 10; details.append(f"DY 12m ({dy_12m:.1f}%) > 2%: **+10**")
    elif dy_12m < 2 and dy_12m > 0: score -= 5; details.append(f"DY 12m ({dy_12m:.1f}%) < 2%: **-5**")
    
    # Critério: Dividend Yield (Média 5 anos)
    dy_5y = row.get('DY 5 Anos Média (%)', 0)
    if dy_5y > 8: score += 25; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 8%: **+25**")
    elif dy_5y > 6: score += 20; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 6%: **+20**")
    elif dy_5y > 4: score += 10; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 4%: **+10**")
    
    # Critério: Payout Ratio
    payout = row.get('Payout Ratio (%)', 0)
    if 30 <= payout <= 60: score += 10; details.append(f"Payout ({payout:.0f}%) entre 30-60%: **+10**")
    elif 60 < payout <= 80: score += 5; details.append(f"Payout ({payout:.0f}%) entre 60-80%: **+5**")
    elif (payout > 0 and payout < 20) or payout > 80: score -= 5; details.append(f"Payout ({payout:.0f}%) fora de 20-80%: **-5**")
    
    # Critério: ROE (Return on Equity)
    roe = row.get('ROE (%)', 0)
    setor = row.get('Setor (brapi)', '').lower()
    if 'finance' in setor:
        if roe > 15: score += 25; details.append(f"ROE (Financeiro) ({roe:.1f}%) > 15%: **+25**")
        elif roe > 12: score += 20; details.append(f"ROE (Financeiro) ({roe:.1f}%) > 12%: **+20**")
        elif roe > 8: score += 10; details.append(f"ROE (Financeiro) ({roe:.1f}%) > 8%: **+10**")
    else:
        if roe > 12: score += 15; details.append(f"ROE ({roe:.1f}%) > 12%: **+15**")
        elif roe > 8: score += 5; details.append(f"ROE ({roe:.1f}%) > 8%: **+5**")
        
    # Critério: P/L e P/VP
    pl = row.get('P/L', 0)
    if 0 < pl < 12: score += 15; details.append(f"P/L ({pl:.2f}) < 12: **+15**")
    elif 12 <= pl < 18: score += 10; details.append(f"P/L ({pl:.2f}) < 18: **+10**")
    elif pl > 25: score -= 5; details.append(f"P/L ({pl:.2f}) > 25: **-5**")
    
    pvp = row.get('P/VP', 0)
    if 0 < pvp < 0.66: score += 20; details.append(f"P/VP ({pvp:.2f}) < 0.66: **+20**")
    elif 0.66 <= pvp < 1.5: score += 10; details.append(f"P/VP ({pvp:.2f}) < 1.5: **+10**")
    elif 1.5 <= pvp < 2.5: score += 5; details.append(f"P/VP ({pvp:.2f}) < 2.5: **+5**")
    elif pvp > 4: score -= 5; details.append(f"P/VP ({pvp:.2f}) > 4: **-5**")
    
    # Critérios de Dívida (Apenas para não-financeiros)
    if 'finance' not in setor:
        market_cap = row.get('Market Cap', 0)
        if market_cap > 0:
            debt_mc = row.get('Dívida Total', 0) / market_cap
            if debt_mc < 0.5: score += 10; details.append(f"Dívida/Market Cap ({debt_mc:.2f}) < 0.5: **+10**")
            elif debt_mc < 1.0: score += 5; details.append(f"Dívida/Market Cap ({debt_mc:.2f}) < 1.0: **+5**")
            elif debt_mc > 2.0: score -= 5; details.append(f"Dívida/Market Cap ({debt_mc:.2f}) > 2.0: **-5**")
        
        div_ebitda = row.get('Dívida/EBITDA', 0)
        if div_ebitda > 0:
            if div_ebitda < 1: score += 10; details.append(f"Dívida/EBITDA ({div_ebitda:.2f}) < 1: **+10**")
            elif div_ebitda < 2: score += 5; details.append(f"Dívida/EBITDA ({div_ebitda:.2f}) < 2: **+5**")
            elif div_ebitda > 6: score -= 5; details.append(f"Dívida/EBITDA ({div_ebitda:.2f}) > 6: **-5**")
            
    # Critério: Crescimento do Preço (5 Anos)
    growth = row.get('Crescimento Preço (%)', 0)
    if growth > 15: score += 15; details.append(f"Crescimento 5A ({growth:.1f}%) > 15%: **+15**")
    elif growth > 10: score += 10; details.append(f"Crescimento 5A ({growth:.1f}%) > 10%: **+10**")
    elif growth > 5: score += 5; details.append(f"Crescimento 5A ({growth:.1f}%) > 5%: **+5**")
    elif growth < 0: score -= 5; details.append(f"Crescimento 5A ({growth:.1f}%) < 0%: **-5**")
    
    # Critério: Sentimento de Mercado
    sentiment_gauge = row.get('Sentimento Gauge', 50)
    sentiment_score = 0
    if sentiment_gauge >= 50:
        sentiment_score = ((sentiment_gauge - 50) / 50) * 10
        details.append(f"Sentimento ({sentiment_gauge:.0f}/100) Positivo: **+{sentiment_score:.1f}**")
    else:
        sentiment_score = ((sentiment_gauge - 50) / 50) * 5
        details.append(f"Sentimento ({sentiment_gauge:.0f}/100) Negativo: **{sentiment_score:.1f}**")
    score += sentiment_score
    
    return max(0, min(200, score)), details


def build_score_details_from_row(row: pd.Series) -> list[str]:
    """
    Constrói a lista de detalhes do score a partir das colunas 'score_*'
    carregadas do arquivo scores.csv.
    """
    details = []
    mapping = [
        ('score_dy_12m', 'DY 12m'), ('score_dy_5anos', 'DY 5 Anos'),
        ('score_payout', 'Payout'), ('score_roe', 'ROE'),
        ('score_pl', 'P/L'), ('score_pvp', 'P/VP'),
        ('score_divida_marketcap', 'Dívida/Market Cap'),
        ('score_divida_ebitda', 'Dívida/EBITDA'),
        ('score_crescimento', 'Crescimento 5A'), ('score_sentimento', 'Sentimento'),
    ]
    for col, label in mapping:
        if col in row.index and pd.notna(row[col]):
            val = row[col]
            sign = '+' if val > 0 else ''
            details.append(f"{label}: **{sign}{val:.1f}**")
    return details
