# -*- coding: utf-8 -*-
"""
📄 Script para extrair e processar dados de ações e fundos da B3.
    Versão 5.0 com salvamento em Parquet e output aprimorado.
    Agora usando yfinance em vez de brapi, filtrando apenas empresas brasileiras via sufixo .SA.
"""
import yfinance as yf
import pandas as pd
from pathlib import Path
import time
import requests
from common import save_to_parquet


# --- MAPEAMENTO DE TICKERS REFINADO (VERSÃO FINAL) ---
MAPEAMENTO_COMPLETO_TICKERS = {
    # Utilidade Pública - Geração de Energia
    "AESB3": ("Utilidade Pública", "Geração de Energia"), "AURE3": ("Utilidade Pública", "Geração de Energia"),
    "ELET3": ("Utilidade Pública", "Geração de Energia"), "ELET5": ("Utilidade Pública", "Geração de Energia"),
    "ELET6": ("Utilidade Pública", "Geração de Energia"), "EMAE4": ("Utilidade Pública", "Geração de Energia"),
    "ENEV3": ("Utilidade Pública", "Geração de Energia"), "ENGI3": ("Utilidade Pública", "Geração de Energia"),
    "ENGI4": ("Utilidade Pública", "Geração de Energia"), "ENGI11": ("Utilidade Pública", "Geração de Energia"),
    "EGIE3": ("Utilidade Pública", "Geração de Energia"), "GEPA3": ("Utilidade Pública", "Geração de Energia"),
    "GEPA4": ("Utilidade Pública", "Geração de Energia"), "ORVR3": ("Utilidade Pública", "Geração de Energia"),
    "RNEW3": ("Utilidade Pública", "Geração de Energia"), "RNEW4": ("Utilidade Pública", "Geração de Energia"),
    "RNEW11": ("Utilidade Pública", "Geração de Energia"), "SRNA3": ("Utilidade Pública", "Geração de Energia"),
    # Utilidade Pública - Transmissão de Energia
    "AFLT3": ("Utilidade Pública", "Transmissão de Energia"), "ALUP3": ("Utilidade Pública", "Transmissão de Energia"),
    "ALUP4": ("Utilidade Pública", "Transmissão de Energia"), "ALUP11": ("Utilidade Pública", "Transmissão de Energia"),
    "ISAE3": ("Utilidade Pública", "Transmissão de Energia"), "ISAE4": ("Utilidade Pública", "Transmissão de Energia"),
    "TAEE3": ("Utilidade Pública", "Transmissão de Energia"), "TAEE4": ("Utilidade Pública", "Transmissão de Energia"),
    "TAEE11": ("Utilidade Pública", "Transmissão de Energia"),
    # Utilidade Pública - Distribuição de Energia
    "CBEE3": ("Utilidade Pública", "Distribuição de Energia"), "CEBR3": ("Utilidade Pública", "Distribuição de Energia"),
    "CEBR5": ("Utilidade Pública", "Distribuição de Energia"), "CEBR6": ("Utilidade Pública", "Distribuição de Energia"),
    "CEEB3": ("Utilidade Pública", "Distribuição de Energia"), "CLSC4": ("Utilidade Pública", "Distribuição de Energia"),
    "CMIG3": ("Utilidade Pública", "Distribuição de Energia"), "CMIG4": ("Utilidade Pública", "Distribuição de Energia"),
    "COCE3": ("Utilidade Pública", "Distribuição de Energia"), "COCE5": ("Utilidade Pública", "Distribuição de Energia"),
    "CPFE3": ("Utilidade Pública", "Distribuição de Energia"), "CPLE3": ("Utilidade Pública", "Distribuição de Energia"),
    "CPLE5": ("Utilidade Pública", "Distribuição de Energia"), "CPLE6": ("Utilidade Pública", "Distribuição de Energia"),
    "EKTR4": ("Utilidade Pública", "Distribuição de Energia"), "ENMT3": ("Utilidade Pública", "Distribuição de Energia"),
    "ENMT4": ("Utilidade Pública", "Distribuição de Energia"), "EQMA3B": ("Utilidade Pública", "Distribuição de Energia"),
    "EQPA3": ("Utilidade Pública", "Distribuição de Energia"), "EQTL3": ("Utilidade Pública", "Distribuição de Energia"),
    "LIGT3": ("Utilidade Pública", "Distribuição de Energia"), "NEOE3": ("Utilidade Pública", "Distribuição de Energia"),
    "REDE3": ("Utilidade Pública", "Distribuição de Energia"),
    # Utilidade Pública - Saneamento
    "CSMG3": ("Utilidade Pública", "Saneamento"), "SAPR3": ("Utilidade Pública", "Saneamento"),
    "SAPR4": ("Utilidade Pública", "Saneamento"), "SAPR11": ("Utilidade Pública", "Saneamento"),
    "SBSP3": ("Utilidade Pública", "Saneamento"),
    # Petróleo, Gás e Biocombustíveis
    "CGAS3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "CSAN3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "PETR3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "PETR4": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "PRIO3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "RECV3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "RPMG3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "VBBR3": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    "CGAS5": ("Petróleo, Gás e Biocombustíveis", "Petróleo, Gás e Biocombustíveis"),
    # Financeiro e Outros - Bancos
    "ABCB4": ("Financeiro e Outros", "Bancos"), "BAZA3": ("Financeiro e Outros", "Bancos"),
    "BBDC3": ("Financeiro e Outros", "Bancos"), "BBDC4": ("Financeiro e Outros", "Bancos"),
    "BEES3": ("Financeiro e Outros", "Bancos"), "BEES4": ("Financeiro e Outros", "Bancos"),
    "BGIP3": ("Financeiro e Outros", "Bancos"), "BGIP4": ("Financeiro e Outros", "Bancos"),
    "BMEB3": ("Financeiro e Outros", "Bancos"), "BMEB4": ("Financeiro e Outros", "Bancos"),
    "BMIN4": ("Financeiro e Outros", "Bancos"), "BMGB4": ("Financeiro e Outros", "Bancos"),
    "BNBR3": ("Financeiro e Outros", "Bancos"), "BPAC3": ("Financeiro e Outros", "Bancos"),
    "BPAC5": ("Financeiro e Outros", "Bancos"), "BPAC11": ("Financeiro e Outros", "Bancos"),
    "BPAN4": ("Financeiro e Outros", "Bancos"), "BRSR3": ("Financeiro e Outros", "Bancos"),
    "BRSR6": ("Financeiro e Outros", "Bancos"), "BSLI3": ("Financeiro e Outros", "Bancos"),
    "BSLI4": ("Financeiro e Outros", "Bancos"), "ITUB3": ("Financeiro e Outros", "Bancos"),
    "ITUB4": ("Financeiro e Outros", "Bancos"), "PINE3": ("Financeiro e Outros", "Bancos"),
    "PINE4": ("Financeiro e Outros", "Bancos"), "SANB3": ("Financeiro e Outros", "Bancos"),
    "SANB4": ("Financeiro e Outros", "Bancos"), "SANB11": ("Financeiro e Outros", "Bancos"),
    "BBAS3": ("Financeiro e Outros", "Bancos"),
    # Financeiro e Outros - Seguros
    "BBSE3": ("Financeiro e Outros", "Seguros"), "CXSE3": ("Financeiro e Outros", "Seguros"),
    "IRBR3": ("Financeiro e Outros", "Seguros"), "PSSA3": ("Financeiro e Outros", "Seguros"),
    "QUAL3": ("Financeiro e Outros", "Seguros"), "WIZC3": ("Financeiro e Outros", "Seguros"),
    # Financeiro e Outros - Holdings e Outros Serviços Financeiros
    "B3SA3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "BRAP3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "BRAP4": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "CIEL3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "GETT3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "GETT4": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "ITSA3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "ITSA4": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "MNPR3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "NEXP3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "REAG3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "RPAD5": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "BRBI11": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    # Financeiro e Outros - Incorporação e Construção
    "CALI3": ("Financeiro e Outros", "Incorporação e Construção"), "CURY3": ("Financeiro e Outros", "Incorporação e Construção"),
    "CYRE3": ("Financeiro e Outros", "Incorporação e Construção"), "DIRR3": ("Financeiro e Outros", "Incorporação e Construção"),
    "EVEN3": ("Financeiro e Outros", "Incorporação e Construção"), "EZTC3": ("Financeiro e Outros", "Incorporação e Construção"),
    "GFSA3": ("Financeiro e Outros", "Incorporação e Construção"), "HBOR3": ("Financeiro e Outros", "Incorporação e Construção"),
    "HBRE3": ("Financeiro e Outros", "Incorporação e Construção"), "JFEN3": ("Financeiro e Outros", "Incorporação e Construção"),
    "LAVV3": ("Financeiro e Outros", "Incorporação e Construção"), "MDNE3": ("Financeiro e Outros", "Incorporação e Construção"),
    "MRVE3": ("Financeiro e Outros", "Incorporação e Construção"), "MTRE3": ("Financeiro e Outros", "Incorporação e Construção"),
    "PDGR3": ("Financeiro e Outros", "Incorporação e Construção"), "PLPL3": ("Financeiro e Outros", "Incorporação e Construção"),
    "RDNI3": ("Financeiro e Outros", "Incorporação e Construção"), "RSID3": ("Financeiro e Outros", "Incorporação e Construção"),
    "TCSA3": ("Financeiro e Outros", "Incorporação e Construção"), "TEND3": ("Financeiro e Outros", "Incorporação e Construção"),
    "TPIS3": ("Financeiro e Outros", "Incorporação e Construção"), "TRIS3": ("Financeiro e Outros", "Incorporação e Construção"),
    "VIVR3": ("Financeiro e Outros", "Incorporação e Construção"), "LPSB3": ("Financeiro e Outros", "Incorporação e Construção"),
    "CCTY3": ("Financeiro e Outros", "Incorporação e Construção"),
    # Financeiro e Outros - Propriedades e Locação
    "ALOS3": ("Financeiro e Outros", "Propriedades e Locação"), "AVLL3": ("Financeiro e Outros", "Propriedades e Locação"),
    "GSHP3": ("Financeiro e Outros", "Propriedades e Locação"), "IGTI3": ("Financeiro e Outros", "Propriedades e Locação"),
    "JHSF3": ("Financeiro e Outros", "Propriedades e Locação"), "LAND3": ("Financeiro e Outros", "Propriedades e Locação"),
    "LOGG3": ("Financeiro e Outros", "Propriedades e Locação"), "MELK3": ("Financeiro e Outros", "Propriedades e Locação"),
    "MULT3": ("Financeiro e Outros", "Propriedades e Locação"), "PEAB3": ("Financeiro e Outros", "Propriedades e Locação"),
    "PEAB4": ("Financeiro e Outros", "Propriedades e Locação"), "SCAR3": ("Financeiro e Outros", "Propriedades e Locação"),
    "SYNE3": ("Financeiro e Outros", "Propriedades e Locação"),
    # Materiais Básicos - Mineração e Siderurgia
    "CBAV3": ("Materiais Básicos", "Mineração e Siderurgia"), "CMIN3": ("Materiais Básicos", "Mineração e Siderurgia"),
    "CSNA3": ("Materiais Básicos", "Mineração e Siderurgia"), "FESA3": ("Materiais Básicos", "Mineração e Siderurgia"),
    "FESA4": ("Materiais Básicos", "Mineração e Siderurgia"), "GGBR3": ("Materiais Básicos", "Mineração e Siderurgia"),
    "GGBR4": ("Materiais Básicos", "Mineração e Siderurgia"), "GOAU3": ("Materiais Básicos", "Mineração e Siderurgia"),
    "GOAU4": ("Materiais Básicos", "Mineração e Siderurgia"), "MBRF3": ("Materiais Básicos", "Mineração e Siderurgia"),
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
    "CRPG5": ("Materiais Básicos", "Química e Petroquímica"), "CRPG6": ("Materiais Básicos", "Química e Petroquímica"),
    "DEXP3": ("Materiais Básicos", "Química e Petroquímica"), "DEXP4": ("Materiais Básicos", "Química e Petroquímica"),
    "FHER3": ("Materiais Básicos", "Química e Petroquímica"), "SNSY5": ("Materiais Básicos", "Química e Petroquímica"),
    "UNIP3": ("Materiais Básicos", "Química e Petroquímica"), "UNIP5": ("Materiais Básicos", "Química e Petroquímica"),
    "UNIP6": ("Materiais Básicos", "Química e Petroquímica"), "VITT3": ("Materiais Básicos", "Química e Petroquímica"),
    # Consumo Cíclico - Comércio Varejista
    "AMAR3": ("Consumo Cíclico", "Comércio Varejista"), "AMER3": ("Consumo Cíclico", "Comércio Varejista"),
    "AMOB3": ("Consumo Cíclico", "Comércio Varejista"), "ASAI3": ("Consumo Cíclico", "Comércio Varejista"),
    "BHIA3": ("Consumo Cíclico", "Comércio Varejista"), "CGRA3": ("Consumo Cíclico", "Comércio Varejista"),
    "CGRA4": ("Consumo Cíclico", "Comércio Varejista"), "ENJU3": ("Consumo Cíclico", "Comércio Varejista"),
    "GMAT3": ("Consumo Cíclico", "Comércio Varejista"), "LJQQ3": ("Consumo Cíclico", "Comércio Varejista"),
    "MGLU3": ("Consumo Cíclico", "Comércio Varejista"), "PCAR3": ("Consumo Cíclico", "Comércio Varejista"),
    "PETZ3": ("Consumo Cíclico", "Comércio Varejista"), "PGMN3": ("Consumo Cíclico", "Comércio Varejista"),
    "PNVL3": ("Consumo Cíclico", "Comércio Varejista"), "RADL3": ("Consumo Cíclico", "Comércio Varejista"),
    "TFCO4": ("Consumo Cíclico", "Comércio Varejista"), "VIVA3": ("Consumo Cíclico", "Comércio Varejista"),
    "WEST3": ("Consumo Cíclico", "Comércio Varejista"),
    # Consumo Cíclico - Calçados e Vestuário
    "ALPA3": ("Consumo Cíclico", "Calçados e Vestuário"), "ALPA4": ("Consumo Cíclico", "Calçados e Vestuário"),
    "GRND3": ("Consumo Cíclico", "Calçados e Vestuário"), "VULC3": ("Consumo Cíclico", "Calçados e Vestuário"),
    "SBFG3": ("Consumo Cíclico", "Calçados e Vestuário"), "LREN3": ("Consumo Cíclico", "Calçados e Vestuário"),
    "CEAB3": ("Consumo Cíclico", "Calçados e Vestuário"), "GUAR3": ("Consumo Cíclico", "Calçados e Vestuário"),
    # Consumo Cíclico - Consumo Diverso (inclui Têxtil e Eletrodomésticos)
    "AZTE3": ("Consumo Cíclico", "Consumo Diverso"), "CAMB3": ("Consumo Cíclico", "Consumo Diverso"),
    "MNDL3": ("Consumo Cíclico", "Consumo Diverso"), "NATU3": ("Consumo Cíclico", "Consumo Diverso"),
    "TECN3": ("Consumo Cíclico", "Consumo Diverso"), "UCAS3": ("Consumo Cíclico", "Consumo Diverso"),
    "VSTE3": ("Consumo Cíclico", "Consumo Diverso"), "BMKS3": ("Consumo Cíclico", "Consumo Diverso"),
    "ESTR4": ("Consumo Cíclico", "Consumo Diverso"), "WHRL3": ("Consumo Cíclico", "Consumo Diverso"),
    "WHRL4": ("Consumo Cíclico", "Consumo Diverso"), "CEDO3": ("Consumo Cíclico", "Consumo Diverso"),
    "CEDO4": ("Consumo Cíclico", "Consumo Diverso"), "CTKA4": ("Consumo Cíclico", "Consumo Diverso"),
    "CTSA3": ("Consumo Cíclico", "Consumo Diverso"), "CTSA4": ("Consumo Cíclico", "Consumo Diverso"),
    "DOHL4": ("Consumo Cíclico", "Consumo Diverso"), "PTNT3": ("Consumo Cíclico", "Consumo Diverso"),
    "PTNT4": ("Consumo Cíclico", "Consumo Diverso"),
    # Consumo Não Cíclico - Alimentos e Bebidas (inclui Produtos de Limpeza)
    "ABEV3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "AGRO3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "BEEF3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "BRFS3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "CAML3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "JALL3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "MDIA3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "MEAL3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "MOAR3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "MRFG3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "NUTR3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "SLCE3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "SMTO3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "SOJA3": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    "TTEN3": ("Consumo Não Cíclico", "Alimentos e Bebidas"), "BOBR4": ("Consumo Não Cíclico", "Alimentos e Bebidas"),
    # Consumo Não Cíclico - Comércio e Distribuição
    "AGXY3": ("Consumo Não Cíclico", "Comércio e Distribuição"), "DMVF3": ("Consumo Não Cíclico", "Comércio e Distribuição"),
    "IFCM3": ("Consumo Não Cíclico", "Comércio e Distribuição"), "LVTC3": ("Consumo Não Cíclico", "Comércio e Distribuição"),
    "PFRM3": ("Consumo Não Cíclico", "Comércio e Distribuição"), "RAIZ4": ("Consumo Não Cíclico", "Comércio e Distribuição"),
    "UGPA3": ("Consumo Não Cíclico", "Comércio e Distribuição"), "VVEO3": ("Consumo Não Cíclico", "Comércio e Distribuição"),
    "WLMM4": ("Consumo Não Cíclico", "Comércio e Distribuição"),
    # Bens Industriais - Máquinas e Motores
    "AERI3": ("Bens Industriais", "Máquinas e Motores"), "ARML3": ("Bens Industriais", "Máquinas e Motores"),
    "BDLL3": ("Bens Industriais", "Máquinas e Motores"), "BDLL4": ("Bens Industriais", "Máquinas e Motores"),
    "DXCO3": ("Bens Industriais", "Máquinas e Motores"), "EALT3": ("Bens Industriais", "Máquinas e Motores"),
    "EALT4": ("Bens Industriais", "Máquinas e Motores"), "FRIO3": ("Bens Industriais", "Máquinas e Motores"),
    "HAGA3": ("Bens Industriais", "Máquinas e Motores"), "HAGA4": ("Bens Industriais", "Máquinas e Motores"),
    "HETA4": ("Bens Industriais", "Máquinas e Motores"), "KEPL3": ("Bens Industriais", "Máquinas e Motores"),
    "LUPA3": ("Bens Industriais", "Máquinas e Motores"), "MGEL4": ("Bens Industriais", "Máquinas e Motores"),
    "MTSA4": ("Bens Industriais", "Máquinas e Motores"), "ROMI3": ("Bens Industriais", "Máquinas e Motores"),
    "RSUL4": ("Bens Industriais", "Máquinas e Motores"), "SHUL4": ("Bens Industriais", "Máquinas e Motores"),
    "WEGE3": ("Bens Industriais", "Máquinas e Motores"),
    # Bens Industriais - Transporte e Componentes
    "EMBR3": ("Bens Industriais", "Transporte e Componentes"), "FRAS3": ("Bens Industriais", "Transporte e Componentes"),
    "LEVE3": ("Bens Industriais", "Transporte e Componentes"), "MWET4": ("Bens Industriais", "Transporte e Componentes"),
    "MYPK3": ("Bens Industriais", "Transporte e Componentes"), "PLAS3": ("Bens Industriais", "Transporte e Componentes"),
    "POMO3": ("Bens Industriais", "Transporte e Componentes"), "POMO4": ("Bens Industriais", "Transporte e Componentes"),
    "PTBL3": ("Bens Industriais", "Transporte e Componentes"), "RAPT3": ("Bens Industriais", "Transporte e Componentes"),
    "RAPT4": ("Bens Industriais", "Transporte e Componentes"), "RCSL3": ("Bens Industriais", "Transporte e Componentes"),
    "RCSL4": ("Bens Industriais", "Transporte e Componentes"), "TASA3": ("Bens Industriais", "Transporte e Componentes"),
    "TASA4": ("Bens Industriais", "Transporte e Componentes"), "TUPY3": ("Bens Industriais", "Transporte e Componentes"),
    # Bens Industriais - Logística e Mobilidade
    "AZUL4": ("Bens Industriais", "Logística e Mobilidade"), "ECOR3": ("Bens Industriais", "Logística e Mobilidade"),
    "GOLL4": ("Bens Industriais", "Logística e Mobilidade"), "HBSA3": ("Bens Industriais", "Logística e Mobilidade"),
    "JSLG3": ("Bens Industriais", "Logística e Mobilidade"), "LOGN3": ("Bens Industriais", "Logística e Mobilidade"),
    "LUXM4": ("Bens Industriais", "Logística e Mobilidade"), "MOTV3": ("Bens Industriais", "Logística e Mobilidade"),
    "MOVI3": ("Bens Industriais", "Logística e Mobilidade"), "PORT3": ("Bens Industriais", "Logística e Mobilidade"),
    "RAIL3": ("Bens Industriais", "Logística e Mobilidade"), "RENT3": ("Bens Industriais", "Logística e Mobilidade"),
    "SEQL3": ("Bens Industriais", "Logística e Mobilidade"), "SIMH3": ("Bens Industriais", "Logística e Mobilidade"),
    "STBP3": ("Bens Industriais", "Logística e Mobilidade"), "TGMA3": ("Bens Industriais", "Logística e Mobilidade"),
    "VAMO3": ("Bens Industriais", "Logística e Mobilidade"),
    # Bens Industriais - Serviços Industriais
    "AZEV3": ("Bens Industriais", "Serviços Industriais"), "AZEV4": ("Bens Industriais", "Serviços Industriais"),
    "EPAR3": ("Bens Industriais", "Serviços Industriais"), "INEP3": ("Bens Industriais", "Serviços Industriais"),
    "INEP4": ("Bens Industriais", "Serviços Industriais"), "MILS3": ("Bens Industriais", "Serviços Industriais"),
    "OSXB3": ("Bens Industriais", "Serviços Industriais"), "PRNR3": ("Bens Industriais", "Serviços Industriais"),
    # Saúde - Hospitais e Análises Clínicas
    "AALR3": ("Saúde", "Hospitais e Análises Clínicas"), "DASA3": ("Saúde", "Hospitais e Análises Clínicas"),
    "FLRY3": ("Saúde", "Hospitais e Análises Clínicas"), "HAPV3": ("Saúde", "Hospitais e Análises Clínicas"),
    "ONCO3": ("Saúde", "Hospitais e Análises Clínicas"), "RDOR3": ("Saúde", "Hospitais e Análises Clínicas"),
    # Saúde - Produtos e Equipamentos Médicos
    "BALM4": ("Saúde", "Produtos e Equipamentos Médicos"), "BIED3": ("Saúde", "Produtos e Equipamentos Médicos"),
    "BIOM3": ("Saúde", "Produtos e Equipamentos Médicos"), "BLAU3": ("Saúde", "Produtos e Equipamentos Médicos"),
    "HYPE3": ("Saúde", "Produtos e Equipamentos Médicos"), "MATD3": ("Saúde", "Produtos e Equipamentos Médicos"),
    "ODPV3": ("Saúde", "Produtos e Equipamentos Médicos"), "OFSA3": ("Saúde", "Produtos e Equipamentos Médicos"),
    # Tecnologia da Informação - Software e Serviços de TI
    "ATED3": ("Tecnologia da Informação", "Software e Serviços de TI"), "BMOB3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "CASH3": ("Tecnologia da Informação", "Software e Serviços de TI"), "CSUD3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "DOTZ3": ("Tecnologia da Informação", "Software e Serviços de TI"), "INTB3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "LWSA3": ("Tecnologia da Informação", "Software e Serviços de TI"), "NGRD3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "TOTS3": ("Tecnologia da Informação", "Software e Serviços de TI"), "TRAD3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    "VLID3": ("Tecnologia da Informação", "Software e Serviços de TI"), "TOKY3": ("Tecnologia da Informação", "Software e Serviços de TI"),
    # Tecnologia da Informação - Hardware e Equipamentos
    "ALLD3": ("Tecnologia da Informação", "Hardware e Equipamentos"), "MLAS3": ("Tecnologia da Informação", "Hardware e Equipamentos"),
    "PDTC3": ("Tecnologia da Informação", "Hardware e Equipamentos"), "POSI3": ("Tecnologia da Informação", "Hardware e Equipamentos"),
    # Comunicações - Telecomunicações
    "BRST3": ("Comunicações", "Telecomunicações"), "DESK3": ("Comunicações", "Telecomunicações"),
    "FIQE3": ("Comunicações", "Telecomunicações"), "OIBR3": ("Comunicações", "Telecomunicações"),
    "OIBR4": ("Comunicações", "Telecomunicações"), "TELB3": ("Comunicações", "Telecomunicações"),
    "TELB4": ("Comunicações", "Telecomunicações"), "TIMS3": ("Comunicações", "Telecomunicações"),
    "VIVT3": ("Comunicações", "Telecomunicações"),
    # Educação
    "ANIM3": ("Educação", "Educação"), "ALPK3": ("Educação", "Educação"),
    "COGN3": ("Educação", "Educação"), "CSED3": ("Educação", "Educação"),
    "SEER3": ("Educação", "Educação"), "SMFT3": ("Educação", "Educação"),
    "YDUQ3": ("Educação", "Educação"), "ZAMP3": ("Educação", "Educação"),
    # Serviços Diversos
    "AHEB3": ("Serviços Diversos", "Serviços Diversos"), "AMBP3": ("Serviços Diversos", "Serviços Diversos"),
    "CTAX3": ("Serviços Diversos", "Serviços Diversos"), "CVCB3": ("Serviços Diversos", "Serviços Diversos"),
    "ESPA3": ("Serviços Diversos", "Serviços Diversos"), "FICT3": ("Serviços Diversos", "Serviços Diversos"),
    "FIEI3": ("Serviços Diversos", "Serviços Diversos"), "GGPS3": ("Serviços Diversos", "Serviços Diversos"),
    "HOOT4": ("Serviços Diversos", "Serviços Diversos"), "OPCT3": ("Serviços Diversos", "Serviços Diversos"),
    "RVEE3": ("Serviços Diversos", "Serviços Diversos"), "SHOW3": ("Serviços Diversos", "Serviços Diversos"),
    "VTRU3": ("Serviços Diversos", "Serviços Diversos"), "HBTS5": ("Serviços Diversos", "Serviços Diversos"),
}

