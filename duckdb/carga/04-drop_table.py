import duckdb
import os

# Obter o diretório do script atual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho para o banco de dados DuckDB
db_path = os.path.join(script_dir, '..', 'banco_dw', 'dw.duckdb')

# Conectar ao banco de dados
con = duckdb.connect(database=db_path, read_only=False)

# Criar um cursor
cursor = con.cursor()

# Lista de tabelas para dropar
tables_to_drop = [
    "acoes_e_fundos_v2",
    "tickers_nao_mapeados_v2"
]

# Loop para dropar cada tabela
for table in tables_to_drop:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"Tabela {table} dropada com sucesso.")
    except duckdb.Error as e:
        print(f"Erro ao dropar a tabela {table}: {e}")

# Fechar a conexão
con.close()
