import requests
import yfinance as yf
import pandas as pd
import warnings
from deep_translator import GoogleTranslator
from tqdm.auto import tqdm

# Este script consulta a lista de ativos na BRAPI, filtra por tipos (ação/fundo) e setores-alvo,
# valida e enriquece com metadados via yfinance (país, nome, market cap), traduz subsetores
# para PT-BR, e retorna um DataFrame padronizado com ticker, empresa, setor (padrão B3),
# subsetor, tipo e logo, pronto para ser salvo no pipeline.

warnings.simplefilter(action='ignore', category=FutureWarning)

# 🎯 Setores-alvo
SETORES_ALVO = {
    "Finance",
    "Utilities",
    "Communications",
    "Industrial Services"
}

# 🌐 Tradução de setores para padrão B3
TRADUCAO_SETORES = {
    "Finance": "Financeiro",
    "Utilities": "Utilidade Pública",
    "Communications": "Comunicações",
    "Industrial Services": "Serviços Industriais"
}

# 🏷️ Tradução de tipos de ativos
TRADUCAO_TIPOS = {
    "stock": "Ação",
    "fund": "Fundo"
}

# 🌍 Função para traduzir subsetores
def traduzir_subsetor(texto):
    if not texto or texto == "N/A":
        return "N/A"
    try:
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except Exception:
        return texto  # fallback para o original se falhar

# 🔍 Função principal
def coletar_dados_ativos(setores):
    try:
        lista = requests.get("https://brapi.dev/api/quote/list").json().get("stocks", [])
    except Exception as e:
        print(f"❌ Erro ao buscar ativos: {e}")
        return pd.DataFrame()
    lista = list(lista)
    lista = [item for item in lista if isinstance(item, dict)]
    lista_iter = tqdm(lista, desc="Filtrando lista BRAPI")

    ativos = {
        f"{item['stock']}.SA": {
            "setor_brapi": TRADUCAO_SETORES.get(item["sector"], item["sector"]),
            "tipo": item["type"],
            "logo": item.get("logo")
        }
        for item in lista_iter
        if item.get("sector") in setores and item.get("type") in {"stock", "fund"} and not str(item.get("stock", "")).endswith("F")
    }

    registros = []
    for ticker, dados in tqdm(ativos.items(), desc="Coletando metadados (yfinance)"):
        try:
            info = yf.Ticker(ticker).info
            if info.get("country") != "Brazil":
                continue

            subsetor_en = info.get("industry", "N/A")
            subsetor_pt = traduzir_subsetor(subsetor_en)

            registros.append({
                "ticker": ticker,
                "empresa": info.get("longName", "N/A"),
                "setor_brapi": dados["setor_brapi"],
                "subsetor_yfinance": subsetor_pt,
                "pais": info.get("country", "N/A"),
                "tipo": TRADUCAO_TIPOS.get(dados["tipo"], dados["tipo"]),  # Aplicando tradução aqui
                "market_cap": info.get("marketCap"),
                "logo": dados["logo"]
            })
        except Exception:
            continue

    return pd.DataFrame(registros)

# 💾 Execução e salvamento
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent / 'data'

df = coletar_dados_ativos(SETORES_ALVO)
if not df.empty:
    BASE.mkdir(parents=True, exist_ok=True)
    out_path = BASE / 'acoes_e_fundos.csv'
    df.to_csv(out_path, index=False)
    print(f"✅ Arquivo salvo em: {out_path}")
else:
    print("⚠️ Nenhum dado coletado para salvar.")
