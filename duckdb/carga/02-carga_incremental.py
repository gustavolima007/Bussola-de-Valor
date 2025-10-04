import duckdb
import os
from datetime import datetime, timezone
from dateutil import tz

# --- Configuração ---
# Lista de tabelas para o processo incremental.
# A lógica de como cada tabela é atualizada será tratada especificamente.
INCREMENTAL_TABLES = [
    "dividendos_ano",
    "precos_acoes_completo",
    "todos_dividendos"
]

# --- Lógica do Script ---
def get_project_root():
    """Encontra o diretório raiz do projeto."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))

def get_current_time_str():
    """Retorna a data e hora atual formatada como string (UTC-3)."""
    # Corrigido para usar datetime.now(timezone.utc) em vez do obsoleto utcnow()
    utc_now = datetime.now(timezone.utc)
    local_time = utc_now.astimezone(tz.gettz('America/Sao_Paulo'))
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

def main():
    """
    Executa o processo de carga incremental para tabelas específicas.
    A lógica principal é substituir os dados do ano corrente na camada 'trusted_dw'
    com os novos dados da 'land_dw', mantendo os dados de anos anteriores intactos.
    """
    project_root = get_project_root()
    land_dw_path = os.path.join(project_root, 'duckdb', 'land_dw')
    trusted_dw_path = os.path.join(project_root, 'duckdb', 'trusted_dw')
    data_atualizacao = get_current_time_str()
    current_year = datetime.now().year

    os.makedirs(trusted_dw_path, exist_ok=True)

    con = duckdb.connect(database=':memory:')
    print("📈 Iniciando Carga Incremental (Estratégia: Substituir Ano Corrente)...")

    for table_name in INCREMENTAL_TABLES:
        source_path = os.path.join(land_dw_path, f"{table_name}.parquet")
        dest_path = os.path.join(trusted_dw_path, f"{table_name}.parquet")

        if not os.path.exists(source_path):
            print(f"  ⚠️  Aviso: Arquivo de origem para '{table_name}' não encontrado. Pulando.")
            continue

        print(f"  🔄  Processando tabela: '{table_name}'")

        try:
            # Lê os dados da land_dw
            land_rel = con.read_parquet(source_path)

            # Se o arquivo de destino não existir, a carga é simplesmente os novos dados
            if not os.path.exists(dest_path):
                land_rel.project(f"*, '{data_atualizacao}' as data_atualizacao").write_parquet(dest_path)
                print(f"  📦  Info: Carga inicial de '{table_name}' concluída.")
                continue

            # Define os filtros para o ano corrente e para o histórico
            if table_name == 'dividendos_ano' or table_name == 'precos_acoes_completo':
                historical_filter = f"ano < {current_year}"
                land_filter = f"ano = {current_year}"
            elif table_name == 'todos_dividendos':
                historical_filter = f"YEAR(data) < {current_year}"
                land_filter = f"YEAR(data) = {current_year}"
            else:
                print(f"  ⚠️  Aviso: Lógica de filtro não definida para '{table_name}'. Pulando.")
                continue

            # 1. Filtra a land_dw para pegar SOMENTE o ano atual
            current_year_land_rel = land_rel.filter(land_filter)
            current_year_land_rel = current_year_land_rel.project(f"*, '{data_atualizacao}' as data_atualizacao")

            # 2. Filtra a trusted_dw para pegar SOMENTE os anos anteriores
            trusted_rel = con.read_parquet(dest_path)
            historical_rel = trusted_rel.filter(historical_filter)

            # 3. Une os dados históricos com os novos dados do ano atual usando UNION BY NAME
            #    para garantir que a união seja feita pelos nomes das colunas,
            #    evitando erros caso a ordem das colunas mude nos arquivos de origem.
            con.register('historical_rel_view', historical_rel)
            con.register('current_year_land_rel_view', current_year_land_rel)
            final_rel = con.sql("SELECT * FROM historical_rel_view UNION ALL BY NAME SELECT * FROM current_year_land_rel_view")

            # 4. Sobrescreve o arquivo de destino com os dados combinados
            final_rel.write_parquet(dest_path)

            # Limpa as views temporárias para evitar conflitos
            con.unregister('historical_rel_view')
            con.unregister('current_year_land_rel_view')

            print(f"  ✅  Sucesso: Tabela '{table_name}' atualizada para o ano de {current_year}.")

        except Exception as e:
            print(f"  ❌  Erro ao processar '{table_name}': {e}")

    con.close()
    print("\n✨ Processo de Carga Incremental finalizado! ✨")

if __name__ == "__main__":
    main()