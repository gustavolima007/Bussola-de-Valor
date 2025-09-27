# app/scoring.py
import pandas as pd

def calculate_score_and_details(row: pd.Series) -> tuple[float, list[str]]:
    """
    Calcula o Score Total (0 a 1000) e retorna as justificativas por critério.
    Esta é a lógica de fallback caso scores.csv não seja encontrado.
    """
    score = 0
    details = []

    # Critério: Dividend Yield (DY) – até 200 pts
    dy_12m = row.get('DY (Taxa 12m, %)', 0)
    if dy_12m > 5: score += 60; details.append(f"DY 12m ({dy_12m:.1f}%) > 5%: **+60**")
    elif dy_12m > 3.5: score += 45; details.append(f"DY 12m ({dy_12m:.1f}%) > 3.5%: **+45**")
    elif dy_12m > 2: score += 30; details.append(f"DY 12m ({dy_12m:.1f}%) > 2%: **+30**")
    elif dy_12m < 2 and dy_12m > 0: score -= 20; details.append(f"DY 12m ({dy_12m:.1f}%) < 2%: **-20**")

    dy_5y = row.get('DY 5 Anos Média (%)', 0)
    if dy_5y > 10: score += 120; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 10%: **+120**")
    elif dy_5y > 8: score += 100; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 8%: **+100**")
    elif dy_5y > 6: score += 80; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 6%: **+80**")
    elif dy_5y > 4: score += 40; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) > 4%: **+40**")
    elif dy_5y < 3 and dy_5y > 1: score -= 20; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) < 3%: **-20**")
    elif dy_5y <= 1: score -= 30; details.append(f"DY Média 5 Anos ({dy_5y:.1f}%) < 1%: **-30**")

    # Critério: Valuation (P/L e P/VP) – até 180 pts
    pl = row.get('P/L', 0)
    if 0 < pl < 12: score += 45; details.append(f"P/L ({pl:.2f}) < 12: **+45**")
    elif 12 <= pl < 18: score += 30; details.append(f"P/L ({pl:.2f}) < 18: **+30**")
    elif pl > 25: score -= 15; details.append(f"P/L ({pl:.2f}) > 25: **-15**")

    pvp = row.get('P/VP', 0)
    if 0 < pvp < 0.5: score += 135; details.append(f"P/VP ({pvp:.2f}) < 0.5: **+135**")
    elif pvp < 0.66: score += 120; details.append(f"P/VP ({pvp:.2f}) < 0.66: **+120**")
    elif pvp < 1: score += 90; details.append(f"P/VP ({pvp:.2f}) < 1: **+90**")
    elif pvp < 1.5: score += 45; details.append(f"P/VP ({pvp:.2f}) < 1.5: **+45**")
    elif pvp < 2.5: score += 15; details.append(f"P/VP ({pvp:.2f}) < 2.5: **+15**")
    elif pvp > 4: score -= 30; details.append(f"P/VP ({pvp:.2f}) > 4: **-30**")

    # Critério: Rentabilidade e Gestão (ROE e Payout) – até 110 pts
    roe = row.get('ROE (%)', 0)
    setor = row.get('Setor (brapi)', '').lower()
    if 'finance' in setor:
        if roe > 15: score += 80; details.append(f"ROE (Financeiro) ({roe:.1f}%) > 15%: **+80**")
        elif roe > 12: score += 60; details.append(f"ROE (Financeiro) ({roe:.1f}%) > 12%: **+60**")
        elif roe > 8: score += 30; details.append(f"ROE (Financeiro) ({roe:.1f}%) > 8%: **+30**")
    else:
        if roe > 12: score += 45; details.append(f"ROE ({roe:.1f}%) > 12%: **+45**")
        elif roe > 8: score += 15; details.append(f"ROE ({roe:.1f}%) > 8%: **+5**")

    payout = row.get('Payout Ratio (%)', 0)
    if 30 <= payout <= 60: score += 30; details.append(f"Payout ({payout:.0f}%) entre 30-60%: **+30**")
    elif 60 < payout <= 80: score += 15; details.append(f"Payout ({payout:.0f}%) entre 60-80%: **+15**")
    elif (payout > 0 and payout < 20) or payout > 80: score -= 15; details.append(f"Payout ({payout:.0f}%) fora de 20-80%: **-15**")

    # Critério: Saúde Financeira (Endividamento e Liquidez) – até 130 pts
    if 'finance' not in setor:
        market_cap = row.get('Market Cap', 0)
        if market_cap > 0:
            debt_mc = row.get('Dívida Total', 0) / market_cap
            if debt_mc < 0.3: score += 45; details.append(f"Dívida/Market Cap ({debt_mc:.2f}) < 0.3: **+45**")
            elif debt_mc < 0.7: score += 30; details.append(f"Dívida/Market Cap ({debt_mc:.2f}) < 0.7: **+30**")
            elif debt_mc > 1.5: score -= 30; details.append(f"Dívida/Market Cap ({debt_mc:.2f}) > 1.5: **-30**")
        
        div_ebitda = row.get('Dívida/EBITDA', 0)
        if div_ebitda > 0:
            if div_ebitda < 1: score += 45; details.append(f"Dívida/EBITDA ({div_ebitda:.2f}) < 1: **+45**")
            elif div_ebitda < 3: score += 15; details.append(f"Dívida/EBITDA ({div_ebitda:.2f}) < 3: **+15**")
            elif div_ebitda > 5: score -= 30; details.append(f"Dívida/EBITDA ({div_ebitda:.2f}) > 5: **-30**")

    current_ratio = row.get('Current Ratio', 0)
    if current_ratio > 2: score += 40; details.append(f"Current Ratio ({current_ratio:.2f}) > 2: **+40**")
    elif current_ratio > 1: score += 20; details.append(f"Current Ratio ({current_ratio:.2f}) > 1: **+20**")
    elif current_ratio < 1: score -= 15; details.append(f"Current Ratio ({current_ratio:.2f}) < 1: **-15**")

    # Critério: Crescimento e Sentimento – até 90 pts
    growth = row.get('Crescimento Preço (%)', 0)
    if growth > 15: score += 50; details.append(f"Crescimento 5A ({growth:.1f}%) > 15%: **+50**")
    elif growth > 10: score += 35; details.append(f"Crescimento 5A ({growth:.1f}%) > 10%: **+35**")
    elif growth > 5: score += 20; details.append(f"Crescimento 5A ({growth:.1f}%) > 5%: **+20**")
    elif growth < 0: score -= 20; details.append(f"Crescimento 5A ({growth:.1f}%) < 0%: **-20**")

    sentiment_gauge = row.get('Sentimento Gauge', 50)
    sentiment_score = 0
    if sentiment_gauge >= 50:
        sentiment_score = ((sentiment_gauge - 50) / 50) * 40
        details.append(f"Sentimento ({sentiment_gauge:.0f}/100) Positivo: **+{sentiment_score:.1f}**")
    else:
        sentiment_score = ((sentiment_gauge - 50) / 50) * 20
        details.append(f"Sentimento ({sentiment_gauge:.0f}/100) Negativo: **{sentiment_score:.1f}**")
    score += sentiment_score

    # Critério: Ciclo de Mercado (Timing) – de -70 a +70 pts
    # Esta lógica depende de um dado externo, que não está no row

    # Critério: Fórmula de Graham (Margem de Segurança) – de -70 a +150 pts
    graham_margin = row.get('margem_seguranca_percent')
    if graham_margin is not None:
        if graham_margin > 200: score += 150; details.append(f"Margem Graham ({graham_margin:.2f}%) > 200%: **+150**")
        elif graham_margin >= 150: score += 130; details.append(f"Margem Graham ({graham_margin:.2f}%) >= 150%: **+130**")
        elif graham_margin >= 100: score += 110; details.append(f"Margem Graham ({graham_margin:.2f}%) >= 100%: **+110**")
        elif graham_margin >= 50: score += 70; details.append(f"Margem Graham ({graham_margin:.2f}%) >= 50%: **+70**")
        elif graham_margin >= 20: score += 35; details.append(f"Margem Graham ({graham_margin:.2f}%) >= 20%: **+35**")
        elif graham_margin >= 0: score += 20; details.append(f"Margem Graham ({graham_margin:.2f}%) >= 0%: **+20**")
        else: score -= 70; details.append(f"Margem Graham ({graham_margin:.2f}%) < 0%: **-70**")

    # Critério: Volatilidade (Beta) – de -35 a +35 pts
    beta = row.get('Beta', 1)
    if beta < 1: score += 35; details.append(f"Beta ({beta:.2f}) < 1: **+35**")
    elif beta > 1.5: score -= 35; details.append(f"Beta ({beta:.2f}) > 1.5: **-35**")

    # Critério: Capitalização de Mercado – até 35 pts
    market_cap = row.get('Market Cap', 0)
    if market_cap > 50e9: score += 35; details.append(f"Market Cap > 50bi: **+35**")
    elif market_cap > 10e9: score += 25; details.append(f"Market Cap > 10bi: **+25**")
    elif market_cap > 2e9: score += 15; details.append(f"Market Cap > 2bi: **+15**")

    # Critério: Liquidez Média Diária – até 35 pts
    liquidez = row.get('Volume Médio Diário', 0)
    if liquidez > 50e6: score += 35; details.append(f"Liquidez > 50M/dia: **+35**")
    elif liquidez > 20e6: score += 25; details.append(f"Liquidez > 20M/dia: **+25**")
    elif liquidez > 5e6: score += 15; details.append(f"Liquidez > 5M/dia: **+15**")

    # Critério: Geração de Caixa (FCF Yield) – até 35 pts
    fcf_yield = row.get('FCF Yield', 0)
    if fcf_yield > 0.08: score += 35; details.append(f"FCF Yield ({fcf_yield:.1%}) > 8%: **+35**")
    elif fcf_yield > 0.05: score += 20; details.append(f"FCF Yield ({fcf_yield:.1%}) > 5%: **+20**")

    return max(0, min(1000, score)), details


def build_score_details_from_row(row: pd.Series) -> list[str]:
    """
    Constrói a lista de detalhes do score a partir das colunas de score pré-calculadas,
    mas gera as mesmas mensagens detalhadas da função de cálculo online.
    """
    # Usa a função de cálculo de score para gerar os detalhes, garantindo consistência.
    # A pontuação final virá do CSV, mas os detalhes são gerados dinamicamente.
    _, details = calculate_score_and_details(row)
    return details


from joblib import Parallel, delayed

def calculate_scores_in_parallel(df: pd.DataFrame) -> list[tuple[float, list[str]]]:
    """
    Calcula os scores para todas as ações no DataFrame em paralelo.
    """
    if df.empty:
        return []
    
    # Extrai as linhas como uma lista de Series para o joblib
    rows = [row for _, row in df.iterrows()]
    
    # Usa n_jobs=-1 para usar todos os cores de CPU disponíveis
    # O backend 'threading' é usado para evitar problemas de memória com pandas Series
    results = Parallel(n_jobs=-1, backend='threading')(delayed(calculate_score_and_details)(row) for row in rows)
    
    return results
