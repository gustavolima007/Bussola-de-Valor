# -*- coding: utf-8 -*-
"""
📄 Script para extrair e processar dados de ações e fundos da B3.

Este script se conecta à API Brapi para obter uma lista de todos os ativos
disponíveis, realiza uma série de filtros e limpezas, e salva o resultado
em arquivo CSV.

Otimizações e Filtros:
- Remove tickers fracionados (terminados em 'F').
- Exclui BDRs (Brazilian Depositary Receipts).
- Elimina o setor 'Miscellaneous' e ativos com setor não especificado.
- Mapeia o setor da Brapi para o padrão hierárquico da B3 (Setor e Subsetor).
- Corrige a classificação de empresas como Klabin, Embraer, Taurus, etc.
- Remove colunas desnecessárias.
- Remove ativos específicos solicitados pelo usuário.
- Renomeia as colunas para um padrão em português e minúsculas.
- Salva o DataFrame em 'data/acoes_e_fundos.csv'.
"""

import requests
import pandas as pd
from pathlib import Path
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mapeamento do padrão da B3 para Setor e Subsetor
SETORES_B3_MAPPER = {
    "Energy Minerals": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "Non-Energy Minerals": ("Materiais Básicos", "Mineração e Siderurgia"),
    "Process Industries": ("Materiais Básicos", "Papel, Química e Outros"),
    "Utilities": ("Utilidade Pública", "Energia Elétrica"),
    "Finance": ("Financeiro e Outros", "Bancos e Financeiros"),
    "Health Technology": ("Saúde", "Saúde Tecnologia"),
    "Health Services": ("Saúde", "Saúde Serviços Médicos"),
    "Producer Manufacturing": ("Bens Industriais", "Máquinas e Equipamentos"),
    "Industrial Services": ("Bens Industriais", "Serviços Industriais"),
    "Transportation": ("Bens Industriais", "Transporte e Logística"),
    "Retail Trade": ("Consumo Cíclico", "Comércio Varejista"),
    "Consumer Durables": ("Consumo Cíclico", "Bens Duráveis"),
    "Consumer Services": ("Consumo Cíclico", "Serviços Educacionais"),
    "Commercial Services": ("Consumo Cíclico", "Serviços Comerciais"),
    "Electronic Technology": ("Tecnologia da Informação", "Hardware e Equipamentos"),
    "Technology Services": ("Tecnologia da Informação", "Serviços de Software"),
    "Communications": ("Comunicações", "Telefonia e Mídia"),
    "Consumer Non-Durables": ("Consumo Não Cíclico", "Alimentos, Bebidas e Pessoais"),
    "Distribution Services": ("Consumo Não Cíclico", "Comércio e Distribuição"),
    "Real Estate": ("Financeiro e Outros", "Imobiliário")
}

