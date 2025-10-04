import duckdb
import os
from datetime import datetime
from dateutil import tz

# Obter o diretório do script atual
script_dir = os.path.dirname(os.path.realpath(__file__))

# Navegar para o diretório raiz do projeto
project_root = os.path.dirname(os.path.dirname(script_dir))

# Caminho para o arquivo parquet de origem
source_parquet_path = os.path.join(project_root, 'data', 'acoes_e_fundos.parquet')

# Caminho para o arquivo parquet de destino
destination_dir = os.path.join(project_root, 'duckdb', 'trusted_dw')
destination_parquet_path = os.path.join(destination_dir, 'acoes_e_fundos.parquet')

# Criar o diretório de destino se não existir
os.makedirs(destination_dir, exist_ok=True)

# Conectar ao DuckDB
con = duckdb.connect(database=':memory:')

# Ler o arquivo parquet de origem
relation = con.read_parquet(source_parquet_path)

# Obter data e hora atual em UTC-3
from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Sao_Paulo') # Corresponds to UTC-3 in most of Brazil
utc_now = datetime.utcnow().replace(tzinfo=from_zone)
local_time = utc_now.astimezone(to_zone)
data_atualizacao = local_time.strftime('%Y-%m-%d %H:%M:%S')


# Adicionar a nova coluna
con.register('temp_relation', relation)
updated_relation = con.sql(f"""
SELECT *, '{data_atualizacao}' AS data_atualizacao
FROM temp_relation
""")

# Escrever para o novo arquivo parquet (sobrescrevendo)
updated_relation.write_parquet(destination_parquet_path)

print(f"Carga completa de '{source_parquet_path}' para '{destination_parquet_path}' com a coluna 'data_atualizacao' foi um sucesso.")

con.close()