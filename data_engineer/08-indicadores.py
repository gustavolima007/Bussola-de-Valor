# -*- coding: utf-8 -*-
"""
🔍 Script para Coleta de Indicadores Financeiros via yfinance + ta

Indicadores Coletados:
- Fundamentais: Preço Atual, P/L, P/VP, ROE, Payout, Crescimento 5a, Dívida, EBITDA, Dívida/EBITDA, Perfil da Ação
- Sentimento de Mercado (recomendações)
- 🆕 Técnicos (somente 1 ano, via ta): RSI(14), MACD(hist) e Volume (último)

Requisitos:
    pip install yfinance ta pandas tqdm
"""

import pandas as pd
import yfinance as yf
from tqdm.auto import tqdm
from pathlib import Path

# Indicadores técnicos via ta
from ta.momentum import RSIIndicator
from ta.trend import MACD

# --- Configurações ---
BASE = Path(__file__).resolve().parent.parent / 'data'
CAMINHO_ARQUIVO_ENTRADA = BASE / "acoes_e_fundos.csv"
CAMINHO_ARQUIVO_SAIDA = BASE / "indicadores.csv"

# ✅ período base para técnicos
PERIODO_PADRAO_HIST = "1y"


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
    sentiment_data = {'sentimento_gauge': 50.0, 'strong_buy': 0, 'buy': 0, 'hold': 0, 'sell': 0, 'strong_sell': 0}
    try:
        recommendations = ticker_obj.recommendations_summary
        if recommendations is None or recommendations.empty:
            return sentiment_data
        latest_rec = recommendations.iloc[-1]
        sb = int(latest_rec.get('strongBuy', 0))
        b = int(latest_rec.get('buy', 0))
        h = int(latest_rec.get('hold', 0))
        s = int(latest_rec.get('sell', 0))
        ss = int(latest_rec.get('strongSell', 0))
        sentiment_data.update({'strong_buy': sb, 'buy': b, 'hold': h, 'sell': s, 'strong_sell': ss})
        total = sb + b + h + s + ss
        if total > 0:
            score = (sb*2 + b*1 + s*(-1) + ss*(-2)) / total
            sentiment_data['sentimento_gauge'] = ((score + 2) / 4) * 100
    except Exception:
        pass
    return sentiment_data


# ===== Indicadores Técnicos (1y) com ta =====
def compute_indicadores_ta(hist: pd.DataFrame) -> dict:
    """Retorna apenas 3 colunas técnicas (1y): rsi_14_1y, macd_diff_1y, volume_1y."""
    out = {"rsi_14_1y": None, "macd_diff_1y": None, "volume_1y": None}
    if hist is None or hist.empty:
        return out

    close = hist.get("Close")
    volume = hist.get("Volume")

    # RSI(14)
    try:
        if close is not None and not close.dropna().empty and len(close.dropna()) >= 15:
            rsi_series = RSIIndicator(close=close, window=14, fillna=False).rsi()
            val = rsi_series.iloc[-1]
            out["rsi_14_1y"] = float(val) if pd.notna(val) else None
    except Exception:
        pass

    # MACD diff (histograma)
    try:
        if close is not None and not close.dropna().empty and len(close.dropna()) >= (26 + 9):
            macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9, fillna=False)
            diff = macd.macd_diff().iloc[-1]
            out["macd_diff_1y"] = float(diff) if pd.notna(diff) else None
    except Exception:
        pass

    # Volume (último)
    try:
        if volume is not None and not volume.dropna().empty:
            out["volume_1y"] = float(volume.iloc[-1]) if pd.notna(volume.iloc[-1]) else None
    except Exception:
        pass

    return out


NOME_EMPRESA_MANUAL = {
    "BRST3": "Brisanet Serviços de Telecomunicações S.A"
}

