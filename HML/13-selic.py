import requests
import pandas as pd
from datetime import datetime, timedelta

# Série 432 = Meta Selic (% a.a.)
SERIE_SELIC = 432

# Datas de início e fim (últimos 10 anos)
fim = datetime.today()
inicio = fim - timedelta(days=365 * 10)

# Format URL with DD/MM/YYYY dates
url = (
    f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{SERIE_SELIC}/dados"
    f"?formato=json&dataInicial={inicio.strftime('%d/%m/%Y')}&dataFinal={fim.strftime('%d/%m/%Y')}"
)

try:
    # Requisição à API do Banco Central
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()  # Raises HTTPError for 4xx/5xx responses

    # Check if response is JSON
    content_type = resp.headers.get('content-type', '')
    if 'application/json' not in content_type:
        print(f"Erro: Resposta não é JSON. Content-Type: {content_type}")
        print(f"Conteúdo da resposta: {resp.text[:500]}")
        exit(1)

    # Parse JSON
    try:
        dados = resp.json()
    except ValueError as e:
        print(f"Erro ao decodificar JSON: {e}")
        print(f"Conteúdo da resposta: {resp.text[:500]}")
        exit(1)

    # Tratamento dos dados
    df = pd.DataFrame(dados)
    if df.empty:
        print("Erro: Nenhum dado retornado pela API")
        exit(1)

    # Convert 'data' to datetime and 'valor' to numeric
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df['valor'] = pd.to_numeric(df['valor'].str.replace(',', '.'), errors='coerce')

    # Remove any rows with NaN values
    df = df.dropna()

    # Extract year and month, then group by year and month to calculate mean 'valor'
    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month
    df_grouped = df.groupby(['ano', 'mes'])['valor'].mean().reset_index()

    # Salvar em CSV
    arquivo_csv = "selic_10_anos_mensal.csv"
    df_grouped.to_csv(arquivo_csv, index=False, encoding="utf-8-sig")

    print(f"Arquivo salvo: {arquivo_csv}")
    print(df_grouped.head())

except requests.exceptions.HTTPError as e:
    print(f"Erro HTTP: {e}")
    print(f"Conteúdo da resposta: {resp.text[:500]}")
except requests.exceptions.RequestException as e:
    print(f"Erro de requisição: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")