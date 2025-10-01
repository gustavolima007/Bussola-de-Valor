# -*- coding: utf-8 -*-
"""
Script para Coleta de Indicadores Financeiros via yfinance + ta
   Calcula e classifica o ciclo de mercado para cada ativo.

Indicadores Coletados:
- Fundamentais: Preço Atual, P/L, P/VP, ROE, Payout, Crescimento 5a, Dívida, EBITDA, Dívida/EBITDA, Perfil da Ação
- Sentimento de Mercado (recomendações)
- Técnicos (somente 1 ano, via ta): RSI(14), MACD(hist) e Volume (último)

Requisitos:
    pip install yfinance ta pandas tqdm
"""

import pandas as pd
import yfinance as yf
from tqdm.auto import tqdm
import random
import time
from pathlib import Path
from common import DATA_DIR, tratar_dados_para_json

# Indicadores técnicos via ta
from ta.momentum import RSIIndicator
from ta.trend import MACD

# --- Configurações ---
CAMINHO_ARQUIVO_ENTRADA = DATA_DIR / "acoes_e_fundos.csv"
CAMINHO_ARQUIVO_SAIDA = DATA_DIR / "indicadores.csv"

# período base para técnicos
PERIODO_PADRAO_HIST = "1y"

# --- Frases por ciclo de mercado ---
frases_por_ciclo = {
    "Pânico / Fundo": [
        {"autor": "Howard Marks", "frase": "O risco está mais baixo quando o preço está mais baixo.", "status": "Compra"},
        {"autor": "George Soros", "frase": "A reflexividade transforma medo em oportunidade.", "status": "Compra"},
        {"autor": "Luiz Barsi", "frase": "O mercado dá presentes para quem não tem medo.", "status": "Compra"},
        {"autor": "Warren Buffett", "frase": "As melhores oportunidades vêm quando ninguém quer comprar.", "status": "Compra"},
    ],
    "Neutro / Transição": [
        {"autor": "Howard Marks", "frase": "Você não pode prever, mas pode se preparar.", "status": "Observação"},
        {"autor": "George Soros", "frase": "Não é sobre estar certo, é sobre estar lucrativo.", "status": "Observação"},
        {"autor": "Luiz Barsi", "frase": "Tenha paciência: o mercado sempre volta à razão.", "status": "Observação"},
        {"autor": "Warren Buffett", "frase": "É melhor esperar por uma oportunidade clara do que agir na dúvida.", "status": "Observação"},
    ],
    "Euforia / Topo": [
        {"autor": "Howard Marks", "frase": "O maior risco surge quando tudo parece seguro.", "status": "Venda"},
        {"autor": "George Soros", "frase": "Quando todos estão certos, é hora de duvidar.", "status": "Venda"},
        {"autor": "Luiz Barsi", "frase": "Quem compra na euforia, paga caro pela empolgação.", "status": "Venda"},
        {"autor": "Warren Buffett", "frase": "Seja temeroso quando os outros são gananciosos.", "status": "Venda"},
    ],
}

# --- Funções de Classificação e Cálculo ---

def get_pl_ratio(ticker: str) -> str:
    """
    Obtém o índice P/L (Preço/Lucro) via yfinance (TTM).
    """
    try:
        # Adiciona o sufixo .SA para ações da B3 e busca os dados
        stock = yf.Ticker(f"{ticker}.SA")
        info = stock.info
        
        # P/L = Preço da ação / Lucro por ação (EPS, TTM)
        pl_ratio = info.get('trailingPE')
        
        if pl_ratio is not None and pl_ratio > 0:
            return f"{pl_ratio:.2f}"
        return "N/A"
    except Exception:
        return "N/A"


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


def classificar_indicador_tecnico(valor: float, lim_baixo: float, lim_alto: float, tipo: str) -> str:
    """Classifica um valor conforme o tipo do indicador."""
    if pd.isna(valor):
        return "N/A"
    v = float(valor)
    if tipo == "RSI":
        if v < lim_baixo: return "Baixo"
        elif v > lim_alto: return "Alto"
        else: return "Medio"
    elif tipo == "MACD":
        if v < lim_baixo: return "Baixa"
        elif v > lim_alto: return "Alta"
        else: return "Neutra"
    elif tipo == "Volume":
        if v < lim_baixo: return "Fraco"
        elif v > lim_alto: return "Forte"
        else: return "Normal"
    return "N/A"

def classificar_ciclo_mercado(score: float) -> str:
    """Classifica o ciclo de mercado com base no score técnico."""
    if pd.isna(score): return "Neutro / Transição"
    if score <= 30: return "Pânico / Fundo"
    elif score <= 60: return "Neutro / Transição"
    else: return "Euforia / Topo"

