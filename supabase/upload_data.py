import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions
from loguru import logger
import numpy as np

# Configure logger for a summarized output
logger.remove()
logger.add(lambda msg: print(msg, end=""), format="{message}", level="INFO")
logger.add("supabase/upload.log", rotation="500 MB", level="DEBUG") # Detailed log file

def get_csv_files(data_path='data'):
    return [f for f in os.listdir(data_path) if f.endswith('.csv')]

def truncate_tables(supabase: Client):
    logger.info("🗑️  Iniciando limpeza das tabelas (truncate)...\n")
    table_key_map = {
        "acoes_e_fundos": "ticker", "ciclo_mercado": "ticker", "dividendos_ano": "ticker",
        "dividendos_ano_resumo": "ticker", "dividend_yield": "ticker", "indicadores": "ticker",
        "indices": "index", "precos_acoes": "ticker", "precos_acoes_completo": "ticker",
        "preco_teto": "ticker", "rj": "nome", "scores": "ticker_base",
        "tickers_nao_mapeados": "ticker", "todos_dividendos": "ticker", "avaliacao_setor": "setor_b3",
    }
    errors = []
    for table, key_column in table_key_map.items():
        try:
            supabase.table(table).delete().neq(key_column, 'a-dummy-value-that-will-never-exist').execute()
        except Exception as e:
            errors.append((table, e))

    if not errors:
        logger.info("✅ Todas as tabelas foram limpas com sucesso.\n")
    else:
        logger.error("❌ Erro ao limpar as seguintes tabelas:")
        for table, e in errors:
            logger.error(f"   - {table}: {e}")
        logger.info("\n")

def upload_to_supabase(supabase: Client, table_name: str, data: list) -> bool:
    try:
        batch_size = 500
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            supabase.table(table_name).insert(batch).execute()
        return True
    except Exception as e:
        logger.error(f"    ❌ Erro ao fazer upload para a tabela {table_name}: {e}")
        return False

def main():
    load_dotenv()
    logger.info("🚀 Iniciando script de upload para o Supabase...\n")

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        logger.error("❌ URL do Supabase ou a Chave não foram definidas no .env")
        return

    try:
        options = ClientOptions(schema="land_dw")
        supabase = create_client(url, key, options=options)
        logger.info("🔗 Conexão com o Supabase estabelecida com sucesso.")
    except Exception as e:
        logger.error(f"❌ Falha ao conectar com o Supabase: {e}")
        return

    truncate_tables(supabase)

    csv_files = get_csv_files()
    data_path = 'data'
    results = []

    logger.info("\n📤 Iniciando upload dos arquivos CSV...\n")
    for file_name in sorted(csv_files):
        table_name = os.path.splitext(file_name)[0]
        file_path = os.path.join(data_path, file_name)
        
        try:
            if table_name == 'tickers_nao_mapeados':
                df = pd.read_csv(file_path, header=None, names=['ticker'])
            else:
                df = pd.read_csv(file_path)

            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
            
            data_to_upload = df.to_dict(orient='records')

            if data_to_upload:
                logger.info(f"  - Processando: {file_name:<30}")
                success = upload_to_supabase(supabase, table_name, data_to_upload)
                results.append({'file': file_name, 'status': '✅ Sucesso' if success else '❌ Falha'})
            else:
                results.append({'file': file_name, 'status': '⚠️ Vazio'})

        except Exception as e:
            logger.error(f"    ❌ Erro ao processar o arquivo {file_name}: {e}")
            results.append({'file': file_name, 'status': '❌ Erro no processamento'})

    logger.info("\n\n📋 Resumo do Upload:\n" + "="*30)
    for res in results:
        logger.info(f"  - {res['file']:<30} {res['status']}")
    logger.info("="*30 + "\n\n✨ Script concluído!\n")

if __name__ == "__main__":
    main()
