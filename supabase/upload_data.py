
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions
from loguru import logger

# Configuração do logger
logger.add("supabase/upload.log", rotation="500 MB", level="INFO")

def get_csv_files(data_path='data'):
    """Lista todos os arquivos CSV no diretório de dados."""
    csv_files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
    logger.info(f"Arquivos CSV encontrados: {csv_files}")
    return csv_files

def upload_to_supabase(supabase: Client, table_name: str, data: list):
    """Faz o upload dos dados para uma tabela do Supabase."""
    try:
        logger.info(f"Iniciando upload para a tabela: {table_name}...")
        # O Supabase pode ter um limite no número de registros por chamada (ex: 1000)
        # Divida os dados em lotes se necessário.
        batch_size = 500
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            response = supabase.table(table_name).upsert(batch)
            # response = supabase.table(table_name).insert(batch).execute()
            logger.info(f"Lote {i//batch_size + 1} enviado para {table_name}. ")
        logger.success(f"Upload para a tabela {table_name} concluído com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao fazer upload para a tabela {table_name}: {e}")

def main():
    """Script principal para ler CSVs e fazer upload para o Supabase."""
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        logger.error("URL do Supabase ou a Chave não foram definidas no seu arquivo .env")
        return

    try:
        options = ClientOptions(schema="dw")
        supabase: Client = create_client(url, key, options=options)
        logger.info("Conexão com o Supabase estabelecida com sucesso!")
    except Exception as e:
        logger.error(f"Falha ao conectar com o Supabase: {e}")
        return

    csv_files = get_csv_files()
    data_path = 'data'

    for file_name in csv_files:
        table_name = os.path.splitext(file_name)[0]
        file_path = os.path.join(data_path, file_name)

        logger.info(f"Processando arquivo: {file_path}")
        try:
            df = pd.read_csv(file_path)
            # Converte colunas de data se existirem
            for col in df.columns:
                if 'date' in col.lower() or 'data' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S%z')
                    except Exception:
                        pass # Ignora erros de conversão
            
            # Substitui valores NaN/NaT por None (NULL no banco)
            df = df.where(pd.notnull(df), None)

            data_to_upload = df.to_dict(orient='records')

            if data_to_upload:
                upload_to_supabase(supabase, table_name, data_to_upload)
            else:
                logger.warning(f"Arquivo {file_name} está vazio. Nada para enviar.")

        except Exception as e:
            logger.error(f"Erro ao processar o arquivo {file_name}: {e}")

if __name__ == "__main__":
    main()
