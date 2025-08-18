import requests
import pandas as pd
from tqdm import tqdm

def coletar_setores_e_subsetores():
    try:
        resposta = requests.get("https://brapi.dev/api/quote/list")
        ativos = resposta.json().get("stocks", [])
    except Exception as e:
        print(f"Erro ao buscar dados da BRAPI: {e}")
        return pd.DataFrame()

    registros = set()
    for item in tqdm(ativos, desc="Coletando setores/subsetores"):
        setor = item.get("sector") or "N/A"
        subsetor = item.get("subcategory") or "N/A"
        registros.add((setor, subsetor))

    df = pd.DataFrame(list(registros), columns=["sector", "industry"])
    return df.sort_values(by=["sector", "industry"]).reset_index(drop=True)

# 🚀 Executar
df_setores = coletar_setores_e_subsetores()
print(df_setores)
