
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from loguru import logger

# Configuração do logger
logger.add("supabase/bucket_upload.log", rotation="500 MB", level="INFO")

def main():
    """Script para fazer upload de arquivos CSV para um bucket do Supabase Storage."""
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        logger.error("URL do Supabase ou a Chave não foram definidas no seu arquivo .env")
        return

    try:
        supabase: Client = create_client(url, key)
        logger.info("Conexão com o Supabase estabelecida com sucesso!")
    except Exception as e:
        logger.error(f"Falha ao conectar com o Supabase: {e}")
        return

    bucket_name = "bucket_dw"
    data_path = 'data'
    
    try:
        # Verifica se o bucket existe
        supabase.storage.get_bucket(bucket_name)
        logger.info(f"Bucket '{bucket_name}' encontrado.")
    except Exception as e:
        logger.error(f"Bucket '{bucket_name}' não encontrado ou erro ao acessá-lo: {e}")
        logger.info("Por favor, crie o bucket no seu painel do Supabase antes de executar o script.")
        return

    csv_files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
    logger.info(f"Arquivos CSV encontrados para upload: {csv_files}")

    for file_name in csv_files:
        file_path = os.path.join(data_path, file_name)
        destination_path = f"LAND/{file_name}"  # O nome do arquivo no bucket será o mesmo

        logger.info(f"Enviando {file_name} para o bucket {bucket_name}...")
        try:
            with open(file_path, 'rb') as f:
                supabase.storage.from_(bucket_name).upload(
                    path=destination_path,
                    file=f,
                    file_options={"cache-control": "3600", "upsert": "true"} # Sobrescreve se já existir
                )
            logger.success(f"Arquivo {file_name} enviado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao enviar o arquivo {file_name}: {e}")

if __name__ == "__main__":
    main()
