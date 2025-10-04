# -*- coding: utf-8 -*-
"""
📈 Script para Coleta de Preços Históricos de Ações

Este script busca os preços de fechamento ajustados de uma lista de tickers
da B3, utilizando a biblioteca yfinance, e gera dois arquivos de saída em Parquet:

1.  `precos_acoes_completo.parquet`: Contém o preço de fechamento do último dia
    de cada ano para os últimos 7 anos.
2.  `precos_acoes.parquet`: Um resumo com o preço atual e de 1 e 6 meses atrás.

Etapas do Processo:
- Lê a lista de tickers do arquivo Parquet.
- Adiciona o sufixo '.SA' aos tickers para consulta no yfinance.
- Baixa o histórico de preços dos últimos 7 anos.
- Processa os dados para extrair os preços de fechamento anuais e o atual/mensal.
- Salva os dois DataFrames resultantes em arquivos Parquet.
"""

import pandas as pd
import yfinance as yf
from datetime import date
import warnings
from pathlib import Path
from tqdm.auto import tqdm
from common import get_tickers, save_to_parquet

# Ignora avisos de FutureWarning para manter o output limpo
warnings.simplefilter(action='ignore', category=FutureWarning)

def gerar_tabela_comparativa_precos(lista_tickers: list, anos_anteriores: int = 7) -> tuple[pd.DataFrame, pd.DataFrame] | tuple[None, None]:
    """
    Busca o preço de fechamento ajustado para uma lista de tickers e gera duas tabelas:
    uma completa com dados anuais e uma resumida com o preço atual e mensal.

    Args:
        lista_tickers (list): A lista de tickers a serem processados.
        anos_anteriores (int): O número de anos a serem analisados no histórico.

    Returns:
        tuple: Uma tupla contendo o DataFrame completo e o DataFrame resumido.
               Retorna (None, None) se ocorrer um erro.
    """
    try:
        # Adiciona o sufixo .SA para compatibilidade com o yfinance
        tickers_sa = [f"{t.upper()}.SA" for t in lista_tickers]
        hoje = date.today()
        ano_inicio = hoje.year - anos_anteriores

        # Define as datas de referência para 1 e 6 meses atrás
        data_1_mes_atras = pd.to_datetime(hoje) - pd.DateOffset(months=1)
        data_6_meses_atras = pd.to_datetime(hoje) - pd.DateOffset(months=6)

        print(f"ℹ️ Baixando dados para {len(tickers_sa)} ativos...")
        # Baixa os dados de uma vez para otimizar as requisições
        hist = yf.download(tickers_sa, start=f"{ano_inicio}-01-01", end=hoje, auto_adjust=True, progress=False)

        if hist.empty:
            print("⚠️ Nenhum dado histórico retornado pelo yfinance.")
            return None, None

        df_closes = hist['Close']
        lista_completa, lista_resumida = [], []

        # Itera sobre os tickers para processar os preços
        for ticker, ticker_sa in tqdm(list(zip(lista_tickers, tickers_sa)), desc="📈 Processando preços por ticker"):
            col = df_closes.get(ticker_sa)
            if col is None or col.dropna().empty:
                print(f"⚠️ Nenhum dado para {ticker}. Pulando.")
                continue

            # Preço de fechamento mais recente
            fechamento_atual = col.dropna().iloc[-1]

            # Busca os preços de 1 e 6 meses atrás usando .asof()
            fechamento_1M_atras = col.asof(data_1_mes_atras)
            fechamento_6M_atras = col.asof(data_6_meses_atras)

            # Adiciona os novos campos ao dicionário da lista resumida
            lista_resumida.append({
                'ticker': ticker,
                'fechamento_atual': fechamento_atual,
                'fechamento_1m_atras': fechamento_1M_atras,
                'fechamento_6m_atras': fechamento_6M_atras
            })
            
            lista_completa.append({'ticker': ticker, 'ano': hoje.year, 'fechamento': fechamento_atual})

            # Preços de fechamento dos anos anteriores
            for j in range(anos_anteriores):
                ano_alvo = hoje.year - (j + 1)
                try:
                    fechamento_ano = df_closes.loc[str(ano_alvo), ticker_sa].dropna().iloc[-1]
                except (KeyError, IndexError):
                    fechamento_ano = None
                lista_completa.append({'ticker': ticker, 'ano': ano_alvo, 'fechamento': fechamento_ano})

        if not lista_completa:
            print("❌ Nenhum resultado processado.")
            return None, None

        # Cria os DataFrames a partir das listas
        df_completo = pd.DataFrame(lista_completa)
        df_resumido = pd.DataFrame(lista_resumida) # Não setar o index aqui
        return df_completo, df_resumido

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None, None

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    print("Iniciando coleta de preços...")
    ativos_alvo = get_tickers()

    if ativos_alvo:
        print(f"ℹ️ Processando {len(ativos_alvo)} ativos. Amostra: {ativos_alvo[:5]}...")
        anos_para_analise = 7
        tabela_completa, tabela_resumida = gerar_tabela_comparativa_precos(ativos_alvo, anos_anteriores=anos_para_analise)

        if tabela_completa is not None and tabela_resumida is not None:
            
            # Salva a tabela completa
            tabela_completa['fechamento'] = tabela_completa['fechamento'].round(2)
            save_to_parquet(tabela_completa, "precos_acoes_completo")

            # Salva a tabela resumida
            tabela_resumida['fechamento_atual'] = tabela_resumida['fechamento_atual'].round(2)
            tabela_resumida['fechamento_1m_atras'] = tabela_resumida['fechamento_1m_atras'].round(2)
            tabela_resumida['fechamento_6m_atras'] = tabela_resumida['fechamento_6m_atras'].round(2)
            save_to_parquet(tabela_resumida, "precos_acoes")

            print(f"\n✅ Coleta de preços concluída:")
            print(f"   - Ativos: {len(tabela_resumida)}")
            print(f"   - Período: {anos_para_analise} anos")
            print(f"   - Registros: {len(tabela_completa)}")
            print(f"   - Data: {date.today().strftime('%d/%m/%Y')}")
        else:
            print("\n❌ Falha ao gerar tabelas de preços.")
    else:
        print("\n⚠️ Nenhum ativo para processar. Verifique a execução de '01-acoes_e_fundos.py'.")