# Mapeamento de tickers específicos para correção
CORRECOES_ESPECIFICAS_B3 = {
    # Energia Elétrica e Saneamento
    "ALUP3": ("Utilidade Pública", "Energia Elétrica"),
    "ALUP4": ("Utilidade Pública", "Energia Elétrica"),
    "ALUP11": ("Utilidade Pública", "Energia Elétrica"),
    "CMIG3": ("Utilidade Pública", "Energia Elétrica"),
    "CMIG4": ("Utilidade Pública", "Energia Elétrica"),
    "CPLE3": ("Utilidade Pública", "Energia Elétrica"),
    "CPLE6": ("Utilidade Pública", "Energia Elétrica"),
    "ELET3": ("Utilidade Pública", "Energia Elétrica"),
    "ELET6": ("Utilidade Pública", "Energia Elétrica"),
    "EQTL3": ("Utilidade Pública", "Energia Elétrica"),
    "EGIE3": ("Utilidade Pública", "Energia Elétrica"),
    "ENGI3": ("Utilidade Pública", "Energia Elétrica"),
    "ENGI4": ("Utilidade Pública", "Energia Elétrica"),
    "ENGI11": ("Utilidade Pública", "Energia Elétrica"),
    "NEOE3": ("Utilidade Pública", "Energia Elétrica"),
    "ENMT3": ("Utilidade Pública", "Energia Elétrica"),
    "ENMT4": ("Utilidade Pública", "Energia Elétrica"),
    "COCE5": ("Utilidade Pública", "Energia Elétrica"),
    "AESB3": ("Utilidade Pública", "Energia Elétrica"),
    "AURE3": ("Utilidade Pública", "Energia Elétrica"),
    "CEBR3": ("Utilidade Pública", "Energia Elétrica"),
    "CEBR5": ("Utilidade Pública", "Energia Elétrica"),
    "CEBR6": ("Utilidade Pública", "Energia Elétrica"),
    "CPFE3": ("Utilidade Pública", "Energia Elétrica"),
    "GEPA4": ("Utilidade Pública", "Energia Elétrica"),
    "LIGT3": ("Utilidade Pública", "Energia Elétrica"),
    "REDE3": ("Utilidade Pública", "Energia Elétrica"),
    "TAEE3": ("Utilidade Pública", "Energia Elétrica"),
    "TAEE4": ("Utilidade Pública", "Energia Elétrica"),
    "TAEE11": ("Utilidade Pública", "Energia Elétrica"),
    "SBSP3": ("Utilidade Pública", "Saneamento"),
    "CSMG3": ("Utilidade Pública", "Saneamento"),
    "SAPR3": ("Utilidade Pública", "Saneamento"),
    "SAPR4": ("Utilidade Pública", "Saneamento"),
    "SAPR11": ("Utilidade Pública", "Saneamento"),
    # Papel e Celulose
    "KLBN11": ("Materiais Básicos", "Papel e Celulose"),
    "KLBN4": ("Materiais Básicos", "Papel e Celulose"),
    "KLBN3": ("Materiais Básicos", "Papel e Celulose"),
    "SUZB3": ("Materiais Básicos", "Papel e Celulose"),
    "EUCA3": ("Materiais Básicos", "Papel e Celulose"),
    "EUCA4": ("Materiais Básicos", "Papel e Celulose"),
    # Químicos
    "NUTR3": ("Materiais Básicos", "Químicos"),
    # Petróleo, Gás e Biocombustíveis
    "CSAN3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    # Bens Duráveis
    "VULC3": ("Consumo Cíclico", "Bens Duráveis"),
    "GRND3": ("Consumo Cíclico", "Bens Duráveis"),
    "VIVA3": ("Consumo Cíclico", "Bens Duráveis"),
     "DOHL4": ("Consumo Cíclico", "Bens Duráveis"),
    # Construção Civil e Imobiliário
    "LAVV3": ("Financeiro", "Construção Civil e Imobiliário"),
    "TRIS3": ("Financeiro", "Construção Civil e Imobiliário"),
    "TEND3": ("Financeiro", "Construção Civil e Imobiliário"),
    "SCAR3": ("Financeiro", "Construção Civil e Imobiliário"),
    "HBOR3": ("Financeiro", "Construção Civil e Imobiliário"),
    "LPSB3": ("Financeiro", "Construção Civil e Imobiliário"),
    "EVEN3": ("Financeiro", "Construção Civil e Imobiliário"),
    "LAND3": ("Financeiro", "Construção Civil e Imobiliário"),
    "DIRR3": ("Financeiro", "Construção Civil e Imobiliário"),
    # Serviços de Software
    "CSUD3": ("Tecnologia da Informação", "Serviços de Software"),
    "VLID3": ("Tecnologia da Informação", "Serviços de Software"),
    "CASH3": ("Tecnologia da Informação", "Serviços de Software"),
    # Serviços Industriais
    "MILS3": ("Bens Industriais", "Serviços Industriais"),
    # Serviços Educacionais
    "COGN3": ("Consumo Cíclico", "Serviços Educacionais"),
    "YDUQ3": ("Consumo Cíclico", "Serviços Educacionais"),
    "TTEN3": ("Consumo Cíclico", "Serviços Educacionais"),
    # Comércio Varejista
    "PETZ3": ("Consumo Cíclico", "Comércio Varejista"),
    # Telefonia e Mídia
    "DESK3": ("Comunicações", "Telefonia e Mídia"),
    # Máquinas e Equipamentos
    "ARML3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "AERI3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "EMBR3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "TASA3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "TASA4": ("Bens Industriais", "Máquinas e Equipamentos"),
    # Alimentos, Bebidas e Pessoais
    "AGRO3": ("Consumo Não Cíclico", "Alimentos, Bebidas e Pessoais"),
    "NUTR3": ("Consumo Não Cíclico", "Alimentos, Bebidas e Pessoais")
}

