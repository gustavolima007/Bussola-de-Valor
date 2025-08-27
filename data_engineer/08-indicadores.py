# -*- coding: utf-8 -*-
"""
🔍 Script para Coleta de Indicadores Financeiros via yfinance

Este script busca uma vasta gama de indicadores fundamentalistas e de mercado
para uma lista de tickers da B3, consolidando tudo em um único arquivo CSV.

Indicadores Coletados:
- Preço Atual, P/L (Preço/Lucro), P/VP (Preço/Valor Patrimonial)
- ROE (Return on Equity), Payout Ratio (percentual de lucro distribuído)
- Crescimento do preço nos últimos 5 anos
- Dívida Total, EBITDA, e a relação Dívida/EBITDA
- Perfil da Ação (classificação por capitalização de mercado)
- Sentimento de Mercado (baseado em recomendações de analistas)

Etapas do Processo:
1.  Lê a lista de tickers do arquivo 'data/acoes_e_fundos.csv'.
2.  Para cada ticker, consulta a API do yfinance para obter os dados.
3.  Calcula métricas derivadas como o perfil da ação e o sentimento.
4.  Normaliza os nomes das colunas para um padrão consistente.
5.  Salva o DataFrame consolidado em 'data/indicadores.csv'.
"""

import pandas as pd
import yfinance as yf
from tqdm.auto import tqdm
from pathlib import Path

# --- Configuração de Caminhos ---
BASE = Path(__file__).resolve().parent.parent / 'data'
CAMINHO_ARQUIVO_ENTRADA = BASE / "acoes_e_fundos.csv"
CAMINHO_ARQUIVO_SAIDA = BASE / "indicadores.csv"

def classify_stock_profile(price: float, market_cap: float) -> str:
    """Classifica o perfil da ação com base no preço e na capitalização de mercado."""
    if price is not None and price < 1.0:
        return "Penny Stock"
    if market_cap is None or market_cap == 0:
        return "N/A"
    if market_cap > 50_000_000_000: # > 50 Bilhões
        return "Blue Chip"
    if market_cap > 10_000_000_000: # > 10 Bilhões
        return "Mid Cap"
    if market_cap > 2_000_000_000:  # > 2 Bilhões
        return "Small Cap"
    return "Micro Cap"

def get_market_sentiment(ticker_obj: yf.Ticker) -> dict:
    """Calcula um medidor de sentimento de mercado com base nas recomendações dos analistas."""
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
        total_recommendations = sb + b + h + s + ss
        
        if total_recommendations > 0:
            # Mapeia as recomendações para um score de -2 (Strong Sell) a +2 (Strong Buy)
            score = (sb * 2 + b * 1 + h * 0 + s * -1 + ss * -2) / total_recommendations
            # Normaliza o score para uma escala de 0 a 100
            sentiment_data['sentimento_gauge'] = ((score + 2) / 4) * 100
            
    except Exception:
        pass # Mantém os valores padrão em caso de erro
    return sentiment_data

def fetch_stock_data(ticker_base: str, metadata: dict) -> dict | None:
    """Busca e processa os dados de um único ticker usando yfinance."""
    ticker_yf = f"{ticker_base}.SA"
    stock = yf.Ticker(ticker_yf)
    info = stock.info

    # Calcula o crescimento do preço nos últimos 5 anos
    hist = stock.history(period="5y")
    growth_price = None
    if not hist.empty and len(hist["Close"]) > 1 and hist["Close"].iloc[0] > 0:
        growth_price = ((hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1) * 100

    # Extrai e calcula os indicadores
    current_price = info.get("currentPrice")
    market_cap = info.get("marketCap", metadata.get("market_cap", 0))
    roe = info.get("returnOnEquity")
    payout_ratio = info.get("payoutRatio")
    total_debt = info.get("totalDebt")
    ebitda = info.get("ebitda")
    debt_to_ebitda = (total_debt / ebitda) if ebitda and total_debt else None

    # Monta o dicionário de resultados
    return {
        "ticker": ticker_base,
        "empresa": info.get("longName", metadata.get("empresa")),
        "setor_brapi": metadata.get("setor_brapi"),
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
        **get_market_sentiment(stock)
    }

def main():
    """Função principal para orquestrar a coleta e o salvamento dos dados."""
    if not CAMINHO_ARQUIVO_ENTRADA.exists():
        print(f"❌ Arquivo de entrada não encontrado: {CAMINHO_ARQUIVO_ENTRADA}")
        return

    print(f"Lendo tickers de: {CAMINHO_ARQUIVO_ENTRADA}")
    df_input = pd.read_csv(CAMINHO_ARQUIVO_ENTRADA)
    
    # Prepara um mapa de metadados para acesso rápido
    df_input["ticker_norm"] = df_input["ticker"].str.strip().str.upper()
    metadata_map = df_input.set_index("ticker_norm").to_dict(orient="index")

    resultados = []
    # Itera sobre os tickers únicos com uma barra de progresso
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

    # Converte a lista de resultados em um DataFrame e padroniza as colunas
    df_output = pd.DataFrame(resultados)
    df_output.columns = [c.strip().lower().replace(" ", "_") for c in df_output.columns]
    
    # Salva o arquivo final
    CAMINHO_ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df_output.to_csv(CAMINHO_ARQUIVO_SAIDA, index=False, encoding='utf-8-sig')
    print(f"\n✅ Arquivo de indicadores salvo com sucesso em: {CAMINHO_ARQUIVO_SAIDA}")
    print(f"Total de {len(df_output)} tickers processados.")

if __name__ == "__main__":
    main()
