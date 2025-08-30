# -*- coding: utf-8 -*-
"""
📄 Script para extrair e processar dados de ações e fundos da B3.

Este script se conecta à API Brapi para obter uma lista de todos os ativos
disponíveis, realiza uma série de filtros e limpezas, e salva o resultado
em um arquivo CSV.

Otimizações e Filtros:
- Remove tickers fracionados (terminados em 'F').
- Exclui BDRs (Brazilian Depositary Receipts).
- Elimina o setor 'Miscellaneous' e ativos com setor não especificado.
- Mapeia o setor da Brapi para o padrão hierárquico da B3 (Setor e Subsetor)
  com nomes mais descritivos.
- Corrige a classificação de empresas como a Klabin.
- Remove colunas desnecessárias.
- Remove ativos específicos solicitados pelo usuário.
- Renomeia as colunas para um padrão em português e minúsculas.
- Salva o DataFrame resultante em 'data/acoes_e_fundos.csv'.
"""

import requests
import pandas as pd
from pathlib import Path
import time

# Mapeamento do padrão da B3 para Setor e Subsetor
# Usa o setor da Brapi (em inglês) para definir Setor e Subsetor B3.
SETORES_B3_MAPPER = {
    "Energy Minerals": ("Petróleo, Gás e Biocombustíveis", "Petróleo e Gás"),
    "Non-Energy Minerals": ("Materiais Básicos", "Mineração e Siderurgia"),
    "Process Industries": ("Materiais Básicos", "Papel, Química e Outros"),
    "Utilities": ("Utilidade Pública", "Energia e Saneamento"),
    "Finance": ("Financeiro e Outros", "Bancos e Financeiros"),
    "Health Technology": ("Saúde", "Saúde Tecnologia"),
    "Health Services": ("Saúde", "Saúde Serviços Médicos"),
    "Producer Manufacturing": ("Bens Industriais", "Máquinas e Equipamentos"),
    "Industrial Services": ("Bens Industriais", "Serviços Industriais"),
    "Transportation": ("Bens Industriais", "Transporte e Logística"),
    "Retail Trade": ("Consumo Cíclico", "Comércio Varejista"),
    "Consumer Durables": ("Consumo Cíclico", "Bens Duráveis"),
    "Consumer Services": ("Consumo Cíclico", "Serviços"),
    "Commercial Services": ("Consumo Cíclico", "Serviços Comerciais"),
    "Electronic Technology": ("Tecnologia da Informação", "TI - Hardware e Equipamentos"),
    "Technology Services": ("Tecnologia da Informação", "TI - Serviços de Software"),
    "Communications": ("Comunicações", "Telefonia e Mídia"),
    "Consumer Non-Durables": ("Consumo Não Cíclico", "Alimentos, Bebidas e Pessoais"),
    "Distribution Services": ("Consumo Não Cíclico", "Comércio e Distribuição")
}

# Mapeamento de tickers específicos para correção.
# Adicione mais empresas conforme a necessidade.
CORRECOES_ESPECIFICAS_B3 = {
    "KLBN11": ("Materiais Básicos", "Papel e Celulose"),
    "KLBN4": ("Materiais Básicos", "Papel e Celulose"),
    "KLBN3": ("Materiais Básicos", "Papel e Celulose"),
    "SUZB3": ("Materiais Básicos", "Papel e Celulose"),
    "NUTR3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "EUCA3": ("Materiais Básicos", "Madeira e Produtos"),
    "EUCA4": ("Materiais Básicos", "Madeira e Produtos")
}

# Lista de tickers a serem removidos do conjunto de dados
TICKERS_A_REMOVER = [
    "SNCI11", "WSEC11", "IRIM11", "RBIF11", "EGYR11", "RENV11"
]

def mapear_setores_b3(df):
    """
    Mapeia os setores da Brapi para o padrão B3 de Setor e Subsetor,
    com correções manuais para empresas específicas.

    Args:
        df (pd.DataFrame): DataFrame com a coluna 'setor_brapi'.

    Returns:
        pd.DataFrame: DataFrame com as novas colunas 'setor_b3' e 'subsetor_b3'.
    """
    # Aplica o mapeamento geral
    df[['setor_b3', 'subsetor_b3']] = df['setor_brapi'].map(SETORES_B3_MAPPER).apply(pd.Series)
    
    # Aplica as correções manuais para cada ticker
    for ticker, (setor, subsetor) in CORRECOES_ESPECIFICAS_B3.items():
        # Usa .loc para garantir a atribuição correta
        df.loc[df['ticker'] == ticker, 'setor_b3'] = setor
        df.loc[df['ticker'] == ticker, 'subsetor_b3'] = subsetor
    
    return df

def extrair_dados_brapi():
    """
    Extrai, filtra e processa dados de ativos da B3 usando a API Brapi.

    Returns:
        pandas.DataFrame: Um DataFrame contendo os dados dos ativos filtrados
                          e processados. Retorna None se ocorrer um erro.
    """
    api_url = "https://brapi.dev/api/quote/list"
    csv_output = "acoes_e_fundos.csv"
    base_dir = Path(__file__).resolve().parent.parent / 'data'

    print("Iniciando extração de dados via Brapi...")
    start_time = time.time()

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        ativos = data.get('stocks', [])

        if not ativos:
            print("Nenhum ativo encontrado na resposta da API.")
            return None

        print("Processando dados...")
        df_ativos = pd.DataFrame(ativos)

        df_ativos = df_ativos[
            ~df_ativos['stock'].str.endswith('F') &
            (df_ativos['type'] != 'bdr')
        ]

        # Removendo os tickers específicos solicitados
        df_ativos = df_ativos[~df_ativos['stock'].isin(TICKERS_A_REMOVER)]

        df_ativos = df_ativos[
            (df_ativos['sector'] != 'Miscellaneous') &
            (df_ativos['sector'].notna()) &
            (df_ativos['sector'].str.strip() != '') &
            (df_ativos['sector'] != 'N/A')
        ]
        
        colunas_renomear = {
            'stock': 'ticker',
            'sector': 'setor_brapi',
            'type': 'tipo',
            'volume': 'volume',
            'logo': 'logo',
            'changePercent': 'percentual_variacao'
        }
        df_ativos = df_ativos.rename(columns=colunas_renomear)

        # Adiciona a nova lógica de mapeamento de setores
        df_ativos = mapear_setores_b3(df_ativos)

        colunas_remover = [col for col in ['change', 'market_cap', 'name', 'close'] if col in df_ativos.columns]
        if colunas_remover:
            df_ativos = df_ativos.drop(columns=colunas_remover)
            print(f"Colunas removidas: {colunas_remover}")
        else:
            print("Nenhuma das colunas alvo para remoção foi encontrada.")
        
        df_ativos = df_ativos.fillna('N/A')
        df_ativos = df_ativos.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df_ativos = df_ativos.replace('', 'N/A')
        
        base_dir.mkdir(parents=True, exist_ok=True)
        csv_path = base_dir / csv_output
        df_ativos.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"Arquivo CSV salvo com sucesso em: {csv_path}")

        elapsed_time = time.time() - start_time
        print(f"Concluído em {elapsed_time:.2f} segundos. Total de ativos: {len(df_ativos)}")
        return df_ativos

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição à API: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None

if __name__ == "__main__":
    df = extrair_dados_brapi()
    if df is not None:
        print("\nAmostra dos primeiros 5 ativos:")
        print(df.head().to_string(index=False))
        print(f"\nColunas disponíveis: {list(df.columns)}")