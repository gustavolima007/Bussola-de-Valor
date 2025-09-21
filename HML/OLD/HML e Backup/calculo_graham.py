# -*- coding: utf-8 -*-
"""
🧪 Script de Teste - Fórmula de Graham

Este script isolado serve para testar a coleta dos dados necessários
para o cálculo do Número de Graham e da Margem de Segurança.

1. Lê os tickers do arquivo 'data/acoes_e_fundos.csv'.
2. Para cada ticker, busca via yfinance:
   - 'trailingEps' (LPA - Lucro por Ação)
   - 'bookValue' (VPA - Valor Patrimonial por Ação) 
   - 'currentPrice' (Preço Atual)
3. Calcula o Número de Graham e a Margem de Segurança.
4. Imprime os resultados na tela para validação.
5. Salva os resultados em um arquivo CSV para análise.
"""

import pandas as pd
import yfinance as yf
from tqdm.auto import tqdm
from pathlib import Path
import numpy as np

# --- Configurações ---
BASE = Path(__file__).resolve().parent.parent / 'data'
CAMINHO_ARQUIVO_ENTRADA = BASE / "acoes_e_fundos.csv"
CAMINHO_ARQUIVO_SAIDA = BASE / "teste_graham_resultados.csv" # Novo arquivo de saída

def calcular_graham(ticker_base: str) -> dict | None:
    """Busca dados, calcula o Número de Graham e retorna um dicionário com os resultados."""
    try:
        ticker_yf = f"{ticker_base}.SA"
        stock = yf.Ticker(ticker_yf)
        info = stock.info

        lpa = info.get("trailingEps")
        vpa = info.get("bookValue")
        preco_atual = info.get("currentPrice")

        # Validação dos dados: LPA e VPA devem ser positivos para a fórmula
        if lpa is None or vpa is None or preco_atual is None or lpa <= 0 or vpa <= 0:
            return None

        # Fórmula de Graham: Valor Intrínseco = Raiz(22.5 * LPA * VPA)
        numero_graham = np.sqrt(22.5 * lpa * vpa)

        # Margem de Segurança = (Valor Intrínseco / Preço Atual) - 1
        margem_seguranca = (numero_graham / preco_atual) - 1

        # Imprime na tela para feedback em tempo real
        print(f"\n--- {ticker_base} ({info.get('longName', 'N/A')}) ---")
        print(f"  Preço Atual: R$ {preco_atual:.2f}")
        print(f"  LPA (Lucro por Ação): R$ {lpa:.2f}")
        print(f"  VPA (Valor Patrimonial por Ação): R$ {vpa:.2f}")
        print(f"  => Número de Graham (Preço Justo): R$ {numero_graham:.2f}")
        print(f"  => Margem de Segurança: {margem_seguranca:.2%}")

        # Retorna os dados para serem salvos no CSV
        return {
            "ticker": ticker_base,
            "empresa": info.get('longName', 'N/A'),
            "preco_atual": preco_atual,
            "lpa": lpa,
            "vpa": vpa,
            "numero_graham": numero_graham,
            "margem_seguranca_percent": margem_seguranca * 100
        }

    except Exception:
        # Ignora erros de tickers não encontrados ou outros problemas de API
        return None

def main():
    df_input = pd.read_csv(CAMINHO_ARQUIVO_ENTRADA)
    
    resultados_graham = []
    for ticker in tqdm(df_input["ticker"].unique(), desc="Calculando Graham"):
        dados = calcular_graham(ticker.strip().upper())
        if dados:
            resultados_graham.append(dados)

    if not resultados_graham:
        print("\n⚠️ Nenhum dado válido foi calculado. O arquivo CSV não será gerado.")
        return

    # Converte a lista de dicionários em um DataFrame e arredonda os valores
    df_output = pd.DataFrame(resultados_graham).round(2)
    df_output.to_csv(CAMINHO_ARQUIVO_SAIDA, index=False, encoding='utf-8-sig', float_format='%.2f')
    print(f"\n✅ Resultados salvos com sucesso em: {CAMINHO_ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()