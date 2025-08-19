import pandas as pd
import yfinance as yf
from datetime import date
import warnings
import os
from tqdm.auto import tqdm
# Lê a lista de tickers em ../data/acoes_e_fundos.csv, baixa preços ajustados no yfinance,
# gera: (1) tabela anual dos últimos 7 anos e (2) tabela resumida com fechamento atual;
# salva em ../data/precos_acoes_completo.csv e ../data/precos_acoes.csv.

# Ignorar avisos futuros
warnings.simplefilter(action='ignore', category=FutureWarning)

def ler_tickers_do_csv(caminho_do_arquivo: str, coluna_ticker: str = 'ticker') -> list:
    """Lê um arquivo CSV e extrai uma lista de tickers únicos."""
    try:
        caminho_do_arquivo = os.path.normpath(caminho_do_arquivo)
        df = pd.read_csv(caminho_do_arquivo)
        if coluna_ticker not in df.columns:
            print(f"Erro: A coluna '{coluna_ticker}' não foi encontrada no arquivo.")
            print(f"Colunas disponíveis: {list(df.columns)}")
            return []
        return df[coluna_ticker].dropna().unique().tolist()
    except FileNotFoundError:
        print(f"\n❌ Erro ao localizar o arquivo CSV:")
        print(f"O caminho definido é inválido ou o arquivo não existe:\n'{caminho_do_arquivo}'")
        print("\n🔍 Verifique se:")
        print("• O arquivo realmente existe nesse local.")
        print("• O caminho está correto e compatível com seu sistema operacional.")
        return []
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        return []

def gerar_tabela_comparativa_precos(lista_tickers: list, anos_anteriores: int = 7) -> tuple[pd.DataFrame, pd.DataFrame] | tuple[None, None]:
    """Busca o preço de fechamento ajustado para uma lista de tickers."""
    try:
        tickers_sa = [t.upper() if t.upper().endswith('.SA') else f"{t.upper()}.SA" for t in lista_tickers]
        hoje = date.today()
        ano_inicio = hoje.year - anos_anteriores

        print(f"Baixando dados históricos de {len(tickers_sa)} ativos...")
        hist = yf.download(tickers_sa, start=f"{ano_inicio}-01-01", end=hoje, auto_adjust=True, progress=False)

        if hist.empty:
            print("Nenhum dado histórico foi encontrado.")
            return None, None

        df_closes = hist['Close']
        lista_completa, lista_resumida = [], []

        for ticker, ticker_sa in tqdm(list(zip(lista_tickers, tickers_sa)), desc="Processando preços por ticker"):
            col = df_closes.get(ticker_sa)
            if col is None or col.dropna().empty:
                print(f"Aviso: Não foram encontrados dados para o ticker {ticker}. Pulando.")
                continue

            fechamento_atual = col.iloc[-1]
            lista_resumida.append({'ticker': ticker, 'fechamento_atual': fechamento_atual})
            lista_completa.append({'ticker': ticker, 'ano': hoje.year, 'fechamento': fechamento_atual})

            for j in range(anos_anteriores):
                ano_alvo = hoje.year - (j + 1)
                try:
                    fechamento_ano = df_closes.loc[str(ano_alvo), ticker_sa].dropna().iloc[-1]
                except (KeyError, IndexError):
                    fechamento_ano = None
                lista_completa.append({'ticker': ticker, 'ano': ano_alvo, 'fechamento': fechamento_ano})

        if not lista_completa:
            print("Nenhum resultado foi processado com sucesso.")
            return None, None

        df_completo = pd.DataFrame(lista_completa)
        df_resumido = pd.DataFrame(lista_resumida).set_index('ticker')
        return df_completo, df_resumido

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None, None

# --- BLOCO DE EXECUÇÃO PRINCIPAL ---

csv_path = "../data/acoes_e_fundos.csv"
output_folder = "../data"

if csv_path:
    csv_path = os.path.normpath(csv_path)
    print(f"Usando arquivo: {csv_path}")
    ativos_alvo = ler_tickers_do_csv(csv_path)

    if ativos_alvo:
        print(f"Processando {len(ativos_alvo)} ativos encontrados no arquivo: {', '.join(ativos_alvo[:5])}...")
        anos_para_analise = 7
        tabela_completa, tabela_resumida = gerar_tabela_comparativa_precos(ativos_alvo, anos_anteriores=anos_para_analise)

        if tabela_completa is not None and tabela_resumida is not None:
            print("\n--- Exibição Resumida (5 primeiras linhas) ---")
            tabela_exibicao = tabela_resumida.head(5).copy()
            tabela_exibicao['fechamento_atual'] = tabela_exibicao['fechamento_atual'].apply(
                lambda x: f"R$ {x:.2f}" if pd.notna(x) else "N/D"
            )
            print(tabela_exibicao.to_string())

            output_folder = os.path.normpath(output_folder)
            os.makedirs(output_folder, exist_ok=True)

            output_path_completo = os.path.join(output_folder, "precos_acoes_completo.csv")
            tabela_completa['fechamento'] = tabela_completa['fechamento'].round(2)
            tabela_completa.to_csv(output_path_completo, index=False)
            print(f"\n✅ Tabela completa salva em: {output_path_completo}")

            output_path_resumido = os.path.join(output_folder, "precos_acoes.csv")
            tabela_resumida.round(2).to_csv(output_path_resumido)
            print(f"✅ Tabela resumida salva em: {output_path_resumido}")

            print(f"\n📊 Estatísticas:")
            print(f"   • Total de ativos processados: {len(tabela_resumida)}")
            print(f"   • Período analisado: {anos_para_analise} anos")
            print(f"   • Total de registros na tabela completa: {len(tabela_completa)}")
            print(f"   • Data de execução: {date.today().strftime('%d/%m/%Y')}")

        else:
            print("Não foi possível gerar as tabelas de preços.")
    else:
        print("Nenhum ativo para processar. Verifique o conteúdo do arquivo CSV.")
else:
    print("❌ ERRO: Caminho ../data/acoes_e_fundos.csv não encontrado.")
    print("Verifique se o arquivo existe na pasta ../data.")
