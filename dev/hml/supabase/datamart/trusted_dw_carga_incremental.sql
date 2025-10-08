BEGIN;

-- 1. Sincronização segura da tabela central 'acoes_e_fundos'

-- Passo 1.1: Criar uma TABELA TEMPORÁRIA com os tickers a remover.
-- Esta tabela existirá durante toda a transação.
CREATE TEMP TABLE tickers_a_remover ON COMMIT DROP AS
SELECT t.ticker
FROM trusted_dw.acoes_e_fundos t
LEFT JOIN land_dw.acoes_e_fundos l ON TRIM(UPPER(t.ticker)) = TRIM(UPPER(l.ticker))
WHERE l.ticker IS NULL;

-- Passo 1.2: Agora, usar a tabela temporária para remover os dados das tabelas filhas.
DELETE FROM trusted_dw.todos_dividendos WHERE ticker IN (SELECT ticker FROM tickers_a_remover);
DELETE FROM trusted_dw.precos_acoes_completo WHERE ticker IN (SELECT ticker FROM tickers_a_remover);
DELETE FROM trusted_dw.dividendos_ano WHERE ticker IN (SELECT ticker FROM tickers_a_remover);
DELETE FROM trusted_dw.scores WHERE ticker_base IN (SELECT ticker FROM tickers_a_remover);
DELETE FROM trusted_dw.precos_acoes WHERE ticker IN (SELECT ticker FROM tickers_a_remover);
DELETE FROM trusted_dw.preco_teto WHERE ticker IN (SELECT ticker FROM tickers_a_remover);
DELETE FROM trusted_dw.indicadores WHERE ticker IN (SELECT ticker FROM tickers_a_remover);
DELETE FROM trusted_dw.dividendos_ano_resumo WHERE ticker IN (SELECT ticker FROM tickers_a_remover);
DELETE FROM trusted_dw.dividend_yield WHERE ticker IN (SELECT ticker FROM tickers_a_remover);
DELETE FROM trusted_dw.ciclo_mercado WHERE ticker IN (SELECT ticker FROM tickers_a_remover);

-- Passo 1.3: Remover os tickers da tabela pai.
DELETE FROM trusted_dw.acoes_e_fundos WHERE ticker IN (SELECT ticker FROM tickers_a_remover);

-- Passo 1.4: Inserir novos tickers e ATUALIZAR os existentes (UPSERT)
INSERT INTO trusted_dw.acoes_e_fundos (ticker, empresa, volume, logo, setor_brapi, tipo, setor_b3, subsetor_b3, data_atualizacao)
SELECT
    TRIM(UPPER(ticker)),
    empresa,
    volume,
    logo,
    setor_brapi,
    tipo,
    setor_b3,
    subsetor_b3,
    CURRENT_TIMESTAMP
FROM land_dw.acoes_e_fundos
ON CONFLICT (ticker) DO UPDATE SET
    empresa = EXCLUDED.empresa,
    volume = EXCLUDED.volume,
    logo = EXCLUDED.logo,
    setor_brapi = EXCLUDED.setor_brapi,
    tipo = EXCLUDED.tipo,
    setor_b3 = EXCLUDED.setor_b3,
    subsetor_b3 = EXCLUDED.subsetor_b3,
    data_atualizacao = CURRENT_TIMESTAMP;

-- 2. Carga completa para as outras tabelas (o restante do script permanece o mesmo)
-- ... (cole o restante do seu script a partir de "tickers_nao_mapeados" aqui) ...

-- tickers_nao_mapeados
TRUNCATE TABLE trusted_dw.tickers_nao_mapeados;
INSERT INTO trusted_dw.tickers_nao_mapeados (id, ticker, data_atualizacao)
SELECT id, ticker, CURRENT_TIMESTAMP FROM land_dw.tickers_nao_mapeados;

