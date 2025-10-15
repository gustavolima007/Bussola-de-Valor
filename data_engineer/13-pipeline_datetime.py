from datetime import datetime, timedelta, timezone
import os
import pandas as pd

def get_utc_minus_3_time():
    """Retorna a data e hora atual no fuso horário UTC-3."""
    return datetime.now(timezone.utc) - timedelta(hours=3)

def main():
    """
    Cria um arquivo parquet contendo a data e hora da última atualização da pipeline.
    O arquivo é salvo no diretório 'duckdb/land_dw/'.
    """
    output_dir = os.path.join('duckdb', 'land_dw')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'pipeline_datetime.parquet')
    
    now_utc_minus_3 = get_utc_minus_3_time()
    
    df = pd.DataFrame([{'pipeline_datetime': now_utc_minus_3}])
    
    df.to_parquet(output_path, index=False)
    
    print(f"Arquivo de data de atualização da pipeline salvo em: {output_path}")

if __name__ == "__main__":
    main()