def calcular_dados_ciclo(rsi_val, macd_val, vol_val, vol_mean) -> dict:
    """Calcula o score e classifica o ciclo de mercado a partir dos indicadores."""
    rsi_status = classificar_indicador_tecnico(rsi_val, 30, 70, "RSI")
    macd_status = classificar_indicador_tecnico(macd_val, -0.5, 0.5, "MACD")
    vol_status = classificar_indicador_tecnico(vol_val, vol_mean * 0.8, vol_mean * 1.2, "Volume")

    score_total = 0
    for cls in (rsi_status, macd_status, vol_status):
        if any(key in str(cls) for key in ["Baixo", "Fraco"]): score_total += 10
        elif any(key in str(cls) for key in ["Medio", "Normal"]): score_total += 33
        elif any(key in str(cls) for key in ["Alto", "Forte"]): score_total += 100
    
    score_medio = round(score_total / 3)
    ciclo = classificar_ciclo_mercado(score_medio)
    frase = random.choice(frases_por_ciclo[ciclo])

    return {
        "ciclo_de_mercado": ciclo,
        "status_ciclo": frase["status"],
        "frase_ciclo": f"“{frase['frase']}” — {frase['autor']}"
    }

NOME_EMPRESA_MANUAL = {
    "BRST3": "Brisanet Serviços de Telecomunicações S.A"
}

def fetch_stock_data(ticker_base: str, metadata: dict, vol_mean: float, p_l_externo: str | None) -> dict | None:
    ticker_yf = f"{ticker_base}.SA"
    stock = yf.Ticker(ticker_yf)
    
    try:
        info = stock.info
    except Exception:
        # If yfinance fails, we can't get any indicators.
        return None

    if not info:
        return None

    # Crescimento em 5 anos (mantido)
    hist_5y = stock.history(period="5y")
    growth_price = None
    if not hist_5y.empty and len(hist_5y["Close"]) > 1 and hist_5y["Close"].iloc[0] > 0:
        growth_price = ((hist_5y["Close"].iloc[-1] / hist_5y["Close"].iloc[0]) - 1) * 100

    # Histórico base para técnicos: 1 ano
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
    beta = info.get("beta")
    average_volume = info.get("averageVolume")
    liquidez_media_diaria = average_volume * current_price if average_volume and current_price else None
    free_cash_flow = info.get("freeCashflow")
    fcf_yield = (free_cash_flow / market_cap) * 100 if free_cash_flow and market_cap else None
    current_ratio = info.get("currentRatio")
    empresa = NOME_EMPRESA_MANUAL.get(ticker_base, info.get("longName", metadata.get("empresa")))

    # Adição para Fórmula de Graham
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

    # Adição para Ciclo de Mercado
    dados_ciclo = calcular_dados_ciclo(tecnicos.get('rsi_14_1y'), tecnicos.get('macd_diff_1y'), tecnicos.get('volume_1y'), vol_mean)

    resultado = {
        "ticker": ticker_base,
        "empresa": empresa,
        "subsetor_b3": metadata.get("subsetor_b3"),
        "tipo": metadata.get("tipo"),
        "market_cap": market_cap,
        "logo": metadata.get("logo"),
        "preco_atual": current_price,
        "p_l": p_l_externo,
        "p_vp": info.get("priceToBook"),
        "payout_ratio": payout_ratio * 100 if payout_ratio else None,
        "crescimento_preco_5a": growth_price,
        "roe": roe * 100 if roe else None,
        "divida_total": total_debt,
        "ebitda": ebitda,
        "divida_ebitda": debt_to_ebitda,
        "beta": beta,
        "current_ratio": current_ratio,
        "liquidez_media_diaria": liquidez_media_diaria,
        "fcf_yield": fcf_yield,
        "perfil_acao": classify_stock_profile(current_price, market_cap),
        # Campos para Fórmula de Graham
        "lpa": lpa,
        "vpa": vpa,
        "margem_seguranca_percent": margem_seguranca_percent,

        # Sentimento de Mercado (analistas)
        **get_market_sentiment(stock),

        # Técnicos via ta (1y, 3 colunas)
        **tecnicos,
    }
    # Adiciona os dados do ciclo ao dicionário principal
    resultado.update(dados_ciclo)
    return resultado



