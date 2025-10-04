import duckdb
import os
from datetime import datetime
from dateutil import tz

# --- Configuração ---
# Lista de tabelas para carga completa
# Neste modo, todos os dados da tabela são apagados e uma nova carga é inserida.
TABLES_TO_LOAD = [
    "acoes_e_fundos",
    "avaliacao_setor",
    "ciclo_mercado",
    "dividend_yield",
    "dividendos_ano_resumo",
    "indicadores",
    "indices",
    "preco_teto",
    "precos_acoes",
    "rj",
    "scores",
    "tickers_nao_mapeados"
]

# --- Lógica do Script ---
def get_project_root():
    """Encontra o diretório raiz do projeto."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))

def get_current_time_str():
    """Retorna a data e hora atual formatada como string (UTC-3)."""
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Sao_Paulo')
    utc_now = datetime.utcnow().replace(tzinfo=from_zone)
    local_time = utc_now.astimezone(to_zone)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

def main():
    """
    Executa o processo de carga completa para as tabelas especificadas.
    Lê um arquivo parquet da camada 'land_dw', adiciona uma coluna de data/hora,
    e o salva na camada 'trusted_dw', sobrescrevendo qualquer dado existente.
    """
    project_root = get_project_root()
    land_dw_path = os.path.join(project_root, 'duckdb', 'land_dw')
    trusted_dw_path = os.path.join(project_root, 'duckdb', 'trusted_dw')
    data_atualizacao = get_current_time_str()

    # Garante que o diretório de destino exista
    os.makedirs(trusted_dw_path, exist_ok=True)

    # Conecta-se ao DuckDB (pode ser em memória, já que é usado para transformação)
    con = duckdb.connect(database=':memory:')
    print("📦 Iniciando Carga Completa...")

    for table_name in TABLES_TO_LOAD:
        source_parquet_path = os.path.join(land_dw_path, f"{table_name}.parquet")
        destination_parquet_path = os.path.join(trusted_dw_path, f"{table_name}.parquet")

        if not os.path.exists(source_parquet_path):
            print(f"  ⚠️  Aviso: Arquivo de origem para '{table_name}' não encontrado. Pulando.")
            continue

        try:
            relation = con.read_parquet(source_parquet_path)
            con.register('temp_relation', relation)
            updated_relation = con.sql(f"SELECT *, '{data_atualizacao}' AS data_atualizacao FROM temp_relation")
            updated_relation.write_parquet(destination_parquet_path)
            print(f"  ✅  Sucesso: Tabela '{table_name}' carregada.")

        except Exception as e:
            print(f"  ❌  Erro ao carregar '{table_name}': {e}")

    con.close()
    print("\n✨ Processo de Carga Completa finalizado! ✨")

if __name__ == "__main__":
    main()
