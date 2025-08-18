# Consolida indicadores fundamentais e de mercado via yfinance para os tickers em ../data/acoes_e_fundos.csv:
# preço atual, P/L, P/VP, ROE, payout, crescimento 5A, dívida total, EBITDA, Dívida/EBITDA,
# perfil da ação e sentimento de mercado. Salva tudo padronizado em ../data/indicadores.csv.
import os
import pandas as pd
import yfinance as yf
from tqdm.auto import tqdm


# O código lê a lista de tickers do arquivo ../data/acoes_e_fundos.csv, remove o sufixo .SA, busca informações de cada ativo no Yahoo Finance, calcula o perfil da ação (Penny Stock, Micro Cap, Small Cap, Mid Cap ou Blue Chip), extrai indicadores como preço atual, P/L, P/VP, ROE, payout ratio, crescimento do preço em 5 anos, dívida total, EBITDA, relação dívida/EBITDA e sentimento de mercado baseado em recomendações de analistas. Todos os dados são organizados em colunas padronizadas em letras minúsculas, sem acentos e com underscores, e o resultado é salvo em ../data/indicadores.csv.

from pathlib import Path
BASE = Path(__file__).resolve().parent.parent / 'data'

CAMINHO_ARQUIVO = BASE / "acoes_e_fundos.csv"
SAIDA_ARQUIVO = BASE / "indicadores.csv"

def normalize_ticker_base(t):
    if pd.isna(t):
        return None
    t = str(t).strip().upper()
    if t.endswith(".SA"):
        t = t[:-3]
    return t

def classify_stock_profile(price: float, market_cap: float) -> str:
    if price is not None and price < 1.0:
        return "Penny Stock"
    if market_cap is None or market_cap == 0:
        return "N/A"
    if market_cap > 50_000_000_000:
        return "Blue Chip"
    if market_cap > 10_000_000_000:
        return "Mid Cap"
    if market_cap > 2_000_000_000:
        return "Small Cap"
    return "Micro Cap"

def get_market_sentiment(ticker_obj: yf.Ticker) -> dict:
    out = {'sentimento_gauge': 50.0, 'strong_buy': 0, 'buy': 0, 'hold': 0, 'sell': 0, 'strong_sell': 0}
    try:
        summary = ticker_obj.recommendations_summary
        if summary is None or summary.empty:
            return out
        rec = summary.iloc[-1]
        sb = int(rec.get('strongBuy', 0)); b = int(rec.get('buy', 0))
        h = int(rec.get('hold', 0)); s = int(rec.get('sell', 0)); ss = int(rec.get('strongSell', 0))
        out.update({'strong_buy': sb, 'buy': b, 'hold': h, 'sell': s, 'strong_sell': ss})
        total = sb + b + h + s + ss
        if total > 0:
            score = (sb*2 + b*1 + h*0 + s*-1 + ss*-2) / total
            out['sentimento_gauge'] = ((score + 2) / 4) * 100
    except Exception:
        pass
    return out

def fetch_stock_data(ticker_base: str, meta: dict) -> dict | None:
    """
    ticker_base vem SEM .SA (ex.: 'VIVT3'). A consulta no Yahoo é feita com '.SA'.
    """
    ticker_yf = f"{ticker_base}.SA"
    stock = yf.Ticker(ticker_yf)
    info = stock.info

    # histórico para crescimento (se vier vazio, não quebra)
    hist = stock.history(period="5y", interval="1d")
    growth_price = 0.0
    try:
        if not hist.empty and len(hist["Close"]) > 1 and hist["Close"].iloc[0] > 0:
            growth_price = ((hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1) * 100
    except Exception:
        growth_price = 0.0

    current_price = info.get("currentPrice", 0.0)
    market_cap = info.get("marketCap", 0.0)
    if not market_cap or market_cap == 0:
        so = info.get("sharesOutstanding", 0)
        if so and current_price:
            market_cap = so * current_price
    if not market_cap:
        market_cap = meta.get("market_cap", 0)

    roe = info.get("returnOnEquity")
    roe = roe * 100 if roe is not None else None
    payout_ratio = info.get("payoutRatio")
    payout_ratio = payout_ratio * 100 if payout_ratio is not None else None

    debt_total = info.get("totalDebt")
    ebitda = info.get("ebitda")
    divida_ebitda = (debt_total / ebitda) if ebitda not in (None, 0) and debt_total is not None else None

    perfil = classify_stock_profile(current_price, market_cap)
    sentimento = get_market_sentiment(stock)

    # monta registro (ticker SEM .SA)
    row = {
        "ticker": ticker_base,
        "empresa": meta.get("empresa", "N/A"),
        "setor_brapi": meta.get("setor_brapi", "N/A"),
        "tipo": meta.get("tipo", "N/A"),
        "market_cap": market_cap,
        "logo": meta.get("logo", "N/A"),
        "preco_atual": current_price,
        "p_l": info.get("trailingPE"),
        "p_vp": info.get("priceToBook"),
        "payout_ratio": payout_ratio,
        "crescimento_preco": growth_price,
        "roe": roe,
        "divida_total": debt_total,
        "ebitda": ebitda,
        "perfil_acao": perfil,
    }
    row.update(sentimento)
    row["divida_ebitda"] = divida_ebitda
    return row

def padroniza_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

def main():
    if not os.path.exists(CAMINHO_ARQUIVO):
        print(f"❌ Arquivo não encontrado: {CAMINHO_ARQUIVO}")
        return

    df_in = pd.read_csv(CAMINHO_ARQUIVO)

    # normaliza tickers do CSV para chavear sem .SA e sem espaços
    df_in["ticker_norm"] = df_in["ticker"].apply(normalize_ticker_base)
    df_in = df_in.dropna(subset=["ticker_norm"])

    # mapeia 1ª ocorrência por ticker (evita .iloc[0] em DataFrame vazio)
    meta_map = df_in.groupby("ticker_norm", as_index=True).first().to_dict(orient="index")

    resultados = []
    for ticker_base, meta in tqdm(meta_map.items(), total=len(meta_map), desc="Coletando indicadores"):
        ticker_yf = f"{ticker_base}.SA"
        print(f"Processando: {ticker_yf}...", end="")
        try:
            dados = fetch_stock_data(ticker_base, meta or {})
            if dados:
                resultados.append(dados)
                print(" ✅")
            else:
                print(" ⚠️ sem dados")
        except Exception as e:
            print(f" ❌ Erro: {e}")

    if not resultados:
        print("❌ Nenhum dado coletado.")
        return

    df_out = pd.DataFrame(resultados)
    df_out = padroniza_colunas(df_out)
    os.makedirs(os.path.dirname(SAIDA_ARQUIVO), exist_ok=True)
    df_out.to_csv(SAIDA_ARQUIVO, index=False)
    print(f"\n✅ Arquivo salvo em: {SAIDA_ARQUIVO}")

if __name__ == "__main__":
    main()
