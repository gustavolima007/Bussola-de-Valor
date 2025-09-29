
import os
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
from tqdm import tqdm

def upload_collections_from_csvs(db):
    """
    Connects to Firebase and uploads all CSV files from the ../data directory
    to their respective collections in Firestore.
    """
    # --- Conexão com o Firebase ---
    # O caminho para o seu arquivo de credenciais JSON
    cred_path = os.path.join(os.path.dirname(__file__), '..', 'firebase-credentials.json')

    # --- Leitura e Upload dos CSVs ---
    # Caminho para a pasta de dados
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    # Lista todos os arquivos .csv na pasta de dados
    try:
        # Exclui o arquivo 'ativos' da lista de upload individual
        # pois ele será criado a partir da junção de outros
        files_to_exclude = [
            'acoes_e_fundos.csv', 'indicadores.csv', 'dividend_yield.csv',
            'preco_teto.csv', 'precos_acoes.csv', 'scores.csv'
        ]
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and f not in files_to_exclude]

        if not csv_files:
            print(f"Nenhum arquivo .csv encontrado no diretório '{data_dir}'.")
            return
    except FileNotFoundError:
        print(f"Erro: O diretório de dados '{data_dir}' não foi encontrado.")
        return

    print(f"Arquivos CSV encontrados: {', '.join(csv_files)}\n")

    # Itera sobre cada arquivo CSV para upload direto
    for file_name in csv_files:
        # Define o nome da coleção (ex: 'acoes_e_fundos.csv' -> 'acoes_e_fundos')
        collection_name = os.path.splitext(file_name)[0]
        file_path = os.path.join(data_dir, file_name)

        print(f"--- Processando '{file_name}' para a coleção '{collection_name}' ---")

        try:
            # Lê o CSV com pandas
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Substitui NaN por None para compatibilidade com Firestore
            df = df.replace({np.nan: None})

            # Converte o dataframe para uma lista de dicionários
            records = df.to_dict(orient='records')

            # Faz o upload de cada registro (linha) para o Firestore
            batch = db.batch()
            count = 0
            for record in records:
                # Remove chaves com valores NaN/None para não criar campos vazios no Firestore
                record_cleaned = {k: v for k, v in record.items() if pd.notna(v)}
                doc_ref = db.collection(collection_name).document() # ID automático
                batch.set(doc_ref, record_cleaned)
                count += 1
                # O Firestore tem um limite de 500 operações por batch
                if count % 499 == 0:
                    batch.commit()
                    batch = db.batch()
                    print(f"  {count} registros enviados...")
            
            batch.commit() # Envia o restante
            print(f"Upload concluído: {len(records)} registros foram adicionados à coleção '{collection_name}'.")

        except Exception as e:
            print(f"  Erro ao processar o arquivo '{file_name}': {e}")
        
        print("-" * (len(file_name) + 30) + "\n")

