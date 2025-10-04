import duckdb
import os

# Obter o diretório do script atual
script_dir = os.path.dirname(os.path.realpath(__file__))

# Navegar para o diretório raiz do projeto
project_root = os.path.dirname(os.path.dirname(script_dir))

# Caminho para o arquivo parquet
parquet_path = os.path.join(project_root, 'data', 'acoes_e_fundos.parquet')

# Conectar ao DuckDB
con = duckdb.connect(database=':memory:')

# Ler o arquivo Parquet e converter para DataFrame
df = con.read_parquet(parquet_path).df()

# Visualizar o DataFrame
print(df)

# Fechar a conexão
con.close()
