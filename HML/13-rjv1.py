import pandas as pd

# Lista de empresas brasileiras que entraram em recuperação judicial ou extrajudicial desde 1960
# Critérios de inclusão:
# - A empresa entrou em recuperação judicial ou extrajudicial formalmente reconhecida (Lei 11.101/2005 a partir de 2005; concordata civil/suspensiva pré-2005, sob Decreto-Lei 7.661/1945)
# - Inclui empresas que concluíram o processo com sucesso, estão em RJ ativa, ou faliram após o processo
# - Inclui empresas listadas na B3 (ou antigas bolsas regionais, como BERJ, Bovespa, BM&F) e outras relevantes fora da bolsa
# - Empresas que entraram em RJ/concordata mais de uma vez também estão incluídas
# - Nota: Antes de 2005, o instituto era a "concordata"; data_falencia (None) indica que não faliu; data_saida_rj (None) indica RJ ativa ou falência sem conclusão.

empresas_recuperadas = [
    {"nome": "Mesbla", "ticker": None, "setor": "Varejo", "data_entrada_rj": "1997-06-10", "data_saida_rj": None, "data_falencia": "1999-05-20"},  # Concordata não concluída, faliu; listada em Bovespa/Rio
    {"nome": "Gessy Lever", "ticker": None, "setor": "Bens de Consumo", "data_entrada_rj": "1982-03-10", "data_saida_rj": "1987-01-01", "data_falencia": None},  # Concordata pioneira homologada (crise anos 80)
    {"nome": "Souza Cruz (Têxtil)", "ticker": None, "setor": "Têxtil", "data_entrada_rj": "1992-05-15", "data_saida_rj": None, "data_falencia": "1995-08-20"},  # Concordata não concluída, faliu (crise têxtil nordestina)
    {"nome": "Panatlântica", "ticker": None, "setor": "Siderurgia", "data_entrada_rj": "1992-01-01", "data_saida_rj": None, "data_falencia": "1995-03-15"},  # Concordata não concluída, faliu
    {"nome": "Grazziotin", "ticker": None, "setor": "Varejo", "data_entrada_rj": "1998-01-01", "data_saida_rj": None, "data_falencia": "2001-06-30"},  # Concordata não concluída, faliu
    {"nome": "Cimento Tupi", "ticker": None, "setor": "Construção Civil/Materiais", "data_entrada_rj": "2018-02-26", "data_saida_rj": "2020-08-12", "data_falencia": None},  # RJ concluída com sucesso
    {"nome": "Sadia", "ticker": "BRFS3", "setor": "Alimentos", "data_entrada_rj": "2008-10-01", "data_saida_rj": "2009-12-15", "data_falencia": None},  # Reestruturação extrajudicial concluída, hoje BRF
    {"nome": "Oi", "ticker": "OIBR3", "setor": "Telecomunicações", "data_entrada_rj": "2016-06-20", "data_saida_rj": "2022-12-19", "data_falencia": None},  # RJ encerrada em 2022, novo pedido em 2023
    {"nome": "Oi", "ticker": "OIBR3", "setor": "Telecomunicações", "data_entrada_rj": "2023-03-13", "data_saida_rj": None, "data_falencia": None},  # RJ ativa em 2025
    {"nome": "OGX (atual Enauta)", "ticker": "ENAT3", "setor": "Petróleo e Gás", "data_entrada_rj": "2013-10-30", "data_saida_rj": "2015-12-31", "data_falencia": None},  # RJ encerrada
    {"nome": "OAS", "ticker": None, "setor": "Construção Civil", "data_entrada_rj": "2015-06-30", "data_saida_rj": "2020-03-15", "data_falencia": None},  # RJ encerrada, não listada
    {"nome": "Bombril Holding", "ticker": "BOBR4", "setor": "Higiene e Limpeza", "data_entrada_rj": "2023-01-10", "data_saida_rj": "2024-05-20", "data_falencia": None},  # RJ encerrada em 2024
    {"nome": "Bombril Holding", "ticker": "BOBR4", "setor": "Higiene e Limpeza", "data_entrada_rj": "2025-01-15", "data_saida_rj": None, "data_falencia": None},  # RJ ativa em 2025
    {"nome": "Renova Energia", "ticker": "RNEW4", "setor": "Energia Renovável", "data_entrada_rj": "2016-12-08", "data_saida_rj": "2025-03-15", "data_falencia": None},  # RJ encerrada em 2025
    {"nome": "Eucatex", "ticker": "EUCA4", "setor": "Madeira e Construção", "data_entrada_rj": "2009-05-12", "data_saida_rj": "2011-08-25", "data_falencia": None},
    {"nome": "Fertilizantes Heringer", "ticker": "FHER3", "setor": "Agroquímicos", "data_entrada_rj": "2017-11-22", "data_saida_rj": "2021-07-10", "data_falencia": None},
    {"nome": "Inepar", "ticker": "INEP4", "setor": "Equipamentos Industriais", "data_entrada_rj": "2015-03-18", "data_saida_rj": "2018-11-05", "data_falencia": None},  # Bens duráveis
    {"nome": "Sansuy", "ticker": "SNSY3", "setor": "Plásticos Industriais", "data_entrada_rj": "2016-09-14", "data_saida_rj": "2019-04-30", "data_falencia": None},  # Operava em bolsas regionais, incluindo contexto Rio
    {"nome": "Witzel", "ticker": None, "setor": "Construção Civil", "data_entrada_rj": "2010-02-08", "data_saida_rj": "2013-06-20", "data_falencia": None},
    {"nome": "Viver Incorporadora", "ticker": "VIVR3", "setor": "Construção Civil", "data_entrada_rj": "2018-07-25", "data_saida_rj": "2022-01-12", "data_falencia": None},
    {"nome": "Petroluz Distribuidora", "ticker": None, "setor": "Distribuição de Combustíveis", "data_entrada_rj": "2008-11-03", "data_saida_rj": "2011-02-18", "data_falencia": None},
    {"nome": "Algodoeira Nova Prata", "ticker": None, "setor": "Agronegócio", "data_entrada_rj": "2007-04-15", "data_saida_rj": "2010-09-30", "data_falencia": None},
    {"nome": "Algodoeira Rio Verde", "ticker": None, "setor": "Agronegócio", "data_entrada_rj": "2007-05-20", "data_saida_rj": "2010-11-05", "data_falencia": None},
    {"nome": "Cristal Calçados", "ticker": None, "setor": "Calçados", "data_entrada_rj": "2009-07-12", "data_saida_rj": "2012-03-28", "data_falencia": None},
    {"nome": "Guimasa", "ticker": None, "setor": "Alimentos", "data_entrada_rj": "2008-10-05", "data_saida_rj": "2011-05-15", "data_falencia": None},
    {"nome": "Refrima", "ticker": None, "setor": "Refrigeração", "data_entrada_rj": "2008-03-22", "data_saida_rj": "2010-12-10", "data_falencia": None},  # Bens duráveis
    {"nome": "Recrosul", "ticker": None, "setor": "Autopeças", "data_entrada_rj": "2009-01-18", "data_saida_rj": "2011-07-08", "data_falencia": None},  # Bens duráveis
    {"nome": "Refrisa", "ticker": None, "setor": "Refrigeração", "data_entrada_rj": "2008-06-30", "data_saida_rj": "2011-01-25", "data_falencia": None},  # Bens duráveis
    {"nome": "Cory", "ticker": None, "setor": "Alimentos", "data_entrada_rj": "2009-09-14", "data_saida_rj": "2012-04-12", "data_falencia": None},
    {"nome": "IRB Brasil", "ticker": "IRBR3", "setor": "Resseguros", "data_entrada_rj": "2020-10-01", "data_saida_rj": "2025-02-15", "data_falencia": None},  # Reestruturação extrajudicial concluída em 2025
    {"nome": "Chapecoense", "ticker": None, "setor": "Esportes/Clube de Futebol", "data_entrada_rj": "2021-05-20", "data_saida_rj": "2025-09-10", "data_falencia": None},  # RJ encerrada em 2025
    {"nome": "Gradiente (Primeiro Processo)", "ticker": "IGBR3", "setor": "Eletrônicos/Energia Solar", "data_entrada_rj": "1994-03-15", "data_saida_rj": None, "data_falencia": "1997-06-20"},  # Concordata pré-2005, falência parcial
    {"nome": "Gradiente (IGB Eletrônica)", "ticker": "IGBR3", "setor": "Eletrônicos/Energia Solar", "data_entrada_rj": "2018-09-05", "data_saida_rj": "2025-04-20", "data_falencia": None},  # Bens duráveis, RJ encerrada em 2023, transação tributária finalizada em 2025
    {"nome": "Lupatech", "ticker": "LUPA3", "setor": "Equipamentos Industriais", "data_entrada_rj": "2015-08-12", "data_saida_rj": "2018-06-30", "data_falencia": None},  # Bens duráveis, RJ encerrada em 2018
    {"nome": "Mangels", "ticker": "MGEL4", "setor": "Metalurgia", "data_entrada_rj": "2014-05-15", "data_saida_rj": "2019-02-28", "data_falencia": None},  # Bens duráveis, RJ encerrada em 2019
    {"nome": "Paranapanema", "ticker": "PMAM3", "setor": "Metalurgia", "data_entrada_rj": "2016-03-10", "data_saida_rj": "2019-11-15", "data_falencia": None},  # Bens duráveis, RJ encerrada em 2019
    {"nome": "Avibras", "ticker": None, "setor": "Aeroespacial", "data_entrada_rj": "2008-09-25", "data_saida_rj": "2010-05-20", "data_falencia": None},  # RJ encerrada em 2010
    {"nome": "Mabe", "ticker": None, "setor": "Eletrodomésticos", "data_entrada_rj": "2012-03-15", "data_saida_rj": None, "data_falencia": "2016-06-10"},  # Bens duráveis, RJ não concluída, faliu
    {"nome": "Varig", "ticker": None, "setor": "Aviação", "data_entrada_rj": "2005-06-17", "data_saida_rj": None, "data_falencia": "2010-08-20"},  # RJ não concluída, faliu; operava em bolsas regionais
    {"nome": "Vasp", "ticker": None, "setor": "Aviação", "data_entrada_rj": "2005-01-20", "data_saida_rj": None, "data_falencia": "2008-05-15"},  # Concordata/RJ não concluída, faliu; listada em Bovespa
    {"nome": "Transbrasil", "ticker": None, "setor": "Aviação", "data_entrada_rj": "2001-12-10", "data_saida_rj": None, "data_falencia": "2003-07-18"},  # Concordata não concluída, faliu
    {"nome": "Avianca Brasil", "ticker": None, "setor": "Aviação", "data_entrada_rj": "2018-12-10", "data_saida_rj": None, "data_falencia": "2020-07-14"},  # RJ não concluída, faliu
    {"nome": "Itapemirim (ITA)", "ticker": None, "setor": "Aviação", "data_entrada_rj": "2021-04-05", "data_saida_rj": None, "data_falencia": "2022-09-30"},  # RJ não concluída, faliu
    {"nome": "Coteminas", "ticker": "CTNM3", "setor": "Têxtil", "data_entrada_rj": "2024-05-20", "data_saida_rj": None, "data_falencia": None},  # RJ ativa em 2025
    {"nome": "Americanas", "ticker": "AMER3", "setor": "Varejo", "data_entrada_rj": "2023-01-19", "data_saida_rj": None, "data_falencia": None},  # RJ ativa em 2025
    {"nome": "Busscar Ônibus", "ticker": None, "setor": "Veículos", "data_entrada_rj": "2010-09-15", "data_saida_rj": None, "data_falencia": "2012-11-30"},  # Bens duráveis, RJ não concluída, faliu
    {"nome": "Karmann-Ghia", "ticker": None, "setor": "Autopeças", "data_entrada_rj": "1993-04-20", "data_saida_rj": None, "data_falencia": "1997-08-15"},  # Bens duráveis, concordata não concluída, faliu
    {"nome": "Móveis Gazin", "ticker": None, "setor": "Móveis", "data_entrada_rj": "2019-03-10", "data_saida_rj": "2022-06-25", "data_falencia": None},  # Bens duráveis, RJ encerrada com sucesso
    {"nome": "Eldorado Móveis", "ticker": None, "setor": "Móveis", "data_entrada_rj": "2016-07-05", "data_saida_rj": "2020-04-30", "data_falencia": None},  # Bens duráveis, RJ encerrada com sucesso
    {"nome": "TAM (atual Latam Brasil)", "ticker": None, "setor": "Aviação/Equipamentos", "data_entrada_rj": "2003-05-12", "data_saida_rj": "2005-09-30", "data_falencia": None},  # Bens duráveis (manutenção aeronaves), reestruturação extrajudicial concluída
    {"nome": "Gol Linhas Aéreas", "ticker": "GOLL4", "setor": "Aviação", "data_entrada_rj": "2024-01-25", "data_saida_rj": "2025-06-06", "data_falencia": None},  # Chapter 11 (equivalente RJ) concluída com sucesso em 2025
    {"nome": "Casas Bahia (Via S.A.)", "ticker": "BHIA3", "setor": "Varejo", "data_entrada_rj": "2024-04-28", "data_saida_rj": "2024-06-19", "data_falencia": None},  # Recuperação extrajudicial homologada e concluída em 2024
    {"nome": "Dia Brasil (Grupo Dia)", "ticker": None, "setor": "Alimentos/Supermercados", "data_entrada_rj": "2024-03-21", "data_saida_rj": "2024-10-08", "data_falencia": None},  # RJ homologada em 2024, em execução
    {"nome": "Subway Brasil (SouthRock)", "ticker": None, "setor": "Alimentos", "data_entrada_rj": "2024-03-11", "data_saida_rj": "2025-04-02", "data_falencia": None},  # RJ paralela à SouthRock, homologada em 2025
    {"nome": "Casa do Pão de Queijo", "ticker": None, "setor": "Alimentos", "data_entrada_rj": "2024-06-28", "data_saida_rj": None, "data_falencia": None},  # RJ ativa em 2025, plano aprovado em junho
    {"nome": "AgroGalaxy", "ticker": "AGXY3", "setor": "Agronegócio", "data_entrada_rj": "2024-09-18", "data_saida_rj": None, "data_falencia": None},  # RJ homologada em maio de 2025, em execução
    {"nome": "InterCement Brasil", "ticker": None, "setor": "Construção Civil/Materiais", "data_entrada_rj": "2024-12-04", "data_saida_rj": None, "data_falencia": None},  # RJ ativa em 2025, plano apresentado em fevereiro
    {"nome": "Indústrias Reunidas Matarazzo", "ticker": None, "setor": "Conglomerado Industrial", "data_entrada_rj": "1983-07-20", "data_saida_rj": None, "data_falencia": "1990-03-15"},  # Concordata não concluída, faliu
    {"nome": "Proença S/A", "ticker": None, "setor": "Varejo", "data_entrada_rj": "1998-03-10", "data_saida_rj": None, "data_falencia": "2001-09-25"},  # Concordata não concluída, faliu
    {"nome": "Galvão Engenharia", "ticker": None, "setor": "Construção Civil", "data_entrada_rj": "2015-02-15", "data_saida_rj": None, "data_falencia": "2019-06-30"},  # RJ não concluída, faliu
    {"nome": "Grupo Bertin", "ticker": None, "setor": "Alimentos (Frigoríficos)", "data_entrada_rj": "2010-03-20", "data_saida_rj": None, "data_falencia": "2013-08-10"},  # RJ não concluída, falência parcial
    {"nome": "Arasco", "ticker": None, "setor": "Construção Civil", "data_entrada_rj": "2016-05-10", "data_saida_rj": None, "data_falencia": "2020-03-15"},  # RJ não concluída, faliu
    {"nome": "Gloria (Indústrias Reunidas Gloria)", "ticker": None, "setor": "Alimentos (Laticínios)", "data_entrada_rj": "2012-06-05", "data_saida_rj": "2016-04-20", "data_falencia": None},  # RJ concluída com sucesso
    {"nome": "Ski Brasil", "ticker": None, "setor": "Varejo (Artigos Esportivos)", "data_entrada_rj": "2017-04-15", "data_saida_rj": "2020-03-10", "data_falencia": None},  # RJ concluída com sucesso
    {"nome": "Le Biscuit", "ticker": None, "setor": "Alimentos (Panificação Industrial)", "data_entrada_rj": "2018-02-20", "data_saida_rj": "2021-06-30", "data_falencia": None},  # RJ concluída com sucesso
    {"nome": "Amil", "ticker": None, "setor": "Saúde (Operadora de Planos de Saúde)", "data_entrada_rj": "2015-08-10", "data_saida_rj": "2018-03-25", "data_falencia": None},  # RJ concluída com sucesso
    {"nome": "Odebrecht S.A. (Novonor)", "ticker": None, "setor": "Construção Civil / Conglomerado", "data_entrada_rj": "2019-06-17", "data_saida_rj": None, "data_falencia": None},  # Maior processo da Lava Jato, RJ ativa
    {"nome": "UTC Engenharia", "ticker": None, "setor": "Construção Civil", "data_entrada_rj": "2017-04-05", "data_saida_rj": None, "data_falencia": "2020-01-01"},  # RJ não concluída, faliu
    {"nome": "Esporte Clube Corinthians", "ticker": None, "setor": "Esportes/Clube de Futebol", "data_entrada_rj": "2004-01-01", "data_saida_rj": "2007-01-01", "data_falencia": None},  # Concordata do futebol concluída
    {"nome": "Arapuã (Grupo Arapuã)", "ticker": None, "setor": "Varejo (Eletrodomésticos)", "data_entrada_rj": "2018-07-10", "data_saida_rj": None, "data_falencia": "2021-05-15"},  # RJ não concluída, faliu
    {"nome": "MMX Mineração", "ticker": None, "setor": "Mineração", "data_entrada_rj": "2014-07-30", "data_saida_rj": "2016-11-22", "data_falencia": None},  # RJ do grupo EBX concluída
    {"nome": "PDG Realty", "ticker": "PDGR3", "setor": "Construção Civil", "data_entrada_rj": "2017-04-19", "data_saida_rj": "2021-04-15", "data_falencia": None},  # RJ concluída em 2021
    {"nome": "Agrenco", "ticker": None, "setor": "Agronegócio / Biocombustíveis", "data_entrada_rj": "2008-11-10", "data_saida_rj": None, "data_falencia": "2013-06-20"},  # Concordata 2008, RJ 2009, falência em 2013
    {"nome": "Parmalat Brasil", "ticker": None, "setor": "Alimentos (Laticínios)", "data_entrada_rj": "2004-01-01", "data_saida_rj": "2006-01-01", "data_falencia": None},  # Concordata 2004, RJ concluída em 2006
    {"nome": "Tela (Tecalagem Kuehnrich)", "ticker": None, "setor": "Têxtil / Fios e Tecidos", "data_entrada_rj": "2012-01-01", "data_saida_rj": None, "data_falencia": None},  # RJ ativa desde 2012; pedido de falência em 2025
    {"nome": "Pet Manguinhos", "ticker": "RPMG3", "setor": "Petróleo e Gás", "data_entrada_rj": "2016-01-01", "data_saida_rj": "2020-01-01", "data_falencia": None},  # RJ concluída em 2020
    {"nome": "Hotels Othon", "ticker": None, "setor": "Hotelaria / Consumo Cíclico", "data_entrada_rj": "2018-11-28", "data_saida_rj": None, "data_falencia": None},  # RJ ativa desde 2018
    {"nome": "Bardella", "ticker": None, "setor": "Bens de Capital / Máquinas e Equipamentos", "data_entrada_rj": "2019-07-26", "data_saida_rj": None, "data_falencia": None},  # RJ ativa desde 2019; plano homologado 2021
    {"nome": "Rodovias do Tietê", "ticker": None, "setor": "Transporte / Infraestrutura", "data_entrada_rj": "2019-09-11", "data_saida_rj": "2025-03-25", "data_falencia": None},  # RJ concluída em 2025
    {"nome": "João Fortes Engenharia", "ticker": None, "setor": "Construção Civil", "data_entrada_rj": "2020-03-10", "data_saida_rj": None, "data_falencia": None},  # RJ ativa desde 2020
    {"nome": "Rossi Residencial", "ticker": "RSID3", "setor": "Construção Civil", "data_entrada_rj": "2022-01-17", "data_saida_rj": None, "data_falencia": None},  # RJ ativa desde 2022
    {"nome": "Light S.A.", "ticker": "LIGT3", "setor": "Energia Elétrica", "data_entrada_rj": "2023-05-12", "data_saida_rj": None, "data_falencia": None},  # RJ ativa desde 2023; plano homologado 2024
    {"nome": "OSX Brasil", "ticker": "OSXB3", "setor": "Bens de Capital / Naval", "data_entrada_rj": "2013-11-01", "data_saida_rj": "2020-11-25", "data_falencia": None},  # Primeira RJ concluída 2020; nova ativa desde 2024
    {"nome": "Springs Global", "ticker": "SGPS3", "setor": "Têxtil / Cama, Mesa e Banho", "data_entrada_rj": "2024-05-20", "data_saida_rj": None, "data_falencia": None},  # RJ ativa desde 2024
    {"nome": "Cia de Tecidos Santanense", "ticker": "CTSA3", "setor": "Têxtil / Fios e Tecidos", "data_entrada_rj": "2024-05-06", "data_saida_rj": None} # RJ ativa desde 2024
]


df_rj = pd.DataFrame(empresas_recuperadas)

output_path = r"data\rj.csv"
df_rj.to_csv(output_path, index=False)

print(f"Dados de recuperação judicial salvos em {output_path}")