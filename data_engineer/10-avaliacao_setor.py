# -*- coding: utf-8 -*-
"""
Avaliação de desempenho por Setor e Subsetor (padrão B3)
"""

from pathlib import Path
import pandas as pd
import numpy as np

# --- INÍCIO: Lógica de Fallback copiada de 01-acoes_e_fundos.py ---

MAPEAMENTO_COMPLETO_TICKERS = {
    # Utilidade Pública - Geração de Energia
    "AURE3": ("Utilidade Pública", "Geração de Energia"), "AESB3": ("Utilidade Pública", "Geração de Energia"),
    "ELET3": ("Utilidade Pública", "Geração de Energia"), "ELET6": ("Utilidade Pública", "Geração de Energia"),
    "EMAE4": ("Utilidade Pública", "Geração de Energia"), "ENEV3": ("Utilidade Pública", "Geração de Energia"),
    "ENGI3": ("Utilidade Pública", "Geração de Energia"), "ENGI4": ("Utilidade Pública", "Geração de Energia"),
    "ENGI11": ("Utilidade Pública", "Geração de Energia"),"EGIE3": ("Utilidade Pública", "Geração de Energia"),
    "GEPA3": ("Utilidade Pública", "Geração de Energia"), "GEPA4": ("Utilidade Pública", "Geração de Energia"),
    "ORVR3": ("Utilidade Pública", "Geração de Energia"), "RNEW3": ("Utilidade Pública", "Geração de Energia"),
    "RNEW4": ("Utilidade Pública", "Geração de Energia"), "RNEW11": ("Utilidade Pública", "Geração de Energia"),
    "SRNA3": ("Utilidade Pública", "Geração de Energia"),

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
    "BRAP4": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "ITSA3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "ITSA4": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "CIEL3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "GETT3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "GETT4": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "MNPR3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "NEXP3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),
    "REAG3": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"), "RPAD5": ("Financeiro e Outros", "Holdings e Outros Serviços Financeiros"),

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

    # Financeiro e Outros - Propriedades e Locação
    "ALOS3": ("Financeiro e Outros", "Propriedades e Locação"), "AVLL3": ("Financeiro e Outros", "Propriedades e Locação"),
    "GSHP3": ("Financeiro e Outros", "Propriedades e Locação"), "IGTI3": ("Financeiro e Outros", "Propriedades e Locação"),
    "JHSF3": ("Financeiro e Outros", "Propriedades e Locação"), "LAND3": ("Financeiro e Outros", "Propriedades e Locação"),
    "LOGG3": ("Financeiro e Outros", "Propriedades e Locação"), "MELK3": ("Financeiro e Outros", "Propriedades e Locação"),
    "MULT3": ("Financeiro e Outros", "Propriedades e Locação"), "PEAB4": ("Financeiro e Outros", "Propriedades e Locação"),
    "SCAR3": ("Financeiro e Outros", "Propriedades e Locação"), "SYNE3": ("Financeiro e Outros", "Propriedades e Locação"),

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
    "BRKM6": ("Materiais Básicos", "Química e Petroquímica"), "CRPG6": ("Materiais Básicos", "Química e Petroquímica"),
    "CRPG3": ("Materiais Básicos", "Química e Petroquímica"), "CRPG5": ("Materiais Básicos", "Química e Petroquímica"),
    "DEXP3": ("Materiais Básicos", "Química e Petroquímica"), "DEXP4": ("Materiais Básicos", "Química e Petroquímica"),
    "FHER3": ("Materiais Básicos", "Química e Petroquímica"), "SNSY5": ("Materiais Básicos", "Química e Petroquímica"),
    "UNIP3": ("Materiais Básicos", "Química e Petroquímica"), "UNIP6": ("Materiais Básicos", "Química e Petroquímica"),
    "VITT3": ("Materiais Básicos", "Química e Petroquímica"),

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
    "WHRL4": ("Consumo Cíclico", "Consumo Diverso"), "CEDO4": ("Consumo Cíclico", "Consumo Diverso"),
    "CTKA4": ("Consumo Cíclico", "Consumo Diverso"), "CTSA3": ("Consumo Cíclico", "Consumo Diverso"),
    "CTSA4": ("Consumo Cíclico", "Consumo Diverso"), "DOHL4": ("Consumo Cíclico", "Consumo Diverso"),
    "PTNT3": ("Consumo Cíclico", "Consumo Diverso"), "PTNT4": ("Consumo Cíclico", "Consumo Diverso"),

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
    "ARML3": ("Bens Industriais", "Máquinas e Motores"), "BDLL3": ("Bens Industriais", "Máquinas e Motores"),
    "BDLL4": ("Bens Industriais", "Máquinas e Motores"), "DXCO3": ("Bens Industriais", "Máquinas e Motores"),
    "EALT3": ("Bens Industriais", "Máquinas e Motores"), "EALT4": ("Bens Industriais", "Máquinas e Motores"),
    "HAGA3": ("Bens Industriais", "Máquinas e Motores"), "HAGA4": ("Bens Industriais", "Máquinas e Motores"),
    "HETA4": ("Bens Industriais", "Máquinas e Motores"), "LUPA3": ("Bens Industriais", "Máquinas e Motores"),
    "MGEL4": ("Bens Industriais", "Máquinas e Motores"), "MTSA4": ("Bens Industriais", "Máquinas e Motores"),
    "ROMI3": ("Bens Industriais", "Máquinas e Motores"), "RSUL4": ("Bens Industriais", "Máquinas e Motores"),
    "SHUL4": ("Bens Industriais", "Máquinas e Motores"), "WEGE3": ("Bens Industriais", "Máquinas e Motores"),

    # Bens Industriais - Transporte e Componentes
    "AERI3": ("Bens Industriais", "Transporte e Componentes"), "EMBR3": ("Bens Industriais", "Transporte e Componentes"),
    "FRAS3": ("Bens Industriais", "Transporte e Componentes"), "KEPL3": ("Bens Industriais", "Transporte e Componentes"),
    "LEVE3": ("Bens Industriais", "Transporte e Componentes"), "MWET4": ("Bens Industriais", "Transporte e Componentes"),
    "MYPK3": ("Bens Industriais", "Transporte e Componentes"), "POMO3": ("Bens Industriais", "Transporte e Componentes"),
    "POMO4": ("Bens Industriais", "Transporte e Componentes"), "PTBL3": ("Bens Industriais", "Transporte e Componentes"),
    "RAPT3": ("Bens Industriais", "Transporte e Componentes"), "RAPT4": ("Bens Industriais", "Transporte e Componentes"),
    "RCSL3": ("Bens Industriais", "Transporte e Componentes"), "RCSL4": ("Bens Industriais", "Transporte e Componentes"),
    "TASA3": ("Bens Industriais", "Transporte e Componentes"), "TASA4": ("Bens Industriais", "Transporte e Componentes"),
    "TUPY3": ("Bens Industriais", "Transporte e Componentes"),

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
    "VTRU3": ("Serviços Diversos", "Serviços Diversos"),
}