-- rj
TRUNCATE TABLE trusted_dw.rj;
INSERT INTO trusted_dw.rj (id, nome, ticker, setor, data_entrada_rj, data_saida_rj, data_falencia, duracao_rj, data_atualizacao)
SELECT id, nome, ticker, setor, data_entrada_rj, data_saida_rj, data_falencia, duracao_rj, CURRENT_TIMESTAMP FROM land_dw.rj;

-- scores
TRUNCATE TABLE trusted_dw.scores;
INSERT INTO trusted_dw.scores (ticker_base, score_dy, score_payout, score_roe, score_pl_pvp, score_divida, score_crescimento_sentimento, score_ciclo_mercado, score_graham, score_beta, score_market_cap, score_liquidez, score_fcf_yield, score_total, data_atualizacao)
SELECT ticker_base, score_dy, score_payout, score_roe, score_pl_pvp, score_divida, score_crescimento_sentimento, score_ciclo_mercado, score_graham, score_beta, score_market_cap, score_liquidez, score_fcf_yield, score_total, CURRENT_TIMESTAMP FROM land_dw.scores;

-- precos_acoes
TRUNCATE TABLE trusted_dw.precos_acoes;
INSERT INTO trusted_dw.precos_acoes (ticker, fechamento_atual, fechamento_1m_atras, fechamento_6m_atras, data_atualizacao)
SELECT ticker, fechamento_atual, fechamento_1m_atras, fechamento_6m_atras, CURRENT_TIMESTAMP FROM land_dw.precos_acoes;

-- preco_teto
TRUNCATE TABLE trusted_dw.preco_teto;
INSERT INTO trusted_dw.preco_teto (ticker, preco_teto_5anos, diferenca_percentual, data_atualizacao)
SELECT ticker, preco_teto_5anos, diferenca_percentual, CURRENT_TIMESTAMP FROM land_dw.preco_teto;

-- indices
TRUNCATE TABLE trusted_dw.indices;
INSERT INTO trusted_dw.indices (id, year, index, close, rsi, macd, volume, data_atualizacao)
SELECT id, year, index, close, rsi, macd, volume, CURRENT_TIMESTAMP FROM land_dw.indices;

-- indicadores
TRUNCATE TABLE trusted_dw.indicadores;
INSERT INTO trusted_dw.indicadores (ticker, empresa, subsetor_b3, tipo, market_cap, logo, preco_atual, p_l, p_vp, payout_ratio, crescimento_preco_5a, roe, divida_total, ebitda, divida_ebitda, beta, current_ratio, liquidez_media_diaria, fcf_yield, perfil_acao, lpa, vpa, margem_seguranca_percent, sentimento_gauge, strong_buy, buy, hold, sell, strong_sell, rsi_14_1y, macd_diff_1y, volume_1y, ciclo_de_mercado, status_ciclo, frase_ciclo, data_atualizacao)
SELECT ticker, empresa, subsetor_b3, tipo, market_cap, logo, preco_atual, p_l, p_vp, payout_ratio, crescimento_preco_5a, roe, divida_total, ebitda, divida_ebitda, beta, current_ratio, liquidez_media_diaria, fcf_yield, perfil_acao, lpa, vpa, margem_seguranca_percent, sentimento_gauge, strong_buy, buy, hold, sell, strong_sell, rsi_14_1y, macd_diff_1y, volume_1y, ciclo_de_mercado, status_ciclo, frase_ciclo, CURRENT_TIMESTAMP FROM land_dw.indicadores;

-- dividend_yield
TRUNCATE TABLE trusted_dw.dividend_yield;
INSERT INTO trusted_dw.dividend_yield (ticker, dy5anos, dy12m, data_atualizacao)
SELECT ticker, dy5anos, dy12m, CURRENT_TIMESTAMP FROM land_dw.dividend_yield;