def build_and_upload_ativos_collection(db):
    """
    Builds a consolidated 'ativos' collection by merging multiple CSVs
    and uploads it to Firestore, using the ticker as the document ID.
    """
    print("\n--- Construindo e enviando a coleção 'ativos' consolidada ---")
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

    try:
        # Carrega os CSVs principais
        df_base = pd.read_csv(os.path.join(data_dir, 'acoes_e_fundos.csv'))
        df_indicadores = pd.read_csv(os.path.join(data_dir, 'indicadores.csv'))
        df_dy = pd.read_csv(os.path.join(data_dir, 'dividend_yield.csv'))
        df_teto = pd.read_csv(os.path.join(data_dir, 'preco_teto.csv'))
        df_precos = pd.read_csv(os.path.join(data_dir, 'precos_acoes.csv'))
        df_scores = pd.read_csv(os.path.join(data_dir, 'scores.csv'))

        # Merge dos dataframes
        df = df_base.merge(df_indicadores, on='ticker', how='left', suffixes=('', '_indic'))
        df = df.merge(df_dy, on='ticker', how='left', suffixes=('', '_dy'))
        df = df.merge(df_teto, on='ticker', how='left', suffixes=('', '_teto'))
        df = df.merge(df_precos, on='ticker', how='left', suffixes=('', '_precos'))
        df = df.merge(df_scores, left_on='ticker', right_on='ticker_base', how='left', suffixes=('', '_scores'))

        # Substitui NaN por None
        df = df.replace({np.nan: None})

        batch = db.batch()
        count = 0
        
        # Itera sobre o dataframe consolidado
        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Enviando ativos"):
            ticker = row['ticker']
            if not ticker or pd.isna(ticker):
                continue

            # Monta o documento aninhado
            doc_data = {
                'ticker': row.get('ticker'),
                'empresa': row.get('empresa'),
                'setorB3': row.get('setor_b3'),
                'subsetorB3': row.get('subsetor_b3'),
                'tipo': row.get('tipo'),
                'logo': row.get('logo'),
                'marketCap': row.get('market_cap'),
                'pL': row.get('p_l'),
                'pVP': row.get('p_vp'),
                'payoutRatio': row.get('payout_ratio'),
                'crescimentoPreco5A': row.get('crescimento_preco_5a'),
                'roe': row.get('roe'),
                'dividaTotal': row.get('divida_total'),
                'ebitda': row.get('ebitda'),
                'dividaEbitda': row.get('divida_ebitda'),
                'beta': row.get('beta'),
                'currentRatio': row.get('current_ratio'),
                'liquidezMediaDiaria': row.get('liquidez_media_diaria'),
                'fcfYield': row.get('fcf_yield'),
                'perfilAcao': row.get('perfil_acao'),
                'lpa': row.get('lpa'),
                'vpa': row.get('vpa'),
                'margemSegurancaPercent': row.get('margem_seguranca_percent'),
                'recomendacoes': {
                    'sentimentoGauge': row.get('sentimento_gauge'),
                    'strongBuy': row.get('strong_buy'),
                    'buy': row.get('buy'),
                    'hold': row.get('hold'),
                    'sell': row.get('sell'),
                    'strongSell': row.get('strong_sell'),
                },
                'tecnicos': {
                    'rsi14_1y': row.get('rsi_14_1y'),
                    'macdDiff1y': row.get('macd_diff_1y'),
                    'volume1y': row.get('volume_1y'),
                },
                'cicloMercado': {
                    'ciclo': row.get('ciclo_de_mercado'),
                    'status': row.get('status_ciclo'),
                    'frase': row.get('frase_ciclo'),
                },
                'precos': {
                    'atual': row.get('fechamento_atual'),
                    'umMesAtras': row.get('fechamento_1M_atras'),
                    'seisMesesAtras': row.get('fechamento_6M_atras'),
                },
                'dividendYield': {
                    'dy5Anos': row.get('DY5anos'),
                    'dy12M': row.get('DY12M'),
                },
                'precoTeto': {
                    'precoTeto5Anos': row.get('preco_teto_5anos'),
                    'diferencaPercentual': row.get('diferenca_percentual'),
                },
                'scores': {
                    'total': row.get('score_total'),
                    'dy': row.get('score_dy'),
                    'payout': row.get('score_payout'),
                    'roe': row.get('score_roe'),
                    'plPvp': row.get('score_pl_pvp'),
                    'divida': row.get('score_divida'),
                    'crescimentoSentimento': row.get('score_crescimento_sentimento'),
                    'cicloMercado': row.get('score_ciclo_mercado'),
                    'graham': row.get('score_graham'),
                    'beta': row.get('score_beta'),
                    'marketCap': row.get('score_market_cap'),
                    'liquidez': row.get('score_liquidez'),
                    'fcfYield': row.get('score_fcf_yield'),
                }
            }
            
            # Define o documento na coleção 'ativos' com o ticker como ID
            doc_ref = db.collection('ativos').document(ticker)
            batch.set(doc_ref, doc_data)
            count += 1
            if count % 499 == 0:
                batch.commit()
                batch = db.batch()
        
        batch.commit()
        print(f"Upload concluído: {count} documentos foram adicionados/atualizados na coleção 'ativos'.")

    except FileNotFoundError as e:
        print(f"Erro: Arquivo necessário para a coleção 'ativos' não encontrado: {e}")
    except Exception as e:
        print(f"Erro ao construir a coleção 'ativos': {e}")

if __name__ == '__main__':
    cred_path = os.path.join(os.path.dirname(__file__), '..', 'firebase-credentials.json')
    if not os.path.exists(cred_path):
        print(f"Erro: Arquivo de credenciais não encontrado em '{cred_path}'")
        exit()

    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Conexão com o Firebase estabelecida com sucesso.")
        
        # Executa os uploads
        upload_collections_from_csvs(db)
        build_and_upload_ativos_collection(db)

    except Exception as e:
        print(f"Erro geral na execução: {e}")
