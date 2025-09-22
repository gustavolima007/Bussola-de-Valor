# -*- coding: utf-8 -*-
"""
📄 Script para extrair e processar dados de ações e fundos da B3.
... (o resto do seu script) ...
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

# Mapeamento completo e específico de Ticker para (Setor, Subsetor)
MAPEAMENTO_COMPLETO_TICKERS = {
    # ... (seu dicionário gigante e correto permanece aqui, sem alterações) ...
    # Utilidade Pública - Energia Elétrica
    "AFLT3": ("Utilidade Pública", "Energia Elétrica"), "ALUP3": ("Utilidade Pública", "Energia Elétrica"),
    "ALUP4": ("Utilidade Pública", "Energia Elétrica"), "ALUP11": ("Utilidade Pública", "Energia Elétrica"),
    "AURE3": ("Utilidade Pública", "Energia Elétrica"), "CEBR3": ("Utilidade Pública", "Energia Elétrica"),
    "CEBR5": ("Utilidade Pública", "Energia Elétrica"), "CEBR6": ("Utilidade Pública", "Energia Elétrica"),
    "CLSC4": ("Utilidade Pública", "Energia Elétrica"), "CMIG3": ("Utilidade Pública", "Energia Elétrica"),
    "CMIG4": ("Utilidade Pública", "Energia Elétrica"), "COCE5": ("Utilidade Pública", "Energia Elétrica"),
    "CPFE3": ("Utilidade Pública", "Energia Elétrica"), "CPLE3": ("Utilidade Pública", "Energia Elétrica"),
    "CPLE5": ("Utilidade Pública", "Energia Elétrica"), "CPLE6": ("Utilidade Pública", "Energia Elétrica"),
    "EGIE3": ("Utilidade Pública", "Energia Elétrica"), "EKTR4": ("Utilidade Pública", "Energia Elétrica"),
    "ELET3": ("Utilidade Pública", "Energia Elétrica"), "ELET6": ("Utilidade Pública", "Energia Elétrica"),
    "EMAE4": ("Utilidade Pública", "Energia Elétrica"), "ENEV3": ("Utilidade Pública", "Energia Elétrica"),
    "ENGI3": ("Utilidade Pública", "Energia Elétrica"), "ENGI4": ("Utilidade Pública", "Energia Elétrica"),
    "ENGI11": ("Utilidade Pública", "Energia Elétrica"), "ENMT3": ("Utilidade Pública", "Energia Elétrica"),
    "ENMT4": ("Utilidade Pública", "Energia Elétrica"), "EQMA3B": ("Utilidade Pública", "Energia Elétrica"),
    "EQPA3": ("Utilidade Pública", "Energia Elétrica"), "EQTL3": ("Utilidade Pública", "Energia Elétrica"),
    "GEPA4": ("Utilidade Pública", "Energia Elétrica"), "ISAE3": ("Utilidade Pública", "Energia Elétrica"),
    "ISAE4": ("Utilidade Pública", "Energia Elétrica"), "LIGT3": ("Utilidade Pública", "Energia Elétrica"),
    "NEOE3": ("Utilidade Pública", "Energia Elétrica"), "ORVR3": ("Utilidade Pública", "Energia Elétrica"),
    "REDE3": ("Utilidade Pública", "Energia Elétrica"), "RNEW3": ("Utilidade Pública", "Energia Elétrica"),
    "RNEW4": ("Utilidade Pública", "Energia Elétrica"), "RNEW11": ("Utilidade Pública", "Energia Elétrica"),
    "SRNA3": ("Utilidade Pública", "Energia Elétrica"), "TAEE3": ("Utilidade Pública", "Energia Elétrica"),
    "TAEE4": ("Utilidade Pública", "Energia Elétrica"), "TAEE11": ("Utilidade Pública", "Energia Elétrica"),
    "AESB3": ("Utilidade Pública", "Energia Elétrica"),

    # Utilidade Pública - Saneamento
    "CSMG3": ("Utilidade Pública", "Saneamento"), "SAPR3": ("Utilidade Pública", "Saneamento"),
    "SAPR4": ("Utilidade Pública", "Saneamento"), "SAPR11": ("Utilidade Pública", "Saneamento"),
    "SBSP3": ("Utilidade Pública", "Saneamento"),

    # Financeiro e Outros - Bancos
    "ABCB4": ("Financeiro e Outros", "Bancos"), "BAZA3": ("Financeiro e Outros", "Bancos"),
    "BBDC3": ("Financeiro e Outros", "Bancos"), "BBDC4": ("Financeiro e Outros", "Bancos"),
    "BEES3": ("Financeiro e Outros", "Bancos"), "BEES4": ("Financeiro e Outros", "Bancos"),
    "BGIP4": ("Financeiro e Outros", "Bancos"), "BMEB4": ("Financeiro e Outros", "Bancos"),
    "BMGB4": ("Financeiro e Outros", "Bancos"), "BNBR3": ("Financeiro e Outros", "Bancos"),
    "BPAC3": ("Financeiro e Outros", "Bancos"), "BPAC5": ("Financeiro e Outros", "Bancos"),
    "BPAC11": ("Financeiro e Outros", "Bancos"), "BPAN4": ("Financeiro e Outros", "Bancos"),
    "BRSR3": ("Financeiro e Outros", "Bancos"), "BRSR6": ("Financeiro e Outros", "Bancos"),
    "BSLI3": ("Financeiro e Outros", "Bancos"), "BSLI4": ("Financeiro e Outros", "Bancos"),
    "ITUB3": ("Financeiro e Outros", "Bancos"), "ITUB4": ("Financeiro e Outros", "Bancos"),
    "PINE3": ("Financeiro e Outros", "Bancos"), "PINE4": ("Financeiro e Outros", "Bancos"),
    "SANB3": ("Financeiro e Outros", "Bancos"), "SANB4": ("Financeiro e Outros", "Bancos"),
    "SANB11": ("Financeiro e Outros", "Bancos"), "BBAS3": ("Financeiro e Outros", "Bancos"),

    # Financeiro e Outros - Serviços Financeiros Diversos
    "ALOS3": ("Financeiro e Outros", "Serviços Financeiros Diversos"), "B3SA3": ("Financeiro e Outros", "Serviços Financeiros Diversos"),
    "BBSE3": ("Financeiro e Outros", "Serviços Financeiros Diversos"), "BRAP3": ("Financeiro e Outros", "Serviços Financeiros Diversos"),
    "BRAP4": ("Financeiro e Outros", "Serviços Financeiros Diversos"), "CXSE3": ("Financeiro e Outros", "Serviços Financeiros Diversos"),
    "IGTI3": ("Financeiro e Outros", "Serviços Financeiros Diversos"), "IRBR3": ("Financeiro e Outros", "Serviços Financeiros Diversos"),
    "ITSA3": ("Financeiro e Outros", "Serviços Financeiros Diversos"), "ITSA4": ("Financeiro e Outros", "Serviços Financeiros Diversos"),
    "PEAB4": ("Financeiro e Outros", "Serviços Financeiros Diversos"), "PSSA3": ("Financeiro e Outros", "Serviços Financeiros Diversos"),
    "QUAL3": ("Financeiro e Outros", "Serviços Financeiros Diversos"), "RENT3": ("Financeiro e Outros", "Serviços Financeiros Diversos"),
    "SYNE3": ("Financeiro e Outros", "Serviços Financeiros Diversos"), "VAMO3": ("Financeiro e Outros", "Serviços Financeiros Diversos"),
    "WIZC3": ("Financeiro e Outros", "Serviços Financeiros Diversos"), "MOVI3": ("Financeiro e Outros", "Serviços Financeiros Diversos"),

    # Financeiro e Outros - Construção Civil e Imobiliário
    "AVLL3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "CALI3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "CURY3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "CYRE3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "DIRR3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "EVEN3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "EZTC3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "GFSA3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "HBOR3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "HBRE3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "JFEN3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "JHSF3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "LAND3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "LAVV3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "LPSB3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "MDNE3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "MELK3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "MRVE3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "MTRE3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "MULT3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "PDGR3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "PLPL3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "RDNI3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "RSID3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "SCAR3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "TCSA3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "TEND3": ("Financeiro e Outros", "Construção Civil e Imobiliário"), "TRIS3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),
    "VIVR3": ("Financeiro e Outros", "Construção Civil e Imobiliário"),

    # Materiais Básicos - Mineração e Siderurgia
    "CBAV3": ("Materiais Básicos", "Mineração e Siderurgia"), "CMIN3": ("Materiais Básicos", "Mineração e Siderurgia"),
    "CSNA3": ("Materiais Básicos", "Mineração e Siderurgia"), "ETER3": ("Materiais Básicos", "Mineração e Siderurgia"),
    "FESA3": ("Materiais Básicos", "Mineração e Siderurgia"), "FESA4": ("Materiais Básicos", "Mineração e Siderurgia"),
    "GGBR3": ("Materiais Básicos", "Mineração e Siderurgia"), "GGBR4": ("Materiais Básicos", "Mineração e Siderurgia"),
    "GOAU3": ("Materiais Básicos", "Mineração e Siderurgia"), "GOAU4": ("Materiais Básicos", "Mineração e Siderurgia"),
    "PMAM3": ("Materiais Básicos", "Mineração e Siderurgia"), "TKNO4": ("Materiais Básicos", "Mineração e Siderurgia"),
    "USIM3": ("Materiais Básicos", "Mineração e Siderurgia"), "USIM5": ("Materiais Básicos", "Mineração e Siderurgia"),
    "VALE3": ("Materiais Básicos", "Mineração e Siderurgia"),

    # Materiais Básicos - Papel e Celulose
    "EUCA3": ("Materiais Básicos", "Papel e Celulose"), "EUCA4": ("Materiais Básicos", "Papel e Celulose"),
    "KLBN3": ("Materiais Básicos", "Papel e Celulose"), "KLBN4": ("Materiais Básicos", "Papel e Celulose"),
    "KLBN11": ("Materiais Básicos", "Papel e Celulose"), "RANI3": ("Materiais Básicos", "Papel e Celulose"),
    "SUZB3": ("Materiais Básicos", "Papel e Celulose"),

    # Materiais Básicos - Química e Petroquímica
    "BRKM3": ("Materiais Básicos", "Química e Petroquímica"), "BRKM5": ("Materiais Básicos", "Química e Petroquímica"),
    "BRKM6": ("Materiais Básicos", "Química e Petroquímica"), "CRPG3": ("Materiais Básicos", "Química e Petroquímica"),
    "CRPG5": ("Materiais Básicos", "Química e Petroquímica"), "DEXP3": ("Materiais Básicos", "Química e Petroquímica"),
    "DEXP4": ("Materiais Básicos", "Química e Petroquímica"), "FHER3": ("Materiais Básicos", "Química e Petroquímica"),
    "UNIP3": ("Materiais Básicos", "Química e Petroquímica"), "UNIP6": ("Materiais Básicos", "Química e Petroquímica"),
    "VITT3": ("Materiais Básicos", "Química e Petroquímica"),

    # Consumo Cíclico - Comércio Varejista
    "AMAR3": ("Consumo Cíclico", "Comércio Varejista"), "AMER3": ("Consumo Cíclico", "Comércio Varejista"),
    "AMOB3": ("Consumo Cíclico", "Comércio Varejista"), "ASAI3": ("Consumo Cíclico", "Comércio Varejista"),
    "BHIA3": ("Consumo Cíclico", "Comércio Varejista"), "CEAB3": ("Consumo Cíclico", "Comércio Varejista"),
    "CGRA3": ("Consumo Cíclico", "Comércio Varejista"), "CGRA4": ("Consumo Cíclico", "Comércio Varejista"),
    "ENJU3": ("Consumo Cíclico", "Comércio Varejista"), "GMAT3": ("Consumo Cíclico", "Comércio Varejista"),
    "GUAR3": ("Consumo Cíclico", "Comércio Varejista"), "LJQQ3": ("Consumo Cíclico", "Comércio Varejista"),
    "LREN3": ("Consumo Cíclico", "Comércio Varejista"), "MGLU3": ("Consumo Cíclico", "Comércio Varejista"),
    "PCAR3": ("Consumo Cíclico", "Comércio Varejista"), "PETZ3": ("Consumo Cíclico", "Comércio Varejista"),
    "PGMN3": ("Consumo Cíclico", "Comércio Varejista"), "PNVL3": ("Consumo Cíclico", "Comércio Varejista"),
    "RADL3": ("Consumo Cíclico", "Comércio Varejista"), "RAIZ4": ("Consumo Cíclico", "Comércio Varejista"),
    "SBFG3": ("Consumo Cíclico", "Comércio Varejista"), "TFCO4": ("Consumo Cíclico", "Comércio Varejista"),
    "UGPA3": ("Consumo Cíclico", "Comércio Varejista"), "VIVA3": ("Consumo Cíclico", "Comércio Varejista"),
    "WEST3": ("Consumo Cíclico", "Comércio Varejista"),

    # Bens de Consumo (Vestuário, Casa e Pessoais)
    "ALPA3": ("Consumo Cíclico", "Bens de Consumo"), "ALPA4": ("Consumo Cíclico", "Bens de Consumo"),
    "BOBR4": ("Consumo Cíclico", "Bens de Consumo"), "CAMB3": ("Consumo Cíclico", "Bens de Consumo"),
    "GRND3": ("Consumo Cíclico", "Bens de Consumo"), "HAGA3": ("Consumo Cíclico", "Bens de Consumo"),
    "HAGA4": ("Consumo Cíclico", "Bens de Consumo"), "MNDL3": ("Consumo Cíclico", "Bens de Consumo"),
    "NATU3": ("Consumo Cíclico", "Bens de Consumo"), "TECN3": ("Consumo Cíclico", "Bens de Consumo"),
    "UCAS3": ("Consumo Cíclico", "Bens de Consumo"), "VSTE3": ("Consumo Cíclico", "Bens de Consumo"),
    "VULC3": ("Consumo Cíclico", "Bens de Consumo"), "WHRL3": ("Consumo Cíclico", "Bens de Consumo"),
    "WHRL4": ("Consumo Cíclico", "Bens de Consumo"), "BMKS3": ("Consumo Cíclico", "Bens de Consumo"),
    "ESTR4": ("Consumo Cíclico", "Bens de Consumo"),

    # Têxtil
    "CEDO4": ("Consumo Cíclico", "Têxtil"), "CTKA4": ("Consumo Cíclico", "Têxtil"),
    "CTSA3": ("Consumo Cíclico", "Têxtil"), "DOHL4": ("Consumo Cíclico", "Têxtil"),
    "PTNT4": ("Consumo Cíclico", "Têxtil"),

    # Consumo Não Cíclico - Alimentos e Bebidas
    "ABEV3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "AGRO3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "AZZA3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "BEEF3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "BRFS3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "CAML3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "JALL3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "MDIA3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "MEAL3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "MRFG3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "NUTR3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "SLCE3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "SMTO3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "SOJA3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),

    # Bens Industriais - Máquinas e Equipamentos
    "AERI3": ("Bens Industriais", "Máquinas e Equipamentos"), "ARML3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "DXCO3": ("Bens Industriais", "Máquinas e Equipamentos"), "EALT3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "EALT4": ("Bens Industriais", "Máquinas e Equipamentos"), "EMBR3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "EPAR3": ("Bens Industriais", "Máquinas e Equipamentos"), "FRAS3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "KEPL3": ("Bens Industriais", "Máquinas e Equipamentos"), "LEVE3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "LUPA3": ("Bens Industriais", "Máquinas e Equipamentos"), "MGEL4": ("Bens Industriais", "Máquinas e Equipamentos"),
    "MTSA4": ("Bens Industriais", "Máquinas e Equipamentos"), "MYPK3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "POMO3": ("Bens Industriais", "Máquinas e Equipamentos"), "POMO4": ("Bens Industriais", "Máquinas e Equipamentos"),
    "PTBL3": ("Bens Industriais", "Máquinas e Equipamentos"), "RAPT3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "RAPT4": ("Bens Industriais", "Máquinas e Equipamentos"), "RCSL3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "RCSL4": ("Bens Industriais", "Máquinas e Equipamentos"), "ROMI3": ("Bens Industriais", "Máquinas e Equipamentos"),
    "RSUL4": ("Bens Industriais", "Máquinas e Equipamentos"), "SHUL4": ("Bens Industriais", "Máquinas e Equipamentos"),
    "TASA3": ("Bens Industriais", "Máquinas e Equipamentos"), "TASA4": ("Bens Industriais", "Máquinas e Equipamentos"),
    "TUPY3": ("Bens Industriais", "Máquinas e Equipamentos"), "WEGE3": ("Bens Industriais", "Máquinas e Equipamentos"),

    # Bens Industriais - Transporte e Logística
    "AZUL4": ("Bens Industriais", "Transporte e Logística"), "ECOR3": ("Bens Industriais", "Transporte e Logística"),
    "GOLL4": ("Bens Industriais", "Transporte e Logística"), "HBSA3": ("Bens Industriais", "Transporte e Logística"),
    "JSLG3": ("Bens Industriais", "Transporte e Logística"), "LOGN3": ("Bens Industriais", "Transporte e Logística"),
    "LUXM4": ("Bens Industriais", "Transporte e Logística"), "MOTV3": ("Bens Industriais", "Transporte e Logística"),
    "PORT3": ("Bens Industriais", "Transporte e Logística"), "RAIL3": ("Bens Industriais", "Transporte e Logística"),
    "SEQL3": ("Bens Industriais", "Transporte e Logística"), "SIMH3": ("Bens Industriais", "Transporte e Logística"),
    "STBP3": ("Bens Industriais", "Transporte e Logística"), "TGMA3": ("Bens Industriais", "Transporte e Logística"),
    "TPIS3": ("Bens Industriais", "Transporte e Logística"),

    # Saúde
    "AALR3": ("Saúde", "Saúde"), "BALM4": ("Saúde", "Saúde"), "BIOM3": ("Saúde", "Saúde"),
    "BLAU3": ("Saúde", "Saúde"), "DASA3": ("Saúde", "Saúde"), "FLRY3": ("Saúde", "Saúde"),
    "HAPV3": ("Saúde", "Saúde"), "HYPE3": ("Saúde", "Saúde"), "MATD3": ("Saúde", "Saúde"),
    "ODPV3": ("Saúde", "Saúde"), "OFSA3": ("Saúde", "Saúde"), "ONCO3": ("Saúde", "Saúde"),
    "RDOR3": ("Saúde", "Saúde"),

    # Tecnologia da Informação - Software e Serviços de TI
    "ATED3": ("Tecnologia da Informação", "Software e Serviços de TI"), "BMOB3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "CASH3": ("Tecnologia da Informação", "Software e Serviços de TI"), "CSUD3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "DOTZ3": ("Tecnologia da Informação", "Software e Serviços de TI"), "INTB3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "LWSA3": ("Tecnologia da Informação", "Software e Serviços de TI"), "NGRD3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "TOTS3": ("Tecnologia da Informação", "Software e Serviços de TI"), "TRAD3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "VLID3": ("Tecnologia da Informação", "Software e Serviços de TI"), "TOKY3": ("Tecnologia da Informação", "Software e Serviços de TI"),

    # Petróleo, Gás e Biocombustíveis
    "BRAV3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "CGAS5": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "CSAN3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "PETR3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "PETR4": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "PRIO3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "RECV3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "RPMG3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "VBBR3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),

    # Bens Industriais - Serviços Industriais
    "AZEV3": ("Bens Industriais", "Serviços Industriais"), "AZEV4": ("Bens Industriais", "Serviços Industriais"),
    "INEP3": ("Bens Industriais", "Serviços Industriais"), "INEP4": ("Bens Industriais", "Serviços Industriais"),
    "LOGG3": ("Bens Industriais", "Serviços Industriais"), "MILS3": ("Bens Industriais", "Serviços Industriais"),
    "OSXB3": ("Bens Industriais", "Serviços Industriais"), "PRNR3": ("Bens Industriais", "Serviços Industriais"),

    # Comunicações - Telecomunicações
    "BRST3": ("Comunicações", "Telecomunicações"), "DESK3": ("Comunicações", "Telecomunicações"),
    "FIQE3": ("Comunicações", "Telecomunicações"), "OIBR3": ("Comunicações", "Telecomunicações"),
    "OIBR4": ("Comunicações", "Telecomunicações"), "TELB3": ("Comunicações", "Telecomunicações"),
    "TELB4": ("Comunicações", "Telecomunicações"), "TIMS3": ("Comunicações", "Telecomunicações"),
    "VIVT3": ("Comunicações", "Telecomunicações"),

    # Educação
    "ALPK3": ("Educação", "Educação"), "BIED3": ("Educação", "Educação"),
    "COGN3": ("Educação", "Educação"), "CSED3": ("Educação", "Educação"),
    "SEER3": ("Educação", "Educação"), "SMFT3": ("Educação", "Educação"),
    "YDUQ3": ("Educação", "Educação"), "ZAMP3": ("Educação", "Educação"),

    # Consumo Não Cíclico - Comércio e Distribuição
    "AGXY3": ("Consumo Não Cíclico", "Comércio e Distribuição"), "DMVF3": ("Consumo Não Cíclico", "Comércio e Distribuição"),
    "IFCM3": ("Consumo Não Cíclico", "Comércio e Distribuição"), "LVTC3": ("Consumo Não Cíclico", "Comércio e Distribuição"),
    "PFRM3": ("Consumo Não Cíclico", "Comércio e Distribuição"), "VVEO3": ("Consumo Não Cíclico", "Comércio e Distribuição"),
    "WLMM4": ("Consumo Não Cíclico", "Comércio e Distribuição"),

    # Tecnologia da Informação - Hardware e Equipamentos
    "ALLD3": ("Tecnologia da Informação", "Hardware e Equipamentos"), "MLAS3": ("Tecnologia da Informação", "Hardware e Equipamentos"),
    "PDTC3": ("Tecnologia da Informação", "Hardware e Equipamentos"), "POSI3": ("Tecnologia da Informação", "Hardware e Equipamentos"),

    # Serviços Diversos
    "AHEB3": ("Serviços Diversos", "Serviços Diversos"), "AMBP3": ("Serviços Diversos", "Serviços Diversos"),
    "CVCB3": ("Serviços Diversos", "Serviços Diversos"), "ESPA3": ("Serviços Diversos", "Serviços Diversos"),
    "FICT3": ("Serviços Diversos", "Serviços Diversos"), "GGPS3": ("Serviços Diversos", "Serviços Diversos"),
    "OPCT3": ("Serviços Diversos", "Serviços Diversos"), "SHOW3": ("Serviços Diversos", "Serviços Diversos"),
    "VTRU3": ("Serviços Diversos", "Serviços Diversos"), "HOOT4": ("Serviços Diversos", "Serviços Diversos"),
    "REAG3": ("Serviços Diversos", "Serviços Diversos"), "CTAX3": ("Serviços Diversos", "Serviços Diversos"),
}

# Lista de tickers a serem removidos
TICKERS_A_REMOVER = [
    "SNCI11", "WSEC11", "IRIM11", "RBIF11", "EGYR11", "RENV11", "RNR9L", "PPLA11"
]

# --- FUNÇÃO CORRIGIDA ---
def mapear_setores_b3(df):
    """
    Mapeia os tickers para o padrão B3 de Setor e Subsetor usando
    um dicionário completo e robusto.

    Args:
        df (pd.DataFrame): DataFrame com a coluna 'ticker'.

    Returns:
        pd.DataFrame: DataFrame com as novas colunas 'setor_b3' e 'subsetor_b3'.
    """
    # Define o valor padrão para tickers que não forem encontrados no mapeamento
    valor_padrao = ('Indefinido', 'Indefinido')

    # Usa o método .get() que é seguro e retorna o valor padrão se a chave (ticker) não existir.
    # Isso garante que a lista sempre terá o mesmo tamanho do DataFrame.
    lista_de_setores = [MAPEAMENTO_COMPLETO_TICKERS.get(ticker, valor_padrao) for ticker in df['ticker']]

    # Converte a lista de tuplas em duas novas colunas no DataFrame
    df[['setor_b3', 'subsetor_b3']] = pd.DataFrame(lista_de_setores, index=df.index)

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
        
        df_ativos = df_ativos.rename(columns={'stock': 'ticker'})

        # Remover tickers específicos
        df_ativos = df_ativos[~df_ativos['ticker'].isin(TICKERS_A_REMOVER)]

        # Mapeamento de setores (usando a nova lógica)
        df_ativos = mapear_setores_b3(df_ativos)

        # Filtro de setores indefinidos APÓS o mapeamento
        df_ativos = df_ativos[df_ativos['setor_b3'] != 'Indefinido']

        # Renomear outras colunas
        colunas_renomear = {
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

        # Remover colunas desnecessárias
        colunas_remover = [col for col in ['change', 'market_cap', 'close'] if col in df_ativos.columns]
        if colunas_remover:
            df_ativos = df_ativos.drop(columns=colunas_remover)

        # Limpeza final
        df_ativos = df_ativos.fillna('N/A')
        df_ativos = df_ativos.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df_ativos = df_ativos.replace('', 'N/A')
        
        # Validações
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