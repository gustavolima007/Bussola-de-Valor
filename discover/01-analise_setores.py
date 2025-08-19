# -*- coding: utf-8 -*-
"""
Script para buscar todos os setores de ativos listados na API Brapi,
traduzir os nomes dos setores para português, e salvar o resultado
em um arquivo CSV com duas colunas: original e traduzido.
"""

import requests
import pandas as pd
from tqdm import tqdm
from deep_translator import GoogleTranslator

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

        print("\nTraduzindo nomes dos setores para português...")
        setores_traduzidos = []
        for setor in tqdm(lista_ordenada_setores, desc="Traduzindo"):
            try:
                traducao = GoogleTranslator(source='auto', target='pt').translate(setor)
            except Exception:
                traducao = "Erro na tradução"
            setores_traduzidos.append(traducao)

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