# Lista de tickers a serem removidos
TICKERS_A_REMOVER = [
    #"SNCI11", "WSEC11", "IRIM11", "RBIF11", "EGYR11", "RENV11", "RNR9L", "PPLA11",
]

def mapear_setores_b3(df):
    """
    Mapeia os tickers para o padrão B3 de Setor e Subsetor usando
    um dicionário completo e robusto.
    """
    valor_padrao = ('Indefinido', 'Indefinido')
   
    # Gera as listas de setores e subsetores de forma explícita
    setores = [MAPEAMENTO_COMPLETO_TICKERS.get(ticker, valor_padrao)[0] for ticker in df['ticker']]
    subsetores = [MAPEAMENTO_COMPLETO_TICKERS.get(ticker, valor_padrao)[1] for ticker in df['ticker']]
   
    # Atribui as listas diretamente às novas colunas
    df['setor_b3'] = setores
    df['subsetor_b3'] = subsetores
   
    return df

def extrair_dados_yfinance():
    """
    Extrai, filtra e processa dados de ativos da B3 usando yfinance, mas busca o logo da API Brapi.
    """
    print("Iniciando extração de dados...")
    start_time = time.time()

    # 1. Buscar logos da API Brapi
    print("Buscando logos da API Brapi...")
    logo_map = {}
    try:
        response = requests.get("https://brapi.dev/api/quote/list", timeout=20)
        response.raise_for_status()
        brapi_data = response.json()
        for stock in brapi_data.get('stocks', []):
            if 'stock' in stock and 'logo' in stock:
                logo_map[stock['stock']] = stock['logo']
        print(f"{len(logo_map)} logos encontrados.")
    except Exception as e:
        print(f"Não foi possível buscar logos da Brapi: {e}. Os logos ficarão em branco.")

    # --- MAPEAMENTO DE LOGOS PARA TICKERS SEM LOGO ---
    LOGO_MAPPING = {
        "ELET5": "ELET3",
        "RNEW11": "RNEW3",
        "CEBR5": "CEBR3",
        "CPLE5": "CPLE3",
        "CGAS3": "CGAS5",
        "BGIP3": "BGIP4",
        "BMEB3": "BMEB4",
        "CRPG3": "CRPG5",
        "CRPG6": "CRPG5",
        "CEDO3": "CEDO4",
        "CTSA3": "CTSA4",
        "TELB3": "TELB4",
    }

    print("Verificando e atribuindo logos ausentes...")
    logos_atribuidos = 0
    for ticker_sem_logo, ticker_com_logo in LOGO_MAPPING.items():
        # Garante que o ticker com logo existe no mapa e tem um logo válido
        if ticker_com_logo in logo_map and logo_map[ticker_com_logo]:
            # Atribui o logo se o ticker sem logo não tiver um
            if ticker_sem_logo not in logo_map or not logo_map.get(ticker_sem_logo):
                logo_map[ticker_sem_logo] = logo_map[ticker_com_logo]
                logos_atribuidos += 1

    if logos_atribuidos > 0:
        print(f"{logos_atribuidos} logos foram atribuídos com sucesso a partir do mapeamento.")
    else:
        print("Nenhum logo novo precisou ser atribuído pelo mapeamento.")

    try:
        # 2. Processar tickers com yfinance
        tickers = [ticker for ticker in MAPEAMENTO_COMPLETO_TICKERS.keys() if ticker not in TICKERS_A_REMOVER]

        dados = []
        tickers_nao_mapeados = set() # Set to collect all tickers not added to acoes_e_fundos

        print("Processando tickers com yfinance...")
        for ticker in tickers:
            ticker_yf = f"{ticker}.SA"
            try:
                yf_ticker = yf.Ticker(ticker_yf)
                info = yf_ticker.info

                empresa = info.get('longName') or info.get('shortName') or f"{ticker} - Não Especificado"
                setor_gl = info.get('sector', 'Indefinido')
                volume = info.get('averageVolume', 0)
                logo = logo_map.get(ticker, '') # Get logo from our map
                tipo = info.get('quoteType', 'stock').lower()

                if tipo != 'equity':
                    tickers_nao_mapeados.add(ticker)
                    continue

                dados.append({
                    'ticker': ticker,
                    'empresa': empresa,
                    'volume': volume,
                    'logo': logo, # New logo
                    'setor_gl': setor_gl,
                    'tipo': tipo
                })

                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Erro ao processar {ticker} com yfinance: {e}")
                tickers_nao_mapeados.add(ticker) # Add to non-mapped list
                continue
        
        if not dados:
            print("❌ Nenhum ativo encontrado via yfinance.")
            # Salva tickers não mapeados mesmo que nenhum ativo seja encontrado
            if tickers_nao_mapeados:
                print(f"⚠️ {len(tickers_nao_mapeados)} tickers não foram adicionados.")
                df_nao_mapeados = pd.DataFrame({'ticker': list(tickers_nao_mapeados)})
                save_to_parquet(df_nao_mapeados, "tickers_nao_mapeados")
            return None

        df_ativos = pd.DataFrame(dados)

        # 3. Mapear setores
        df_ativos = mapear_setores_b3(df_ativos)

        # Adicionar tickers com setor indefinido aos não mapeados
        indefinidos = df_ativos[df_ativos['setor_b3'] == 'Indefinido']['ticker'].tolist()
        for ticker in indefinidos:
            tickers_nao_mapeados.add(ticker)

        # Filtrar indefinidos
        df_ativos = df_ativos[df_ativos['setor_b3'] != 'Indefinido']

        df_ativos['empresa'] = df_ativos['empresa'].fillna(df_ativos['ticker'] + ' - Não Especificado')

        colunas_manter = [
            'ticker', 'empresa', 'volume', 'logo', 'setor_gl', 'tipo', 'setor_b3', 'subsetor_b3'
        ]
        df_ativos = df_ativos[colunas_manter]

        if len(df_ativos) == 0:
            print("DataFrame vazio após filtros! Nenhum arquivo será salvo.")
            return None

        # Salvar tickers não mapeados
        if tickers_nao_mapeados:
            print(f"AVISO: {len(tickers_nao_mapeados)} tickers não foram adicionados ao arquivo principal.")
            df_nao_mapeados = pd.DataFrame({'ticker': sorted(list(tickers_nao_mapeados))})
            save_to_parquet(df_nao_mapeados, "tickers_nao_mapeados")

        save_to_parquet(df_ativos, "acoes_e_fundos")
        elapsed_time = time.time() - start_time
        print(f"SUCESSO: Processamento concluído em {elapsed_time:.2f}s.")

        return df_ativos
    except Exception as e:
        print(f"ERRO: Ocorreu um erro inesperado no processamento principal: {e}")
        return None

if __name__ == "__main__":
    extrair_dados_yfinance()