def main():
    """
    Função principal para orquestrar a coleta de indicadores e dados de ciclo de mercado.
    """
    # 1. Setup e Impressão Inicial
    print("="*80)
    print("--- Coleta de Indicadores Financeiros (08-indicadores) ---")
    print("="*80)

    if not CAMINHO_ARQUIVO_ENTRADA.exists():
        print(f"[X] ERRO: Arquivo de entrada não encontrado: {CAMINHO_ARQUIVO_ENTRADA}")
        return

    print(f"[>] Lendo tickers de: {CAMINHO_ARQUIVO_ENTRADA}")
    df_input = pd.read_csv(CAMINHO_ARQUIVO_ENTRADA)
    df_input["ticker_norm"] = df_input["ticker"].str.strip().str.upper()
    metadata_map = df_input.set_index("ticker_norm").to_dict(orient="index")
    total_tickers = len(metadata_map)
    print(f"[+] {total_tickers} tickers encontrados.")

    # 2. Coletar P/L para todos os tickers
    print("\n[>] Coletando P/L para todos os tickers...")
    pl_map = {}
    with tqdm(total=total_tickers, desc="Coletando P/L", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
        for ticker_base in metadata_map.keys():
            pl_map[ticker_base] = get_pl_ratio(ticker_base)
            pbar.update(1)
            time.sleep(0.1) # Pausa para evitar rate limiting
    print("[+] P/L coletado para todos os tickers.")

    # 3. Pré-cálculo do volume (saída simplificada)
    print("\n[>] Pré-calculando a média de volume de todos os ativos...")
    all_volumes = []
    # Loop simples, sem tqdm para esta parte
    for ticker_base in metadata_map.keys():
        try:
            hist_1y = yf.Ticker(f"{ticker_base}.SA").history(period=PERIODO_PADRAO_HIST)
            if not hist_1y.empty and 'Volume' in hist_1y.columns:
                all_volumes.append(hist_1y['Volume'].iloc[-1])
        except Exception:
            continue
    vol_mean = pd.Series(all_volumes).mean() if all_volumes else 0
    print("[+] Média de volume calculada.")

    # 4. Loop principal com progresso limpo e tratamento de erros
    print("\n[>] Coletando indicadores fundamentalistas e técnicos...")
    resultados = []
    erros = []
    with tqdm(total=total_tickers, desc="Coletando Indicadores", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
        for ticker_base, meta in metadata_map.items():
            try:
                # Busca o P/L do mapa pré-carregado
                p_l_externo = pl_map.get(ticker_base)
                dados = fetch_stock_data(ticker_base, meta, vol_mean, p_l_externo)
                if dados:
                    resultados.append(dados)
                else:
                    erros.append((ticker_base, "Dados não retornados pelo fetcher"))
            except Exception as e:
                erros.append((ticker_base, str(e).replace('\n', ' ')))
            finally:
                pbar.update(1)
                time.sleep(0.2)  # Pausa para evitar rate limiting

    # 4. Resumo Final
    print("\n" + "="*80)
    print("--- Resumo da Execução ---")

    if not resultados:
        print("[X] ERRO: Nenhum dado foi coletado com sucesso.")
        if erros:
            print(f"    - {len(erros)} tickers falharam durante a coleta.")
        print("="*80)
        return

    # Salvar indicadores.csv
    df_output = pd.DataFrame(resultados)
    df_output.columns = [c.strip().lower().replace(" ", "_") for c in df_output.columns]
    df_output = tratar_dados_para_json(df_output)
    CAMINHO_ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df_output.to_csv(CAMINHO_ARQUIVO_SAIDA, index=False, encoding='utf-8-sig')
    
    print(f"[+] {len(df_output)} tickers processados com sucesso.")
    print(f"    - Arquivo de indicadores salvo em: {CAMINHO_ARQUIVO_SAIDA}")

    # Salvar ciclo_mercado.csv
    CAMINHO_CICLO_MERCADO = DATA_DIR / "ciclo_mercado.csv"
    if 'ticker' in df_output.columns and 'status_ciclo' in df_output.columns:
        df_ciclo = df_output[['ticker', 'status_ciclo']].copy()
        df_ciclo.rename(columns={'status_ciclo': 'status_ciclo'}, inplace=True)
        df_ciclo = tratar_dados_para_json(df_ciclo)
        df_ciclo.to_csv(CAMINHO_CICLO_MERCADO, index=False, encoding='utf-8-sig')
        print(f"    - Arquivo de ciclo de mercado salvo em: {CAMINHO_CICLO_MERCADO}")

    # Imprimir erros, se houver
    if erros:
        print(f"\n[!] {len(erros)} tickers falharam:")
        for ticker, erro in erros[:5]:  # Imprime os 5 primeiros erros para amostragem
             print(f"    - {ticker}: {erro}")
        if len(erros) > 5:
            print("    - ... (e outros)")

    print("\n[+] Processo concluído.")
    print("="*80)


if __name__ == "__main__":
    main()
