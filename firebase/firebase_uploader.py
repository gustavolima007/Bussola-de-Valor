
import os
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

def upload_csv_to_firestore():
    """
    Connects to Firebase and uploads all CSV files from the ../data directory
    to their respective collections in Firestore.
    """
    # --- Conexão com o Firebase ---
    # O caminho para o seu arquivo de credenciais JSON
    cred_path = os.path.join(os.path.dirname(__file__), '..', 'firebase-credentials.json')
    
    # Verifica se o arquivo de credencial existe
    if not os.path.exists(cred_path):
        print(f"Erro: Arquivo de credenciais não encontrado em '{cred_path}'")
        print("Por favor, baixe o arquivo JSON da sua conta de serviço do Firebase,")
        print("renomeie para 'firebase-credentials.json' e coloque na raiz do projeto.")
        return

    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Conexão com o Firebase estabelecida com sucesso.")
    except Exception as e:
        print(f"Erro ao conectar com o Firebase: {e}")
        return

    # --- Leitura e Upload dos CSVs ---
    # Caminho para a pasta de dados
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    # Lista todos os arquivos .csv na pasta de dados
    try:
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if not csv_files:
            print(f"Nenhum arquivo .csv encontrado no diretório '{data_dir}'.")
            return
    except FileNotFoundError:
        print(f"Erro: O diretório de dados '{data_dir}' não foi encontrado.")
        return

    print(f"Arquivos CSV encontrados: {', '.join(csv_files)}\n")

    # Itera sobre cada arquivo CSV
    for file_name in csv_files:
        # Define o nome da coleção (ex: 'acoes_e_fundos.csv' -> 'acoes_e_fundos')
        collection_name = os.path.splitext(file_name)[0]
        file_path = os.path.join(data_dir, file_name)

        print(f"--- Processando '{file_name}' para a coleção '{collection_name}' ---")

        try:
            # Lê o CSV com pandas
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Converte colunas que podem ser problemáticas para tipos nativos do Python
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.to_pydatetime()
                elif pd.api.types.is_numeric_dtype(df[col]):
                    # Converte para tipos nativos para evitar problemas de serialização com numpy types
                    df[col] = df[col].apply(lambda x: int(x) if pd.notna(x) and x == int(x) else float(x) if pd.notna(x) else None)

            # Converte o dataframe para uma lista de dicionários
            records = df.to_dict('records')

            # Faz o upload de cada registro (linha) para o Firestore
            batch = db.batch()
            count = 0
            for record in records:
                # Remove chaves com valores NaN/None para não criar campos vazios no Firestore
                record_cleaned = {k: v for k, v in record.items() if pd.notna(v)}
                doc_ref = db.collection(collection_name).document()
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

if __name__ == '__main__':
    upload_csv_to_firestore()
