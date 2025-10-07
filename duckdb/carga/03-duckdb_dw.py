import duckdb
import os
import glob

# --- Lógica do Script ---
def get_project_root():
    """Encontra o diretório raiz do projeto."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))

def main():
    """
    Carrega todos os arquivos .parquet da camada 'trusted_dw' para um único
    arquivo de banco de dados DuckDB, criando ou substituindo as tabelas.
    """
    project_root = get_project_root()
    trusted_dw_path = os.path.join(project_root, 'duckdb', 'trusted_dw')
    db_dir = os.path.join(project_root, 'duckdb', 'banco_dw')
    db_path = os.path.join(db_dir, 'dw.duckdb')

    # Garante que o diretório do banco de dados exista
    os.makedirs(db_dir, exist_ok=True)

    # Encontra todos os arquivos parquet no diretório trusted_dw
    parquet_files = glob.glob(os.path.join(trusted_dw_path, '*.parquet'))

    if not parquet_files:
        print("⚠️  Aviso: Nenhum arquivo .parquet encontrado em 'trusted_dw'. O banco de dados não será atualizado.")
        return

    print(f"🗄️  Iniciando a carga do Data Warehouse DuckDB em '{db_path}'...")

    try:
        # Conecta-se ao arquivo do banco de dados DuckDB
        con = duckdb.connect(database=db_path)

        for file_path in parquet_files:
            table_name = os.path.basename(file_path).replace('.parquet', '')
            try:
                # Cria ou substitui a tabela no DW a partir do arquivo parquet
                con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}')")
                print(f"  ✅  Sucesso: Tabela '{table_name}' carregada no DW.")
            except Exception as e:
                # Relança a exceção para que o orquestrador saiba da falha
                raise RuntimeError(f"Erro ao carregar a tabela '{table_name}'") from e

        con.close()
        print("\n✨ Processo de carga do DW finalizado! ✨")

    except Exception as e:
        print(f"❌  Erro fatal ao conectar ou operar o banco de dados DuckDB: {e}")
        raise  # Relança a exceção para sinalizar a falha

if __name__ == "__main__":
    main()
