import pandas as pd
from pathlib import Path

# Define the paths to the CSV files
BASE_DIR = Path(__file__).resolve().parent.parent / 'data'
ACOES_E_FUNDOS_PATH = BASE_DIR / 'acoes_e_fundos.csv'
INDICADORES_PATH = BASE_DIR / 'indicadores.csv'

# Read the CSV files into pandas DataFrames
try:
    df_acoes = pd.read_csv(ACOES_E_FUNDOS_PATH)
    df_indicadores = pd.read_csv(INDICADORES_PATH)
except FileNotFoundError as e:
    print(f"Error: {e}. Make sure the CSV files exist.")
    exit()

# Merge the DataFrames on the 'ticker' column
# Ensure the 'ticker' column in df_indicadores is uppercase to match df_acoes
df_indicadores['ticker'] = df_indicadores['ticker'].str.upper()
df_merged = pd.merge(df_acoes, df_indicadores, on='ticker', how='inner')

# Select the desired columns
# Assuming 'setor' refers to 'setor_b3'
if 'empresa' in df_merged.columns and 'setor_b3' in df_merged.columns:
    df_result = df_merged[['ticker', 'empresa', 'setor_b3']]

    # Print the resulting DataFrame
    print(df_result.to_string())
else:
    print("Error: One or more of the required columns ('ticker', 'empresa', 'setor_b3') are not in the merged DataFrame.")
    print("Available columns are:", df_merged.columns.tolist())
