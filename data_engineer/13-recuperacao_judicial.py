import pandas as pd
import os

# Lista de empresas brasileiras que entraram em recuperação judicial ou extrajudicial desde 1960
# O campo "setor" foi atualizado para corresponder à classificação oficial (subsetor) definida.
empresas_recuperadas = [
    {"nome": "Mesbla", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "1997-06-10", "data_saida_rj": None, "data_falencia": "1999-05-20"},
    {"nome": "Gessy Lever", "ticker": None, "setor": "Bens de Consumo", "data_entrada_rj": "1982-03-10", "data_saida_rj": "1987-01-01", "data_falencia": None},
    {"nome": "Souza Cruz (Têxtil)", "ticker": None, "setor": "Têxtil", "data_entrada_rj": "1992-05-15", "data_saida_rj": None, "data_falencia": "1995-08-20"},
    {"nome": "Panatlântica", "ticker": None, "setor": "Mineração e Siderurgia", "data_entrada_rj": "1992-01-01", "data_saida_rj": None, "data_falencia": "1995-03-15"},
    {"nome": "Grazziotin", "ticker": "CGRA4", "setor": "Comércio Varejista", "data_entrada_rj": "1998-01-01", "data_saida_rj": None, "data_falencia": "2001-06-30"},
    {"nome": "Cimento Tupi", "ticker": None, "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2018-02-26", "data_saida_rj": "2020-08-12", "data_falencia": None},
    {"nome": "Sadia", "ticker": "BRFS3", "setor": "Alimentos e Bebidas", "data_entrada_rj": "2008-10-01", "data_saida_rj": "2009-12-15", "data_falencia": None},
    {"nome": "Oi", "ticker": "OIBR3", "setor": "Telecomunicações", "data_entrada_rj": "2016-06-20", "data_saida_rj": "2022-12-19", "data_falencia": None},
    {"nome": "Oi", "ticker": "OIBR3", "setor": "Telecomunicações", "data_entrada_rj": "2023-03-13", "data_saida_rj": None, "data_falencia": None},
    {"nome": "OGX (atual Dommo)", "ticker": "DMMO3", "setor": "Petróleo, Gás e Biocombustíveis", "data_entrada_rj": "2013-10-30", "data_saida_rj": "2015-12-31", "data_falencia": None},
    {"nome": "OAS", "ticker": None, "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2015-06-30", "data_saida_rj": "2020-03-15", "data_falencia": None},
    {"nome": "Bombril Holding", "ticker": "BOBR4", "setor": "Bens de Consumo", "data_entrada_rj": "2023-01-10", "data_saida_rj": "2024-05-20", "data_falencia": None},
    {"nome": "Bombril Holding", "ticker": "BOBR4", "setor": "Bens de Consumo", "data_entrada_rj": "2025-01-15", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Renova Energia", "ticker": "RNEW4", "setor": "Energia Elétrica", "data_entrada_rj": "2016-12-08", "data_saida_rj": "2025-03-15", "data_falencia": None},
    {"nome": "Eucatex", "ticker": "EUCA4", "setor": "Papel e Celulose", "data_entrada_rj": "2009-05-12", "data_saida_rj": "2011-08-25", "data_falencia": None},
    {"nome": "Fertilizantes Heringer", "ticker": "FHER3", "setor": "Química e Petroquímica", "data_entrada_rj": "2017-11-22", "data_saida_rj": "2021-07-10", "data_falencia": None},
    {"nome": "Inepar", "ticker": "INEP4", "setor": "Serviços Industriais", "data_entrada_rj": "2015-03-18", "data_saida_rj": "2018-11-05", "data_falencia": None},
    {"nome": "Sansuy", "ticker": "SNSY3", "setor": "Química e Petroquímica", "data_entrada_rj": "2016-09-14", "data_saida_rj": "2019-04-30", "data_falencia": None},
    {"nome": "Witzel", "ticker": None, "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2010-02-08", "data_saida_rj": "2013-06-20", "data_falencia": None},
    {"nome": "Viver Incorporadora", "ticker": "VIVR3", "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2018-07-25", "data_saida_rj": "2022-01-12", "data_falencia": None},
    {"nome": "Petroluz Distribuidora", "ticker": None, "setor": "Comércio e Distribuição", "data_entrada_rj": "2008-11-03", "data_saida_rj": "2011-02-18", "data_falencia": None},
    {"nome": "Algodoeira Nova Prata", "ticker": None, "setor": "Alimentos e Bebidas", "data_entrada_rj": "2007-04-15", "data_saida_rj": "2010-09-30", "data_falencia": None},
    {"nome": "Algodoeira Rio Verde", "ticker": None, "setor": "Alimentos e Bebidas", "data_entrada_rj": "2007-05-20", "data_saida_rj": "2010-11-05", "data_falencia": None},
    {"nome": "Cristal Calçados", "ticker": None, "setor": "Bens de Consumo", "data_entrada_rj": "2009-07-12", "data_saida_rj": "2012-03-28", "data_falencia": None},
    {"nome": "Guimasa", "ticker": None, "setor": "Alimentos e Bebidas", "data_entrada_rj": "2008-10-05", "data_saida_rj": "2011-05-15", "data_falencia": None},
    {"nome": "Refrima", "ticker": None, "setor": "Máquinas e Equipamentos", "data_entrada_rj": "2008-03-22", "data_saida_rj": "2010-12-10", "data_falencia": None},
    {"nome": "Recrusul", "ticker": "RCSL4", "setor": "Máquinas e Equipamentos", "data_entrada_rj": "2009-01-18", "data_saida_rj": "2011-07-08", "data_falencia": None},
    {"nome": "Refrisa", "ticker": None, "setor": "Máquinas e Equipamentos", "data_entrada_rj": "2008-06-30", "data_saida_rj": "2011-01-25", "data_falencia": None},
    {"nome": "Cory", "ticker": None, "setor": "Alimentos e Bebidas", "data_entrada_rj": "2009-09-14", "data_saida_rj": "2012-04-12", "data_falencia": None},
    {"nome": "IRB Brasil", "ticker": "IRBR3", "setor": "Serviços Financeiros Diversos", "data_entrada_rj": "2020-10-01", "data_saida_rj": "2025-02-15", "data_falencia": None},
    {"nome": "Chapecoense", "ticker": None, "setor": "Serviços Diversos", "data_entrada_rj": "2021-05-20", "data_saida_rj": "2025-09-10", "data_falencia": None},
    {"nome": "Gradiente (Primeiro Processo)", "ticker": "IGBR3", "setor": "Bens de Consumo", "data_entrada_rj": "1994-03-15", "data_saida_rj": None, "data_falencia": "1997-06-20"},
    {"nome": "Gradiente (IGB Eletrônica)", "ticker": "IGBR3", "setor": "Bens de Consumo", "data_entrada_rj": "2018-09-05", "data_saida_rj": "2025-04-20", "data_falencia": None},
    {"nome": "Lupatech", "ticker": "LUPA3", "setor": "Máquinas e Equipamentos", "data_entrada_rj": "2015-08-12", "data_saida_rj": "2018-06-30", "data_falencia": None},
    {"nome": "Mangels", "ticker": "MGEL4", "setor": "Máquinas e Equipamentos", "data_entrada_rj": "2014-05-15", "data_saida_rj": "2019-02-28", "data_falencia": None},
    {"nome": "Paranapanema", "ticker": "PMAM3", "setor": "Mineração e Siderurgia", "data_entrada_rj": "2016-03-10", "data_saida_rj": "2019-11-15", "data_falencia": None},
    {"nome": "Avibras", "ticker": None, "setor": "Máquinas e Equipamentos", "data_entrada_rj": "2008-09-25", "data_saida_rj": "2010-05-20", "data_falencia": None},
    {"nome": "Mabe", "ticker": None, "setor": "Bens de Consumo", "data_entrada_rj": "2012-03-15", "data_saida_rj": None, "data_falencia": "2016-06-10"},
    {"nome": "Varig", "ticker": None, "setor": "Transporte e Logística", "data_entrada_rj": "2005-06-17", "data_saida_rj": None, "data_falencia": "2010-08-20"},
    {"nome": "Vasp", "ticker": None, "setor": "Transporte e Logística", "data_entrada_rj": "2005-01-20", "data_saida_rj": None, "data_falencia": "2008-05-15"},
    {"nome": "Transbrasil", "ticker": None, "setor": "Transporte e Logística", "data_entrada_rj": "2001-12-10", "data_saida_rj": None, "data_falencia": "2003-07-18"},
    {"nome": "Avianca Brasil", "ticker": None, "setor": "Transporte e Logística", "data_entrada_rj": "2018-12-10", "data_saida_rj": None, "data_falencia": "2020-07-14"},
    {"nome": "Itapemirim (ITA)", "ticker": None, "setor": "Transporte e Logística", "data_entrada_rj": "2021-04-05", "data_saida_rj": None, "data_falencia": "2022-09-30"},
    {"nome": "Coteminas", "ticker": "CTNM3", "setor": "Têxtil", "data_entrada_rj": "2024-05-20", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Americanas", "ticker": "AMER3", "setor": "Comércio Varejista", "data_entrada_rj": "2023-01-19", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Busscar Ônibus", "ticker": None, "setor": "Máquinas e Equipamentos", "data_entrada_rj": "2010-09-15", "data_saida_rj": None, "data_falencia": "2012-11-30"},
    {"nome": "Karmann-Ghia", "ticker": None, "setor": "Máquinas e Equipamentos", "data_entrada_rj": "1993-04-20", "data_saida_rj": None, "data_falencia": "1997-08-15"},
    {"nome": "Móveis Gazin", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "2019-03-10", "data_saida_rj": "2022-06-25", "data_falencia": None},
    {"nome": "Eldorado Móveis", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "2016-07-05", "data_saida_rj": "2020-04-30", "data_falencia": None},
    {"nome": "TAM (atual Latam Brasil)", "ticker": None, "setor": "Transporte e Logística", "data_entrada_rj": "2003-05-12", "data_saida_rj": "2005-09-30", "data_falencia": None},
    {"nome": "Gol Linhas Aéreas", "ticker": "GOLL4", "setor": "Transporte e Logística", "data_entrada_rj": "2024-01-25", "data_saida_rj": "2025-06-06", "data_falencia": None},
    {"nome": "Casas Bahia (Via S.A.)", "ticker": "BHIA3", "setor": "Comércio Varejista", "data_entrada_rj": "2024-04-28", "data_saida_rj": "2024-06-19", "data_falencia": None},
    {"nome": "Dia Brasil (Grupo Dia)", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "2024-03-21", "data_saida_rj": "2024-10-08", "data_falencia": None},
    {"nome": "Subway Brasil (SouthRock)", "ticker": None, "setor": "Alimentos e Bebidas", "data_entrada_rj": "2024-03-11", "data_saida_rj": "2025-04-02", "data_falencia": None},
    {"nome": "Casa do Pão de Queijo", "ticker": None, "setor": "Alimentos e Bebidas", "data_entrada_rj": "2024-06-28", "data_saida_rj": None, "data_falencia": None},
    {"nome": "AgroGalaxy", "ticker": "AGXY3", "setor": "Comércio e Distribuição", "data_entrada_rj": "2024-09-18", "data_saida_rj": None, "data_falencia": None},
    {"nome": "InterCement Brasil", "ticker": None, "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2024-12-04", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Indústrias Reunidas Matarazzo", "ticker": None, "setor": "Serviços Industriais", "data_entrada_rj": "1983-07-20", "data_saida_rj": None, "data_falencia": "1990-03-15"},
    {"nome": "Proença S/A", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "1998-03-10", "data_saida_rj": None, "data_falencia": "2001-09-25"},
    {"nome": "Galvão Engenharia", "ticker": None, "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2015-02-15", "data_saida_rj": None, "data_falencia": "2019-06-30"},
    {"nome": "Grupo Bertin", "ticker": None, "setor": "Alimentos e Bebidas", "data_entrada_rj": "2010-03-20", "data_saida_rj": None, "data_falencia": "2013-08-10"},
    {"nome": "Arasco", "ticker": None, "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2016-05-10", "data_saida_rj": None, "data_falencia": "2020-03-15"},
    {"nome": "Gloria (Indústrias Reunidas Gloria)", "ticker": None, "setor": "Alimentos e Bebidas", "data_entrada_rj": "2012-06-05", "data_saida_rj": "2016-04-20", "data_falencia": None},
    {"nome": "Ski Brasil", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "2017-04-15", "data_saida_rj": "2020-03-10", "data_falencia": None},
    {"nome": "Le Biscuit", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "2018-02-20", "data_saida_rj": "2021-06-30", "data_falencia": None},
    {"nome": "Amil", "ticker": None, "setor": "Saúde", "data_entrada_rj": "2015-08-10", "data_saida_rj": "2018-03-25", "data_falencia": None},
    {"nome": "Odebrecht S.A. (Novonor)", "ticker": None, "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2019-06-17", "data_saida_rj": None, "data_falencia": None},
    {"nome": "UTC Engenharia", "ticker": None, "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2017-04-05", "data_saida_rj": None, "data_falencia": "2020-01-01"},
    {"nome": "Esporte Clube Corinthians", "ticker": None, "setor": "Serviços Diversos", "data_entrada_rj": "2004-01-01", "data_saida_rj": "2007-01-01", "data_falencia": None},
    {"nome": "Arapuã (Grupo Arapuã)", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "2018-07-10", "data_saida_rj": None, "data_falencia": "2021-05-15"},
    {"nome": "MMX Mineração", "ticker": "MMXM3", "setor": "Mineração e Siderurgia", "data_entrada_rj": "2014-07-30", "data_saida_rj": "2016-11-22", "data_falencia": None},
    {"nome": "PDG Realty", "ticker": "PDGR3", "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2017-04-19", "data_saida_rj": "2021-04-15", "data_falencia": None},
    {"nome": "Agrenco", "ticker": "AGEN11", "setor": "Petróleo, Gás e Biocombustíveis", "data_entrada_rj": "2008-11-10", "data_saida_rj": None, "data_falencia": "2013-06-20"},
    {"nome": "Parmalat Brasil", "ticker": None, "setor": "Alimentos e Bebidas", "data_entrada_rj": "2004-01-01", "data_saida_rj": "2006-01-01", "data_falencia": None},
    {"nome": "Teka (Tecelagem Kuehnrich)", "ticker": "TEKA4", "setor": "Têxtil", "data_entrada_rj": "2012-01-01", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Refinaria de Manguinhos", "ticker": "RPMG3", "setor": "Petróleo, Gás e Biocombustíveis", "data_entrada_rj": "2016-01-01", "data_saida_rj": "2020-01-01", "data_falencia": None},
    {"nome": "Hotéis Othon", "ticker": "HOOT4", "setor": "Serviços Diversos", "data_entrada_rj": "2018-11-28", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Bardella", "ticker": "BDLL4", "setor": "Máquinas e Equipamentos", "data_entrada_rj": "2019-07-26", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Rodovias do Tietê", "ticker": "RDVT3", "setor": "Transporte e Logística", "data_entrada_rj": "2019-09-11", "data_saida_rj": "2025-03-25", "data_falencia": None},
    {"nome": "João Fortes Engenharia", "ticker": "JFEN3", "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2020-03-10", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Rossi Residencial", "ticker": "RSID3", "setor": "Construção Civil e Imobiliário", "data_entrada_rj": "2022-01-17", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Light S.A.", "ticker": "LIGT3", "setor": "Energia Elétrica", "data_entrada_rj": "2023-05-12", "data_saida_rj": None, "data_falencia": None},
    {"nome": "OSX Brasil", "ticker": "OSXB3", "setor": "Serviços Industriais", "data_entrada_rj": "2013-11-01", "data_saida_rj": "2020-11-25", "data_falencia": None},
    {"nome": "Springs Global", "ticker": "SGPS3", "setor": "Têxtil", "data_entrada_rj": "2024-05-20", "data_saida_rj": None, "data_falencia": None},
    {"nome": "Cia de Tecidos Santanense", "ticker": "CTSA3", "setor": "Têxtil", "data_entrada_rj": "2024-05-06", "data_saida_rj": None, "data_falencia": None},
    {"nome": "H-Buster", "ticker": None, "setor": "Hardware e Equipamentos", "data_entrada_rj": "2013-03-22", "data_saida_rj": None, "data_falencia": "2015-01-01"},
    {"nome": "Livraria Cultura", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "2018-10-25", "data_saida_rj": None, "data_falencia": "2023-02-09"},
    {"nome": "Livraria Saraiva", "ticker": None, "setor": "Comércio Varejista", "data_entrada_rj": "2018-11-13", "data_saida_rj": None, "data_falencia": "2023-01-01"},
    {"nome": "Unimed Nacional (Cooperativas)", "ticker": None, "setor": "Saúde", "data_entrada_rj": "2015-01-01", "data_saida_rj": None, "data_falencia": "2018-01-01"},
    {"nome": "Hapvida (Subsidiárias)", "ticker": "HAPV3", "setor": "Saúde", "data_entrada_rj": "2023-01-01", "data_saida_rj": None, "data_falencia": None}
]

df_rj = pd.DataFrame(empresas_recuperadas)

# --- INÍCIO DA SEÇÃO PARA CÁLCULO DA DURAÇÃO ---

# Converte as colunas de data para o formato datetime, tratando erros como 'NaT' (Not a Time)
df_rj['data_entrada_rj'] = pd.to_datetime(df_rj['data_entrada_rj'], errors='coerce')
df_rj['data_saida_rj'] = pd.to_datetime(df_rj['data_saida_rj'], errors='coerce')

def calcular_duracao(row):
    """Calcula a duração entre duas datas e formata em anos e meses."""
    if pd.notna(row['data_entrada_rj']) and pd.notna(row['data_saida_rj']):
        # Calcula a diferença total em meses
        meses_totais = (row['data_saida_rj'].year - row['data_entrada_rj'].year) * 12 + (row['data_saida_rj'].month - row['data_entrada_rj'].month)
        
        if meses_totais < 0:
            return 'Datas Inválidas'

        anos = meses_totais // 12
        meses = meses_totais % 12
        
        resultado = []
        if anos > 0:
            resultado.append(f"{anos} ano{'s' if anos > 1 else ''}")
        # Inclui meses se houver, ou se for a única unidade (anos == 0)
        if meses > 0 or anos == 0:
            # Correção para o plural de "mês"
            resultado.append(f"{meses} {'meses' if meses > 1 else 'mês'}")
        
        # Junta as partes com " e " ou retorna o valor único
        return " e ".join(resultado) if resultado else "Menos de 1 mês"
    else:
        # Se a data de saída não existir, o processo está em andamento
        return 'Em Andamento'

# Aplica a função para criar a nova coluna 'duracao_rj'
df_rj['duracao_rj'] = df_rj.apply(calcular_duracao, axis=1)

# --- FIM DA SEÇÃO DE CÁLCULO ---

# Assegura que o diretório 'data' exista
os.makedirs('data', exist_ok=True)

output_path = r"data\rj.csv"
df_rj.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Dados de recuperação judicial salvos em {output_path}")

# Imprime as 5 primeiras linhas com as colunas relevantes para verificação
print("\nVisualização do DataFrame com a nova coluna 'duracao_rj':")
print(df_rj[['nome', 'data_entrada_rj', 'data_saida_rj', 'duracao_rj']].head().to_string())