def mapear_setores_b3(df):
    """
    Mapeia os tickers para o padrão B3 de Setor e Subsetor.
    """
    valor_padrao = ('Indefinido', 'Indefinido')
    # A função de mapeamento precisa da coluna 'ticker'.
    if 'ticker' not in df.columns and 'ticker_base' in df.columns:
        df['ticker'] = df['ticker_base']
    elif 'ticker' not in df.columns and 'stock' in df.columns:
        df = df.rename(columns={'stock': 'ticker'})

    if 'ticker' in df.columns:
        setores = [MAPEAMENTO_COMPLETO_TICKERS.get(ticker, valor_padrao)[0] for ticker in df['ticker']]
        subsetores = [MAPEAMENTO_COMPLETO_TICKERS.get(ticker, valor_padrao)[1] for ticker in df['ticker']]
        df['setor_b3'] = setores
        df['subsetor_b3'] = subsetores
    else:
        # Se não houver coluna de ticker, cria colunas vazias para evitar KeyErrors
        print("AVISO: Não foi possível encontrar a coluna 'ticker', 'ticker_base' ou 'stock'. As colunas de setor não serão criadas.")
        df['setor_b3'] = 'Indefinido'
        df['subsetor_b3'] = 'Indefinido'
    return df

# --- FIM: Lógica de Fallback ---


# --- Funções de Cálculo de Score por Critério ---

def calcular_score_dy(dy_5a_medio):
    if dy_5a_medio >= 10: return 50
    if 8 <= dy_5a_medio < 10: return 40
    if 6 <= dy_5a_medio < 8: return 30
    if 4 <= dy_5a_medio < 6: return 20
    if 2 <= dy_5a_medio < 4: return -10
    return -20

def calcular_score_roe(roe_medio):
    if roe_medio > 25: return 40
    if 20 <= roe_medio <= 25: return 30
    if 15 <= roe_medio < 20: return 20
    if 10 <= roe_medio < 15: return 10
    return 0