# Lista de tickers a serem removidos
TICKERS_A_REMOVER = [
    "SNCI11", "WSEC11", "IRIM11", "RBIF11", "EGYR11", "RENV11", "RNR9L", "PPLA11"
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
    def fallback_map(setor):
        if pd.isna(setor) or setor in ['N/A', '', 'Miscellaneous']:
            return ('Indefinido', 'Indefinido')
        return SETORES_B3_MAPPER.get(setor, ('Outros', 'Não Classificado'))

    df[['setor_b3', 'subsetor_b3']] = df['setor_brapi'].apply(fallback_map).apply(pd.Series)
    
    # Correções manuais
    for ticker, (setor, subsetor) in CORRECOES_ESPECIFICAS_B3.items():
        df.loc[df['ticker'] == ticker, ['setor_b3', 'subsetor_b3']] = [setor, subsetor]
    
    return df

def extrair_dados_brapi():
    """
    Extrai, filtra e processa dados de ativos da B3 usando a API Brapi.

    Returns:
        pandas.DataFrame: Um DataFrame contendo os dados dos ativos filtrados
                          e processados. Retorna None se ocorrer um erro.
    """
    api_url = "https://brapi.dev/api/quote/list"
    base_dir = Path(__file__).resolve().parent.parent / 'data'
    csv_output = base_dir / "acoes_e_fundos.csv"

    logger.info("Iniciando extração de dados via Brapi...")
    start_time = time.time()

    try:
        # Configuração de retry para a API
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get(api_url, timeout=15)
        response.raise_for_status()
        time.sleep(1)  # Respeitar rate limit
        data = response.json()
        ativos = data.get('stocks', [])

        if not ativos:
            logger.error("Nenhum ativo encontrado na resposta da API.")
            return None

        df_ativos = pd.DataFrame(ativos)

        # Filtros
        df_ativos = df_ativos[
            (~df_ativos['stock'].str.endswith('F')) &
            (df_ativos['type'] != 'bdr')
        ]

        # Remover tickers específicos
        df_ativos = df_ativos[~df_ativos['stock'].isin(TICKERS_A_REMOVER)]

        # Filtros de setor
        df_ativos = df_ativos[
            (df_ativos['sector'] != 'Miscellaneous') &
            (df_ativos['sector'].notna()) &
            (df_ativos['sector'].str.strip() != '') &
            (df_ativos['sector'] != 'N/A')
        ]

        # Renomear colunas
        colunas_renomear = {
            'stock': 'ticker',
            'name': 'empresa',
            'sector': 'setor_brapi',
            'type': 'tipo',
            'volume': 'volume',
            'logo': 'logo',
            'changePercent': 'percentual_variacao'
        }
        df_ativos = df_ativos.rename(columns=colunas_renomear)

        # Preencher NaNs em empresa
        df_ativos['empresa'] = df_ativos['empresa'].fillna(df_ativos['ticker'] + ' - Não Especificado')

        # Mapeamento de setores
        df_ativos = mapear_setores_b3(df_ativos)

        # Remover colunas desnecessárias
        colunas_remover = [col for col in ['change', 'market_cap', 'close'] if col in df_ativos.columns]
        if colunas_remover:
            df_ativos = df_ativos.drop(columns=colunas_remover)

        # Limpeza final
        df_ativos = df_ativos.fillna('N/A')
        df_ativos = df_ativos.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df_ativos = df_ativos.replace('', 'N/A')

        # Opcional: Remover duplicatas por ticker (descomente se desejar)
        # df_ativos = df_ativos.drop_duplicates(subset=['ticker'])

        # Validações
        unmapped = df_ativos[df_ativos['setor_b3'] == 'Indefinido']['ticker'].tolist()
        if unmapped:
            logger.warning(f"Setores não mapeados para tickers: {unmapped}")
        assert df_ativos['setor_b3'].notna().all(), "Alguns setores não mapeados!"
        assert len(df_ativos) > 0, "DataFrame vazio após filtros!"

        # Salvar output
        base_dir.mkdir(parents=True, exist_ok=True)
        df_ativos.to_csv(csv_output, index=False, encoding='utf-8-sig')
        logger.info(f"Arquivo CSV salvo: {csv_output}")

        elapsed_time = time.time() - start_time
        logger.info(f"Concluído em {elapsed_time:.2f} segundos. Total de ativos: {len(df_ativos)}")
        return df_ativos

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição à API: {e}")
        return None
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado: {e}")
        return None

if __name__ == "__main__":
    extrair_dados_brapi()