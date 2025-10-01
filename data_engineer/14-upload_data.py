import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions
from loguru import logger
import numpy as np
from pathlib import Path

# Configure logger for a summarized output
LOG_DIR = Path(__file__).resolve().parent.parent / 'supabase'
LOG_FILE = LOG_DIR / 'upload.log'
LOG_DIR.mkdir(parents=True, exist_ok=True)
logger.remove()
logger.add(lambda msg: print(msg, end=""), format="{message}", level="INFO")
logger.add(LOG_FILE, rotation="500 MB", level="DEBUG") # Detailed log file

def get_csv_files(data_path='data'):
    return [f for f in os.listdir(data_path) if f.endswith('.csv')]

def truncate_tables(supabase: Client):
    logger.info("🗑️  Iniciando limpeza das tabelas (truncate)...\n")
    
    # Mapa de tabelas com uma coluna chave e um valor dummy do tipo correto.
    table_key_map = {
        # Tabelas com chave primária/referência de texto
        "scores": ("ticker_base", "dummy_text"),
        "precos_acoes": ("ticker", "dummy_text"),
        "preco_teto": ("ticker", "dummy_text"),
        "indicadores": ("ticker", "dummy_text"),
        "dividendos_ano_resumo": ("ticker", "dummy_text"),
        "dividend_yield": ("ticker", "dummy_text"),
        "ciclo_mercado": ("ticker", "dummy_text"),
        "acoes_e_fundos": ("ticker", "dummy_text"),

        # Tabelas com chave primária/referência numérica (SERIAL)
        "todos_dividendos": ("id", -1),
        "precos_acoes_completo": ("id", -1),
        "dividendos_ano": ("id", -1),
        "rj": ("id", -1),
        "tickers_nao_mapeados": ("id", -1),
        "avaliacao_setor": ("id", -1),
        "indices": ("id", -1),
    }

    # A ordem de deleção é definida aqui para respeitar as foreign keys
    ordered_tables = [
        "todos_dividendos", "scores", "precos_acoes_completo", "precos_acoes",
        "preco_teto", "indicadores", "dividendos_ano_resumo", "dividendos_ano",
        "dividend_yield", "ciclo_mercado", "rj", "tickers_nao_mapeados",
        "avaliacao_setor", "indices",
        # 'acoes_e_fundos' deve ser a última
        "acoes_e_fundos"
    ]

    errors = []
    for table in ordered_tables:
        try:
            # Checa se a tabela existe no mapa antes de usar
            if table in table_key_map:
                key_column, dummy_value = table_key_map[table]
                supabase.table(table).delete().neq(key_column, dummy_value).execute()
            else:
                logger.warning(f"   - Tabela '{table}' não encontrada no mapa de chaves para truncate. Pulando.")

        except Exception as e:
            errors.append((table, e.response.json() if hasattr(e, 'response') else str(e)))

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
        logger.error(f"    ❌ Erro ao fazer upload para a tabela {table_name}: {e.response.json() if hasattr(e, 'response') else str(e)}")
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
        logger.info("🔗 Conexão com o Supabase estabelecida com sucesso.\n")
    except Exception as e:
        logger.error(f"❌ Falha ao conectar com o Supabase: {e}")
        return

    truncate_tables(supabase)

    csv_files = get_csv_files()
    data_path = 'data'
    results = []

    logger.info("\n📤 Iniciando upload dos arquivos CSV...\n")
    # Garante que acoes_e_fundos seja processado primeiro para satisfazer as FKs
    ordered_files = sorted(csv_files, key=lambda x: (x != 'acoes_e_fundos.csv', x))

    for file_name in ordered_files:
        table_name = os.path.splitext(file_name)[0]
        file_path = os.path.join(data_path, file_name)
        
        try:
            if table_name == 'tickers_nao_mapeados':
                df = pd.read_csv(file_path, header=None, names=['ticker'])
            else:
                df = pd.read_csv(file_path)

            df.columns = [c.lower().replace(' ', '_') for c in df.columns]

            # Adicionado para corrigir o problema da coluna ticker_base
            if table_name == 'dividend_yield':
                if 'ticker_base' in df.columns:
                    df = df.drop(columns=['ticker_base'])
            
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
    for res in sorted(results, key=lambda x: (x['status'] == '❌ Falha', x['status'] == '⚠️ Vazio')):
        logger.info(f"  - {res['file']:<30} {res['status']}")
    logger.info("="*30 + "\n\n✨ Script concluído!\n")

if __name__ == "__main__":
    main()
