import pandas as pd
from bcb import get

# Busca dados de índices prudenciais (ajuste o 'table_name' se necessário; teste com 'sisf_ranking_instituicoes_financeiras')
# Dataset aproximado: https://opendata.bcb.gov.br/dataset/indices-de-capital (verifique ID exato no portal BCB)
df = get(2278, start_date='2020-01-01')  # ID exemplo para índices de capital; substitua pelo ID exato do Basileia (procure no portal)

# Filtra para Banco do Brasil (código 70)
bb_data = df[df['codigo'] == 70]  # 'codigo' pode variar; inspecione as colunas
bb_basileia = bb_data['basileia'].iloc[-1]  # Último valor (ajuste coluna)

print(f"Índice de Basileia do BB (último período): {bb_basileia:.2f}%")