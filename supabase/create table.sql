
CREATE TABLE todos_dividendos (
    "Data" DATE,
    "Valor" REAL,
    "Ticker" TEXT
);

CREATE TABLE tickers_nao_mapeados (
    "Ticker" TEXT
);

CREATE TABLE scores (
    "ticker_base" TEXT,
    "score_dy" INTEGER,
    "score_payout" INTEGER,
    "score_roe" INTEGER,
    "score_pl_pvp" INTEGER,
    "score_divida" INTEGER,
    "score_crescimento_sentimento" REAL,
    "score_ciclo_mercado" INTEGER,
    "score_graham" INTEGER,
    "score_beta" INTEGER,
    "score_market_cap" INTEGER,
    "score_liquidez" INTEGER,
    "score_fcf_yield" INTEGER,
    "score_total" REAL
);

CREATE TABLE precos_acoes_completo (
    "ticker" TEXT,
    "ano" INTEGER,
    "fechamento" REAL
);

CREATE TABLE precos_acoes (
    "ticker" TEXT,
    "fechamento_atual" REAL,
    "fechamento_1M_atras" REAL,
    "fechamento_6M_atras" REAL
);

CREATE TABLE preco_teto (
    "ticker" TEXT,
    "preco_teto_5anos" REAL,
    "diferenca_percentual" REAL
);

CREATE TABLE indicadores (
    "ticker" TEXT,
    "empresa" TEXT,
    "subsetor_b3" TEXT,
    "tipo" TEXT,
    "market_cap" BIGINT,
    "logo" TEXT,
    "preco_atual" REAL,
    "p_l" REAL,
    "p_vp" REAL,
    "payout_ratio" REAL,
    "crescimento_preco_5a" REAL,
    "roe" REAL,
    "divida_total" REAL,
    "ebitda" REAL,
    "divida_ebitda" REAL,
    "beta" REAL,
    "current_ratio" REAL,
    "liquidez_media_diaria" REAL,
    "fcf_yield" REAL,
    "perfil_acao" TEXT,
    "lpa" REAL,
    "vpa" REAL,
    "margem_seguranca_percent" REAL,
    "sentimento_gauge" REAL,
    "strong_buy" INTEGER,
    "buy" INTEGER,
    "hold" INTEGER,
    "sell" INTEGER,
    "strong_sell" INTEGER,
    "rsi_14_1y" REAL,
    "macd_diff_1y" REAL,
    "volume_1y" REAL,
    "ciclo_de_mercado" TEXT,
    "status_ciclo" TEXT,
    "frase_ciclo" TEXT
);

CREATE TABLE dividendos_ano_resumo (
    "ticker" TEXT,
    "valor_5anos" REAL,
    "valor_12m" REAL
);

CREATE TABLE dividendos_ano (
    "ano" INTEGER,
    "ticker" TEXT,
    "dividendo" REAL
);

CREATE TABLE dividend_yield (
    "ticker" TEXT,
    "DY5anos" REAL,
    "DY12M" REAL
);

CREATE TABLE avaliacao_setor (
    "setor_b3" TEXT,
    "pontuacao_setor" REAL,
    "subsetor_b3" TEXT,
    "pontuacao_final" REAL,
    "score_dy" INTEGER,
    "score_roe" INTEGER,
    "score_beta" INTEGER,
    "score_payout" INTEGER,
    "score_empresas_boas" INTEGER,
    "penalidade_empresas_ruins" INTEGER,
    "score_graham" INTEGER,
    "penalidade_rj" REAL,
    "dy_5a_medio" REAL,
    "roe_medio" REAL,
    "beta_medio" REAL,
    "payout_medio" REAL,
    "margem_graham_media" REAL,
    "score_original" REAL,
    "empresas_boas_contagem" INTEGER,
    "empresas_ruins_contagem" REAL,
    "ocorrencias_rj" REAL
);

CREATE TABLE acoes_e_fundos (
    "ticker" TEXT,
    "empresa" TEXT,
    "volume" INTEGER,
    "logo" TEXT,
    "setor_brapi" TEXT,
    "tipo" TEXT,
    "setor_b3" TEXT,
    "subsetor_b3" TEXT
);

CREATE TABLE ciclo_mercado (
    "ticker" TEXT,
    "Status Ciclo" TEXT
);

CREATE TABLE rj (
    "nome" TEXT,
    "ticker" TEXT,
    "setor" TEXT,
    "data_entrada_rj" DATE,
    "data_saida_rj" DATE,
    "data_falencia" DATE,
    "duracao_rj" TEXT
);

CREATE TABLE indices (
    "year" INTEGER,
    "index" TEXT,
    "close" REAL,
    "rsi" REAL,
    "macd" REAL,
    "volume" INTEGER
);