def calcular_score_beta(beta_medio):
    if beta_medio < 0.8: return 20
    if 0.8 <= beta_medio <= 1.2: return 10
    if 1.2 < beta_medio <= 1.5: return 0
    return -10

def calcular_score_payout(payout_medio):
    if 30 <= payout_medio <= 60: return 20
    if (20 <= payout_medio < 30) or (60 < payout_medio <= 80): return 10
    return 0

def calcular_score_empresas_boas(contagem):
    if contagem >= 8: return 40
    if 6 <= contagem < 8: return 30
    if 3 <= contagem <= 5: return 20
    if 1 <= contagem <= 2: return 10
    return 0

def calcular_penalidade_empresas_ruins(contagem):
    if contagem >= 6: return -30
    if 3 <= contagem <= 5: return -20
    if 1 <= contagem <= 2: return -10
    return 0

def calcular_score_graham(margem_media):
    if margem_media > 150: return 30
    if 100 <= margem_media <= 150: return 20
    if 50 <= margem_media < 100: return 10
    return 0

def main() -> None:
    # --- Paths ---
    data_dir = Path(__file__).resolve().parent.parent / "data"
    indicadores_path = data_dir / "indicadores.csv"
    dy_path = data_dir / "dividend_yield.csv"
    scores_path = data_dir / "scores.csv"
    rj_path = data_dir / "rj.csv"
    acoes_path = data_dir / "acoes_e_fundos.csv"
    output_path = data_dir / "avaliacao_setor.csv"

    print("Iniciando avaliação de setores...")
    try:
        indicadores_df = pd.read_csv(indicadores_path)
        dy_df = pd.read_csv(dy_path)
        scores_df = pd.read_csv(scores_path)
        rj_df = pd.read_csv(rj_path)
        acoes_df = pd.read_csv(acoes_path)
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}. Abortando.")
        return

    # --- Fallback de Mapeamento de Setor ---
    if 'subsetor_b3' not in acoes_df.columns:
        print("AVISO: 'subsetor_b3' não encontrado. Executando mapeamento de setores como fallback.")
        acoes_df = mapear_setores_b3(acoes_df)

    # --- Preparação e Merge ---
    # Normaliza tickers
    for df in [indicadores_df, dy_df, scores_df, acoes_df]:
        if 'ticker' in df.columns:
            df["ticker_base"] = df["ticker"].astype(str).str.upper().str.strip()
        elif 'ticker_base' in df.columns:
             df["ticker_base"] = df["ticker_base"].astype(str).str.upper().str.strip()


    # Merge principal
    indicadores_df = indicadores_df.drop(columns=['setor_b3', 'subsetor_b3'], errors='ignore')
    merged_df = pd.merge(
        indicadores_df,
        acoes_df[['ticker_base', 'setor_b3', 'subsetor_b3']].drop_duplicates(),
        on="ticker_base",
        how="left"
    )
    merged_df = pd.merge(
        merged_df,
        dy_df[['ticker_base', 'DY5anos']],
        on="ticker_base",
        how="left"
    )
    merged_df = pd.merge(
        merged_df,
        scores_df[['ticker_base', 'score_total']],
        on="ticker_base",
        how="left"
    )
    
    # Limpa e converte tipos
    merged_df = merged_df.dropna(subset=[col for col in ['setor_b3', 'subsetor_b3'] if col in merged_df.columns])
    numeric_cols = ['roe', 'beta', 'payout_ratio', 'margem_seguranca_percent', 'DY5anos', 'score_total']
    for col in numeric_cols:
        merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')
    merged_df = merged_df.fillna(0)


    # --- Agregação por Subsetor ---
    subsetor_stats = merged_df.groupby('subsetor_b3').agg(
        roe_medio=('roe', 'mean'),
        beta_medio=('beta', 'mean'),
        payout_medio=('payout_ratio', 'mean'),
        dy_5a_medio=('DY5anos', 'mean'),
        margem_graham_media=('margem_seguranca_percent', 'mean'),
        score_original=('score_total', 'mean')
    ).reset_index()

    # Contagem de empresas com score > 150
    boas = merged_df[merged_df['score_total'] > 150].groupby('subsetor_b3').size().reset_index(name='empresas_boas_contagem')
    subsetor_stats = pd.merge(subsetor_stats, boas, on='subsetor_b3', how='left')

    # Contagem de empresas com score < 50
    ruins = merged_df[merged_df['score_total'] < 50].groupby('subsetor_b3').size().reset_index(name='empresas_ruins_contagem')
    subsetor_stats = pd.merge(subsetor_stats, ruins, on='subsetor_b3', how='left')

    # Contagem de empresas em RJ
    rj_df['setor'] = rj_df['setor'].str.strip()
    rj_counts = rj_df[rj_df['data_saida_rj'].isnull()].groupby('setor').size().reset_index(name='ocorrencias_rj')
    subsetor_stats = pd.merge(subsetor_stats, rj_counts, left_on='subsetor_b3', right_on='setor', how='left').drop(columns='setor')
    
    subsetor_stats = subsetor_stats.fillna(0)

    # --- Cálculo das Pontuações por Critério ---
    subsetor_stats['score_dy'] = subsetor_stats['dy_5a_medio'].apply(calcular_score_dy)
    subsetor_stats['score_roe'] = subsetor_stats['roe_medio'].apply(calcular_score_roe)
    subsetor_stats['score_beta'] = subsetor_stats['beta_medio'].apply(calcular_score_beta)
    subsetor_stats['score_payout'] = subsetor_stats['payout_medio'].apply(calcular_score_payout)
    subsetor_stats['score_empresas_boas'] = subsetor_stats['empresas_boas_contagem'].apply(calcular_score_empresas_boas)
    subsetor_stats['penalidade_empresas_ruins'] = subsetor_stats['empresas_ruins_contagem'].apply(calcular_penalidade_empresas_ruins)
    subsetor_stats['score_graham'] = subsetor_stats['margem_graham_media'].apply(calcular_score_graham)

    # Cálculo da Penalidade de RJ (normalizada)
    max_ocorrencias = subsetor_stats['ocorrencias_rj'].max()
    if max_ocorrencias > 0:
        subsetor_stats['penalidade_rj'] = -(subsetor_stats['ocorrencias_rj'] / max_ocorrencias * 40)
    else:
        subsetor_stats['penalidade_rj'] = 0

    # --- Pontuação Final ---
    positive_score_cols = [
        'score_original', 'score_dy', 'score_roe', 'score_beta', 'score_payout', 
        'score_empresas_boas', 'score_graham'
    ]
    subsetor_stats['pontuacao_positiva'] = subsetor_stats[positive_score_cols].sum(axis=1)
    subsetor_stats['pontuacao_positiva'] = subsetor_stats['pontuacao_positiva'].apply(lambda x: min(x, 500))

    penalty_cols = ['penalidade_empresas_ruins', 'penalidade_rj']
    subsetor_stats['pontuacao_final'] = subsetor_stats['pontuacao_positiva'] + subsetor_stats[penalty_cols].sum(axis=1)

    # --- Agregação para o Setor Principal ---
    # Garante que cada subsetor está mapeado para um setor_b3
    setor_mapping = acoes_df[['setor_b3', 'subsetor_b3']].drop_duplicates()
    resultado_final = pd.merge(subsetor_stats, setor_mapping, on='subsetor_b3', how='left')
    
    # Calcula a pontuação média do setor
    pontuacao_setor_media = resultado_final.groupby('setor_b3')['pontuacao_final'].mean().reset_index()
    pontuacao_setor_media = pontuacao_setor_media.rename(columns={'pontuacao_final': 'pontuacao_setor'})
    
    resultado_final = pd.merge(resultado_final, pontuacao_setor_media, on='setor_b3', how='left')

    # --- Finalização e Salvamento ---
    # Ordena e seleciona colunas
    colunas_finais = [
        'setor_b3', 'pontuacao_setor', 'subsetor_b3', 'pontuacao_final',
        'score_dy', 'score_roe', 'score_beta', 'score_payout',
        'score_empresas_boas', 'penalidade_empresas_ruins', 'score_graham', 'penalidade_rj',
        'dy_5a_medio', 'roe_medio', 'beta_medio', 'payout_medio', 'margem_graham_media', 'score_original',
        'empresas_boas_contagem', 'empresas_ruins_contagem', 'ocorrencias_rj'
    ]
    resultado_final = resultado_final[colunas_finais]
    resultado_final = resultado_final.sort_values(by=['pontuacao_setor', 'pontuacao_final'], ascending=[False, False])
    
    # Arredonda valores para melhor visualização
    for col in resultado_final.columns:
        if pd.api.types.is_numeric_dtype(resultado_final[col]):
            resultado_final[col] = resultado_final[col].round(2)

    resultado_final.to_csv(output_path, index=False, float_format="%.2f")
    print(f"OK. Novo arquivo de avaliação de setores salvo em: {output_path}")


if __name__ == "__main__":
    main()
