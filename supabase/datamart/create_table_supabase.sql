-- Schema land_dw
CREATE SCHEMA IF NOT EXISTS land_dw;

-- Tabela Central de Ativos
CREATE TABLE land_dw.acoes_e_fundos (
    ticker TEXT PRIMARY KEY,
    empresa TEXT,
    volume INTEGER,
    logo TEXT,
    setor_brapi TEXT,
    tipo TEXT,
    setor_b3 TEXT,
    subsetor_b3 TEXT
);

-- Tabelas com relacionamento
CREATE TABLE land_dw.todos_dividendos (
    id SERIAL PRIMARY KEY,
    data DATE,
    valor REAL,
    ticker TEXT REFERENCES land_dw.acoes_e_fundos(ticker)
);

CREATE TABLE land_dw.tickers_nao_mapeados (
    id SERIAL PRIMARY KEY,
    ticker TEXT
);

CREATE TABLE land_dw.scores (
    ticker_base TEXT PRIMARY KEY REFERENCES land_dw.acoes_e_fundos(ticker),
    score_dy INTEGER,
    score_payout INTEGER,
    score_roe INTEGER,
    score_pl_pvp INTEGER,
    score_divida INTEGER,
    score_crescimento_sentimento REAL,
    score_ciclo_mercado INTEGER,
    score_graham INTEGER,
    score_beta INTEGER,
    score_market_cap INTEGER,
    score_liquidez INTEGER,
    score_fcf_yield INTEGER,
    score_total REAL
);

CREATE TABLE land_dw.precos_acoes_completo (
    id SERIAL PRIMARY KEY,
    ticker TEXT REFERENCES land_dw.acoes_e_fundos(ticker),
    ano INTEGER,
    fechamento REAL
);

CREATE TABLE land_dw.precos_acoes (
    ticker TEXT PRIMARY KEY REFERENCES land_dw.acoes_e_fundos(ticker),
    fechamento_atual REAL,
    fechamento_1m_atras REAL,
    fechamento_6m_atras REAL
);

CREATE TABLE land_dw.preco_teto (
    ticker TEXT PRIMARY KEY REFERENCES land_dw.acoes_e_fundos(ticker),
    preco_teto_5anos REAL,
    diferenca_percentual REAL
);

CREATE TABLE land_dw.indicadores (
    ticker TEXT PRIMARY KEY REFERENCES land_dw.acoes_e_fundos(ticker),
    empresa TEXT,
    subsetor_b3 TEXT,
    tipo TEXT,
    market_cap BIGINT,
    logo TEXT,
    preco_atual REAL,
    p_l REAL,
    p_vp REAL,
    payout_ratio REAL,
    crescimento_preco_5a REAL,
    roe REAL,
    divida_total REAL,
    ebitda REAL,
    divida_ebitda REAL,
    beta REAL,
    current_ratio REAL,
    liquidez_media_diaria REAL,
    fcf_yield REAL,
    perfil_acao TEXT,
    lpa REAL,
    vpa REAL,
    margem_seguranca_percent REAL,
    sentimento_gauge REAL,
    strong_buy INTEGER,
    buy INTEGER,
    hold INTEGER,
    sell INTEGER,
    strong_sell INTEGER,
    rsi_14_1y REAL,
    macd_diff_1y REAL,
    volume_1y REAL,
    ciclo_de_mercado TEXT,
    status_ciclo TEXT,
    frase_ciclo TEXT
);

CREATE TABLE land_dw.dividendos_ano_resumo (
    ticker TEXT PRIMARY KEY REFERENCES land_dw.acoes_e_fundos(ticker),
    valor_5anos REAL,
    valor_12m REAL
);

CREATE TABLE land_dw.dividendos_ano (
    id SERIAL PRIMARY KEY,
    ano INTEGER,
    ticker TEXT REFERENCES land_dw.acoes_e_fundos(ticker),
    dividendo REAL
);

CREATE TABLE land_dw.dividend_yield (
    ticker TEXT PRIMARY KEY REFERENCES land_dw.acoes_e_fundos(ticker),
    dy5anos REAL,
    dy12m REAL
);

CREATE TABLE land_dw.avaliacao_setor (
    id SERIAL PRIMARY KEY,
    setor_b3 TEXT,
    pontuacao_setor REAL,
    subsetor_b3 TEXT,
    pontuacao_final REAL,
    score_dy INTEGER,
    score_roe INTEGER,
    score_beta INTEGER,
    score_payout INTEGER,
    score_empresas_boas INTEGER,
    penalidade_empresas_ruins INTEGER,
    score_graham INTEGER,
    penalidade_rj REAL,
    dy_5a_medio REAL,
    roe_medio REAL,
    beta_medio REAL,
    payout_medio REAL,
    margem_graham_media REAL,
    score_original REAL,
    empresas_boas_contagem INTEGER,
    empresas_ruins_contagem REAL,
    ocorrencias_rj REAL
);

CREATE TABLE land_dw.ciclo_mercado (
    ticker TEXT PRIMARY KEY REFERENCES land_dw.acoes_e_fundos(ticker),
    status_ciclo TEXT
);

CREATE TABLE land_dw.rj (
    id SERIAL PRIMARY KEY,
    nome TEXT,
    ticker TEXT,
    setor TEXT,
    data_entrada_rj DATE,
    data_saida_rj DATE,
    data_falencia DATE,
    duracao_rj TEXT
);

CREATE TABLE land_dw.indices (
    id SERIAL PRIMARY KEY,
    year INTEGER,
    index TEXT,
    close REAL,
    rsi REAL,
    macd REAL,
    volume INTEGER
);
