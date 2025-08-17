import requests
import yfinance as yf
import pandas as pd
import warnings
from deep_translator import GoogleTranslator

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

    ativos = {
        f"{item['stock']}.SA": {
            "setor_brapi": TRADUCAO_SETORES.get(item["sector"], item["sector"]),
            "tipo": item["type"],
            "logo": item.get("logo")
        }
        for item in lista
        if item["sector"] in setores and item["type"] in {"stock", "fund"} and not item["stock"].endswith("F")
    }

    registros = []
    for i, (ticker, dados) in enumerate(ativos.items(), 1):
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
            print(f"✅ [{i}] {ticker} incluído")
        except Exception:
            continue

    return pd.DataFrame(registros)

# 💾 Execução e salvamento
df = coletar_dados_ativos(SETORES_ALVO)
