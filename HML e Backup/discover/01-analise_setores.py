# -*- coding: utf-8 -*-
"""
Script para buscar todos os setores de ativos listados na API Brapi,
traduzir os nomes dos setores para português, e salvar o resultado
em um arquivo CSV com duas colunas: original e traduzido.
"""

import requests
import pandas as pd
from tqdm import tqdm
# Dicionário fixo para tradução dos setores B3 (EN -> PT)
TRADUCAO_SETORES_B3 = {
    "Energy Minerals": "Petróleo, Gás e Biocombustíveis",
    "Non-Energy Minerals": "Materiais Básicos",
    "Utilities": "Utilidade Pública",
    "Finance": "Financeiro e Outros",
    "Process Industries": "Materiais Básicos",
    "Health Technology": "Saúde",
    "Health Services": "Saúde",
    "Producer Manufacturing": "Bens Industriais",
    "Industrial Services": "Bens Industriais",
    "Transportation": "Bens Industriais",
    "Retail Trade": "Consumo Cíclico",
    "Consumer Durables": "Consumo Cíclico",
    "Consumer Services": "Consumo Cíclico",
    "Electronic Technology": "Tecnologia da Informação",
    "Technology Services": "Tecnologia da Informação",
    "Commercial Services": "Consumo Cíclico",
    "Communications": "Comunicações",
    "Consumer Non-Durables": "Consumo não Cíclico",
    "Distribution Services": "Consumo não Cíclico"
}

def obter_e_salvar_setores_brapi():
    api_url = "https://brapi.dev/api/quote/list"
    nome_arquivo_csv = "setores_b3.csv"
    
    print("Iniciando busca de dados na API da Brapi...")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        ativos = data.get('stocks', [])

        if not ativos:
            print("Nenhum ativo foi encontrado na resposta da API.")
            return False

        print("\nProcessando ativos e extraindo os setores...")
        df_ativos = pd.DataFrame(ativos)
        setores_unicos = set()

        for setor in tqdm(df_ativos['sector'], desc="Filtrando setores únicos"):
            if pd.notna(setor) and setor.strip():
                setores_unicos.add(setor)

        lista_ordenada_setores = sorted(list(setores_unicos))

        print("\nConvertendo nomes dos setores para português via dicionário fixo...")
        setores_traduzidos = [TRADUCAO_SETORES_B3.get(setor, setor) for setor in lista_ordenada_setores]

        df_setores = pd.DataFrame({
            "Setor (Inglês)": lista_ordenada_setores,
            "Setor (Português)": setores_traduzidos
        })

        df_setores.to_csv(nome_arquivo_csv, index=False, encoding='utf-8-sig')
        print(f"\nArquivo '{nome_arquivo_csv}' gerado com sucesso com traduções incluídas!")

        return df_setores

    except requests.exceptions.Timeout:
        print("Erro: A requisição para a API demorou demais para responder (timeout).")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição à API: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o processamento: {e}")
        return None

if __name__ == "__main__":
    df_resultado = obter_e_salvar_setores_brapi()

    if df_resultado is not None:
        print("\n--- AMOSTRA DOS SETORES TRADUZIDOS ---")
        print(df_resultado.head(10).to_string(index=False))
        print(f"\nTotal de {len(df_resultado)} setores únicos encontrados e salvos.")
