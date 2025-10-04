import duckdb
import os
from datetime import datetime
from dateutil import tz

script_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))

source_path = os.path.join(project_root, 'data', 'acoes_e_fundos.parquet')
dest_path = os.path.join(project_root, 'duckdb', 'trusted_dw', 'acoes_e_fundos.parquet')

con = duckdb.connect(database=':memory:')

if not os.path.exists(dest_path):
    print(f"Arquivo de destino não encontrado. Execute a carga completa primeiro.")
    con.close()
    exit()

# Use CTEs for clarity
get_new_records_query = f"""
WITH source_data AS (
    SELECT * FROM read_parquet('{source_path}')
),
destination_data AS (
    SELECT * FROM read_parquet('{dest_path}')
)
SELECT s.*
FROM source_data s
LEFT JOIN destination_data d ON s.ticker = d.ticker
WHERE d.ticker IS NULL
"""

new_records_rel = con.sql(get_new_records_query)

try:
    num_new_records = len(new_records_rel.fetchall())
except Exception:
    num_new_records = 0

if num_new_records > 0:
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Sao_Paulo')
    utc_now = datetime.utcnow().replace(tzinfo=from_zone)
    local_time = utc_now.astimezone(to_zone)
    data_atualizacao = local_time.strftime('%Y-%m-%d %H:%M:%S')

    # Re-execute query to get relation object back, and add date
    new_records_rel = con.sql(get_new_records_query)
    new_records_with_date_rel = new_records_rel.project(f"*, '{data_atualizacao}' as data_atualizacao")

    # Union and write back
    con.execute(f"CREATE OR REPLACE VIEW destination_view AS SELECT * FROM read_parquet('{dest_path}')")
    final_rel = con.sql("SELECT * FROM destination_view").union(new_records_with_date_rel)
    final_rel.write_parquet(dest_path)

    print(f"{num_new_records} novos registros foram adicionados a '{dest_path}'.")
else:
    print("Nenhum novo registro encontrado.")

con.close()
