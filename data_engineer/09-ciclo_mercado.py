# -*- coding: utf-8 -*-
"""
Script para Geração de Dados de Ciclo de Mercado para Todos os Ativos

Este script utiliza a lógica de análise técnica (RSI, MACD, Volume) para
classificar o ciclo de mercado de cada ativo listado no arquivo 
`acoes_e_fundos.csv`.

O processo consiste em:
1.  Carregar a lista completa de tickers.
2.  Para cada ticker:
    a. Baixar o histórico de preços usando o yfinance.
    b. Calcular os indicadores RSI, MACD e Volume.
    c. Gerar um score baseado nesses indicadores.
    d. Classificar o ciclo de mercado (Pânico, Neutro, Euforia).
    e. Determinar o status (Compra, Venda, Observação).
3.  Consolidar os resultados.
4.  Salvar o DataFrame resultante no arquivo `data/ciclo_mercado.csv`.
"""

import yfinance as yf
import pandas as pd
import ta
import random
from tqdm import tqdm
from common import DATA_DIR, get_tickers

# --- Configuração de Caminhos ---
INPUT_FILE = DATA_DIR / "acoes_e_fundos.csv"
OUTPUT_FILE = DATA_DIR / "ciclo_mercado.csv"

# --- Lógica de Análise (Adaptada de HML/ciclo.py) ---

# Frases por ciclo de mercado (usado para determinar o status)
frases_por_ciclo = {
    "Pânico / Fundo": [{"status": "Compra"}],
    "Neutro / Transição": [{"status": "Observação"}],
    "Euforia / Topo": [{"status": "Venda"}]
}

def classificar(valor, lim_baixo, lim_alto, tipo):
    """Classifica um valor numérico em categorias."""
    valor = float(valor)
    if tipo == "RSI":
        if valor < lim_baixo: return "📉 Baixo"
        elif valor > lim_alto: return "📈 Alto"
        else: return "📊 Médio"
    elif tipo == "MACD":
        if valor < lim_baixo: return "🐻 Baixa"
        elif valor > lim_alto: return "🐂 Alta"
        else: return "⚖️ Neutra"
    elif tipo == "Volume":
        if valor < lim_baixo: return "🪙 Fraco"
        elif valor > lim_alto: return "🏦 Forte"
        else: return "💰 Normal"

def analisar_indicadores(df):
    """Calcula e analisa os indicadores técnicos de um DataFrame de preços."""
    if df.empty or len(df) < 30:  # Requer dados suficientes
        return None

    close = df['Close'].dropna()
    volume = df['Volume'].dropna()

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    if close.empty or volume.empty:
        return None

    try:
        rsi = ta.momentum.RSIIndicator(close=close).rsi()
        macd = ta.trend.MACD(close=close).macd_diff()
        vol_mean = float(volume.mean())

        if rsi.empty or macd.empty:
            return None

        rsi_val = float(rsi.iloc[-1])
        macd_val = float(macd.iloc[-1])
        vol_val = float(volume.iloc[-1])

        rsi_status = classificar(rsi_val, 30, 70, "RSI")
        macd_status = classificar(macd_val, -0.5, 0.5, "MACD")
        vol_status = classificar(vol_val, vol_mean * 0.8, vol_mean * 1.2, "Volume")

        return {
            "RSI (Sentimento)": {"valor": rsi_val, "classificacao": rsi_status},
            "MACD (Tendência)": {"valor": macd_val, "classificacao": macd_status},
            "Volume (Convicção)": {"valor": vol_val, "classificacao": vol_status}
        }
    except Exception:
        return None

def classificar_ciclo(score):
    """Classifica o ciclo de mercado com base no score."""
    if score <= 30: return "Pânico / Fundo"
    elif score <= 60: return "Neutro / Transição"
    else: return "Euforia / Topo"

def main():
    """
    Orquestra a geração do arquivo ciclo_mercado.csv.
    """
    tickers = get_tickers()
    if not tickers:
        print("Nenhum ticker encontrado. Abortando.")
        return

    tabela_consolidada = []
    
    print("Analisando ciclo de mercado para cada ticker...")
    for ticker in tqdm(tickers, desc="Analisando Tickers"):
        try:
            # Adiciona .SA para compatibilidade com yfinance
            ticker_yf = f"{ticker}.SA"
            df_yf = yf.download(ticker_yf, period="1y", progress=False)

            if df_yf.empty:
                # print(f"AVISO: Nenhum dado baixado para {ticker_yf}. Pulando.")
                continue

            indicadores = analisar_indicadores(df_yf)
            if not indicadores:
                # print(f"AVISO: Não foi possível calcular indicadores para {ticker_yf}. Pulando.")
                continue

            score_total = 0
            for indicador in indicadores.values():
                class_str = indicador["classificacao"]
                if "Baixo" in class_str or "Fraco" in class_str or "🐻" in class_str:
                    score_total += 10
                elif "Médio" in class_str or "Normal" in class_str or "⚖️" in class_str:
                    score_total += 33
                elif "Alto" in class_str or "Forte" in class_str or "🐂" in class_str:
                    score_total += 100
            
            score_medio = round(score_total / 3)
            ciclo = classificar_ciclo(score_medio)
            status = random.choice(frases_por_ciclo[ciclo])["status"]

            tabela_consolidada.append({
                "ticker": ticker,
                "score_ciclo": score_medio,
                "ciclo_mercado": ciclo,
                "Status 🟢🔴": status,
            })

        except Exception as e:
            print(f"ERRO: Exceção inesperada ao processar {ticker}: {e}")
            # Ignora erros para tickers individuais para não parar o processo
            continue
            
    if not tabela_consolidada:
        print("Nenhum dado de ciclo de mercado pôde ser gerado.")
        return

    df_final = pd.DataFrame(tabela_consolidada)
    
    # Salva o arquivo
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\nArquivo gerado com sucesso em: {OUTPUT_FILE}")
    print(f"Total de tickers processados: {len(df_final)}")

if __name__ == "__main__":
    main()