-- ciclo_mercado
TRUNCATE TABLE trusted_dw.ciclo_mercado;
INSERT INTO trusted_dw.ciclo_mercado (ticker, status_ciclo, data_atualizacao)
SELECT ticker, status_ciclo, CURRENT_TIMESTAMP FROM land_dw.ciclo_mercado;

-- avaliacao_setor
TRUNCATE TABLE trusted_dw.avaliacao_setor;
INSERT INTO trusted_dw.avaliacao_setor (id, setor_b3, pontuacao_setor, subsetor_b3, pontuacao_final, score_dy, score_roe, score_beta, score_payout, score_empresas_boas, penalidade_empresas_ruins, score_graham, penalidade_rj, dy_5a_medio, roe_medio, beta_medio, payout_medio, margem_graham_media, score_original, empresas_boas_contagem, empresas_ruins_contagem, ocorrencias_rj, data_atualizacao)
SELECT id, setor_b3, pontuacao_setor, subsetor_b3, pontuacao_final, score_dy, score_roe, score_beta, score_payout, score_empresas_boas, penalidade_empresas_ruins, score_graham, penalidade_rj, dy_5a_medio, roe_medio, beta_medio, payout_medio, margem_graham_media, score_original, empresas_boas_contagem, empresas_ruins_contagem, ocorrencias_rj, CURRENT_TIMESTAMP FROM land_dw.avaliacao_setor;

-- dividendos_ano_resumo (tratada como cadastro)
TRUNCATE TABLE trusted_dw.dividendos_ano_resumo;
INSERT INTO trusted_dw.dividendos_ano_resumo (ticker, valor_5anos, valor_12m, data_atualizacao)
SELECT ticker, valor_5anos, valor_12m, CURRENT_TIMESTAMP FROM land_dw.dividendos_ano_resumo;

-- 3. Carga incremental para tabelas não-cadastro
-- todos_dividendos
INSERT INTO trusted_dw.todos_dividendos (id, data, valor, ticker, data_atualizacao)
SELECT src.id, src.data, src.valor, src.ticker, CURRENT_TIMESTAMP
FROM land_dw.todos_dividendos src
WHERE src.data >= CURRENT_DATE - INTERVAL '60 days'
  AND src.ticker IN (SELECT ticker FROM trusted_dw.acoes_e_fundos)
ON CONFLICT (id) DO UPDATE
SET data = EXCLUDED.data,
    valor = EXCLUDED.valor,
    ticker = EXCLUDED.ticker,
    data_atualizacao = CURRENT_TIMESTAMP;

-- precos_acoes_completo
INSERT INTO trusted_dw.precos_acoes_completo (id, ticker, ano, fechamento, data_atualizacao)
SELECT src.id, src.ticker, src.ano, src.fechamento, CURRENT_TIMESTAMP
FROM land_dw.precos_acoes_completo src
WHERE src.ano >= EXTRACT(YEAR FROM CURRENT_DATE) - 1
  AND src.ticker IN (SELECT ticker FROM trusted_dw.acoes_e_fundos)
ON CONFLICT (id) DO UPDATE
SET ticker = EXCLUDED.ticker,
    ano = EXCLUDED.ano,
    fechamento = EXCLUDED.fechamento,
    data_atualizacao = CURRENT_TIMESTAMP;

-- dividendos_ano
INSERT INTO trusted_dw.dividendos_ano (id, ano, ticker, dividendo, data_atualizacao)
SELECT src.id, src.ano, src.ticker, src.dividendo, CURRENT_TIMESTAMP
FROM land_dw.dividendos_ano src
WHERE src.ano >= EXTRACT(YEAR FROM CURRENT_DATE) - 1
  AND src.ticker IN (SELECT ticker FROM trusted_dw.acoes_e_fundos)
ON CONFLICT (id) DO UPDATE
SET ano = EXCLUDED.ano,
    ticker = EXCLUDED.ticker,
    dividendo = EXCLUDED.dividendo,
    data_atualizacao = CURRENT_TIMESTAMP;

COMMIT;