def fetch_stock_data(ticker_base: str, metadata: dict) -> dict | None:
    ticker_yf = f"{ticker_base}.SA"
    stock = yf.Ticker(ticker_yf)
    info = stock.info

    # Crescimento em 5 anos (mantido)
    hist_5y = stock.history(period="5y")
    growth_price = None
    if not hist_5y.empty and len(hist_5y["Close"]) > 1 and hist_5y["Close"].iloc[0] > 0:
        growth_price = ((hist_5y["Close"].iloc[-1] / hist_5y["Close"].iloc[0]) - 1) * 100

    # ✅ Histórico base para técnicos: 1 ano
    hist_1y = stock.history(period=PERIODO_PADRAO_HIST)

    # Técnicos (1y) com ta
    tecnicos = compute_indicadores_ta(hist_1y)

    # Fundamentais
    current_price = info.get("currentPrice")
    market_cap = info.get("marketCap", metadata.get("market_cap", 0))
    roe = info.get("returnOnEquity")
    payout_ratio = info.get("payoutRatio")
    total_debt = info.get("totalDebt")
    ebitda = info.get("ebitda")
    debt_to_ebitda = (total_debt / ebitda) if ebitda and total_debt else None
    empresa = NOME_EMPRESA_MANUAL.get(ticker_base, info.get("longName", metadata.get("empresa")))

    # --- 🆕 Adição para Fórmula de Graham ---
    # Coleta os dados e já calcula a margem de segurança percentual.
    lpa = info.get('trailingEps')
    vpa = info.get('bookValue')
    margem_seguranca_percent = None
    
    # Validação dos dados: LPA, VPA e Preço devem ser positivos para a fórmula
    if lpa and vpa and current_price and lpa > 0 and vpa > 0 and current_price > 0:
        try:
            # Fórmula de Graham: Valor Intrínseco = Raiz(22.5 * LPA * VPA)
            numero_graham = (22.5 * lpa * vpa) ** 0.5
            # Margem de Segurança = (Valor Intrínseco / Preço Atual) - 1
            margem_seguranca = (numero_graham / current_price) - 1
            margem_seguranca_percent = round(margem_seguranca * 100, 2)
        except (ValueError, TypeError):
            pass # Mantém margem_seguranca_percent como None

    return {
        "ticker": ticker_base,
        "empresa": empresa,
        "subsetor_b3": metadata.get("subsetor_b3"),
        "tipo": metadata.get("tipo"),
        "market_cap": market_cap,
        "logo": metadata.get("logo"),
        "preco_atual": current_price,
        "p_l": info.get("trailingPE"),
        "p_vp": info.get("priceToBook"),
        "payout_ratio": payout_ratio * 100 if payout_ratio else None,
        "crescimento_preco_5a": growth_price,
        "roe": roe * 100 if roe else None,
        "divida_total": total_debt,
        "ebitda": ebitda,
        "divida_ebitda": debt_to_ebitda,
        "perfil_acao": classify_stock_profile(current_price, market_cap),
        # 🆕 Campos para Fórmula de Graham
        "lpa": lpa,
        "vpa": vpa,
        "margem_seguranca_percent": margem_seguranca_percent,

        # Sentimento de Mercado (analistas)
        **get_market_sentiment(stock),

        # 🆕 Técnicos via ta (1y, 3 colunas)
        **tecnicos,
    }


def main():
    if not CAMINHO_ARQUIVO_ENTRADA.exists():
        print(f"❌ Arquivo de entrada não encontrado: {CAMINHO_ARQUIVO_ENTRADA}")
        return

    print("Iniciando extração de 08-indicadores...")
    df_input = pd.read_csv(CAMINHO_ARQUIVO_ENTRADA)

    df_input["ticker_norm"] = df_input["ticker"].str.strip().str.upper()
    metadata_map = df_input.set_index("ticker_norm").to_dict(orient="index")

    resultados = []
    for ticker_base, meta in tqdm(metadata_map.items(), desc="Coletando indicadores"):
        try:
            dados = fetch_stock_data(ticker_base, meta)
            if dados:
                resultados.append(dados)
        except Exception as e:
            print(f"❌ Erro ao processar {ticker_base}: {e}")

    if not resultados:
        print("⚠️ Nenhum dado foi coletado com sucesso.")
        return

    df_output = pd.DataFrame(resultados)
    df_output.columns = [c.strip().lower().replace(" ", "_") for c in df_output.columns]

    CAMINHO_ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df_output.to_csv(CAMINHO_ARQUIVO_SAIDA, index=False, encoding='utf-8-sig')

    print(f"\n✅ Arquivo de indicadores salvo com sucesso em: {CAMINHO_ARQUIVO_SAIDA}")
    print(f"Total de {len(df_output)} tickers processados.")


if __name__ == "__main__":
    main()
