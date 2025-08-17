import pandas as pd
import os

# Calcula DY 5 anos e DY 12 meses juntando preços atuais (precos_acoes.csv) e somas
# de dividendos (dividendos_ano_resumo.csv); normaliza tickers, computa percentuais
# e salva ../data/dividend_yield.csv com as colunas ticker, DY5anos e DY12M.

# Carregar os arquivos CSV
precos = pd.read_csv("../data/precos_acoes.csv")
div = pd.read_csv("../data/dividendos_ano_resumo.csv")

# Normalizar tickers para merge
precos["ticker_base"] = (
    precos["ticker"].astype(str).str.upper().str.strip().str.replace(".SA", "", regex=False)
)
div["ticker_base"] = div["ticker"].astype(str).str.upper().str.strip()

# Garantir tipos numéricos
precos["fechamento_atual"] = pd.to_numeric(precos["fechamento_atual"], errors="coerce")
div["valor_5anos"] = pd.to_numeric(div["valor_5anos"], errors="coerce")
div["valor_12m"] = pd.to_numeric(div["valor_12m"], errors="coerce")

# Merge para ter todos os tickers do arquivo de preços
df = precos.merge(div[["ticker_base", "valor_5anos", "valor_12m"]], on="ticker_base", how="left")

# Calcular DYs
df["DY5anos"] = (((df["valor_5anos"] / 5) / df["fechamento_atual"]) * 100).where(df["fechamento_atual"] > 0)
df["DY12M"]   = ((df["valor_12m"] / df["fechamento_atual"]) * 100).where(df["fechamento_atual"] > 0)

# Arredondar
df["DY5anos"] = df["DY5anos"].round(2)
df["DY12M"] = df["DY12M"].round(2)

# Selecionar apenas as colunas desejadas
df_final = df[["ticker", "DY5anos", "DY12M"]]

# Mostrar primeiros 5
print(df_final.head(5))

# Salvar no caminho solicitado
os.makedirs("../data", exist_ok=True)
df_final.to_csv("../data/dividend_yield.csv", index=False)
print("Arquivo salvo em: ../data/dividend_yield.csv")
