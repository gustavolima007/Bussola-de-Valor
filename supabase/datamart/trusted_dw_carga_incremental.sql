-- Carga incremental da tabela trusted_dw.acoes_e_fundos
INSERT INTO trusted_dw.acoes_e_fundos
SELECT * FROM land_dw.acoes_e_fundos WHERE data_atualizacao >= NOW() - INTERVAL '30 days'
ON CONFLICT (ticker) DO UPDATE SET
    empresa = EXCLUDED.empresa,
    volume = EXCLUDED.volume,
    logo = EXCLUDED.logo,
    setor_brapi = EXCLUDED.setor_brapi,
    tipo = EXCLUDED.tipo,
    setor_b3 = EXCLUDED.setor_b3,
    subsetor_b3 = EXCLUDED.subsetor_b3,
    data_atualizacao = EXCLUDED.data_atualizacao;

-- Carga incremental da tabela trusted_dw.todos_dividendos
INSERT INTO trusted_dw.todos_dividendos
SELECT * FROM land_dw.todos_dividendos WHERE data_atualizacao >= NOW() - INTERVAL '30 days'
ON CONFLICT (id) DO UPDATE SET
    data = EXCLUDED.data,
    -- Carga incremental da tabela trusted_dw.acoes_e_fundos
    -- Tabela de cadastro: acoes_e_fundos — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.acoes_e_fundos (
        ticker, empresa, volume, logo, setor_brapi, tipo, setor_b3, subsetor_b3, data_atualizacao
    )
    SELECT
        src.ticker, src.empresa, src.volume, src.logo, src.setor_brapi, src.tipo, src.setor_b3, src.subsetor_b3, src.data_atualizacao
    FROM land_dw.acoes_e_fundos AS src
    ON CONFLICT (ticker) DO UPDATE SET
        empresa = EXCLUDED.empresa,
        volume = EXCLUDED.volume,
        logo = EXCLUDED.logo,
        setor_brapi = EXCLUDED.setor_brapi,
        tipo = EXCLUDED.tipo,
        setor_b3 = EXCLUDED.setor_b3,
        subsetor_b3 = EXCLUDED.subsetor_b3,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.todos_dividendos
    INSERT INTO trusted_dw.todos_dividendos (
        id, data, valor, ticker, data_atualizacao
    )
    SELECT
        src.id, src.data, src.valor, src.ticker, src.data_atualizacao
    FROM land_dw.todos_dividendos AS src
    WHERE src.data_atualizacao >= NOW() - INTERVAL '30 days'
    ON CONFLICT (id) DO UPDATE SET
        data = EXCLUDED.data,
        valor = EXCLUDED.valor,
        ticker = EXCLUDED.ticker,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.acoes_e_fundos
    INSERT INTO trusted_dw.acoes_e_fundos (
        ticker, empresa, volume, logo, setor_brapi, tipo, setor_b3, subsetor_b3, data_atualizacao
    )
    SELECT
        src.ticker, src.empresa, src.volume, src.logo, src.setor_brapi, src.tipo, src.setor_b3, src.subsetor_b3, src.data_atualizacao
    FROM land_dw.acoes_e_fundos AS src
    WHERE src.data_atualizacao >= NOW() - INTERVAL '30 days'
    ON CONFLICT (ticker) DO UPDATE SET
        empresa = EXCLUDED.empresa,
        volume = EXCLUDED.volume,
        logo = EXCLUDED.logo,
        setor_brapi = EXCLUDED.setor_brapi,
        tipo = EXCLUDED.tipo,
        setor_b3 = EXCLUDED.setor_b3,
        subsetor_b3 = EXCLUDED.subsetor_b3,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.todos_dividendos
    INSERT INTO trusted_dw.todos_dividendos (
        id, data, valor, ticker, data_atualizacao
    )
    SELECT
        src.id, src.data, src.valor, src.ticker, src.data_atualizacao
    FROM land_dw.todos_dividendos AS src
    WHERE src.data_atualizacao >= NOW() - INTERVAL '30 days'
    ON CONFLICT (id) DO UPDATE SET
        data = EXCLUDED.data,
        valor = EXCLUDED.valor,
        ticker = EXCLUDED.ticker,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.tickers_nao_mapeados
    -- Tabela de cadastro: tickers_nao_mapeados — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.tickers_nao_mapeados (
        id, ticker, data_atualizacao
    )
    SELECT
        src.id, src.ticker, src.data_atualizacao
    FROM land_dw.tickers_nao_mapeados AS src
    ON CONFLICT (id) DO UPDATE SET
        ticker = EXCLUDED.ticker,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.scores
    -- Tabela de cadastro: scores — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.scores (
        ticker_base, score_dy, score_payout, score_roe, score_pl_pvp, score_divida,
        score_crescimento_sentimento, score_ciclo_mercado, score_graham, score_beta,
        score_market_cap, score_liquidez, score_fcf_yield, score_total, data_atualizacao
    )
    SELECT
        src.ticker_base, src.score_dy, src.score_payout, src.score_roe, src.score_pl_pvp, src.score_divida,
        src.score_crescimento_sentimento, src.score_ciclo_mercado, src.score_graham, src.score_beta,
        src.score_market_cap, src.score_liquidez, src.score_fcf_yield, src.score_total, src.data_atualizacao
    FROM land_dw.scores AS src
    ON CONFLICT (ticker_base) DO UPDATE SET
        score_dy = EXCLUDED.score_dy,
        score_payout = EXCLUDED.score_payout,
        score_roe = EXCLUDED.score_roe,
        score_pl_pvp = EXCLUDED.score_pl_pvp,
        score_divida = EXCLUDED.score_divida,
        score_crescimento_sentimento = EXCLUDED.score_crescimento_sentimento,
        score_ciclo_mercado = EXCLUDED.score_ciclo_mercado,
        score_graham = EXCLUDED.score_graham,
        score_beta = EXCLUDED.score_beta,
        score_market_cap = EXCLUDED.score_market_cap,
        score_liquidez = EXCLUDED.score_liquidez,
        score_fcf_yield = EXCLUDED.score_fcf_yield,
        score_total = EXCLUDED.score_total,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.precos_acoes_completo
    INSERT INTO trusted_dw.precos_acoes_completo (
        id, ticker, ano, fechamento, data_atualizacao
    )
    SELECT
        src.id, src.ticker, src.ano, src.fechamento, src.data_atualizacao
    FROM land_dw.precos_acoes_completo AS src
    WHERE src.data_atualizacao >= NOW() - INTERVAL '30 days'
    ON CONFLICT (id) DO UPDATE SET
        ticker = EXCLUDED.ticker,
        ano = EXCLUDED.ano,
        fechamento = EXCLUDED.fechamento,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.precos_acoes
    -- Tabela de cadastro: precos_acoes — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.precos_acoes (
        ticker, fechamento_atual, fechamento_1m_atras, fechamento_6m_atras, data_atualizacao
    )
    SELECT
        src.ticker, src.fechamento_atual, src.fechamento_1m_atras, src.fechamento_6m_atras, src.data_atualizacao
    FROM land_dw.precos_acoes AS src
    ON CONFLICT (ticker) DO UPDATE SET
        fechamento_atual = EXCLUDED.fechamento_atual,
        fechamento_1m_atras = EXCLUDED.fechamento_1m_atras,
        fechamento_6m_atras = EXCLUDED.fechamento_6m_atras,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.preco_teto
    -- Tabela de cadastro: preco_teto — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.preco_teto (
        ticker, preco_teto_5anos, diferenca_percentual, data_atualizacao
    )
    SELECT
        src.ticker, src.preco_teto_5anos, src.diferenca_percentual, src.data_atualizacao
    FROM land_dw.preco_teto AS src
    ON CONFLICT (ticker) DO UPDATE SET
        preco_teto_5anos = EXCLUDED.preco_teto_5anos,
        diferenca_percentual = EXCLUDED.diferenca_percentual,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.indicadores
    -- Tabela de cadastro: indicadores — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.indicadores (
        ticker, empresa, subsetor_b3, tipo, market_cap, logo, preco_atual, p_l, p_vp,
        payout_ratio, crescimento_preco_5a, roe, divida_total, ebitda, divida_ebitda,
        beta, current_ratio, liquidez_media_diaria, fcf_yield, perfil_acao, lpa, vpa,
        margem_seguranca_percent, sentimento_gauge, strong_buy, buy, hold, sell, strong_sell,
        rsi_14_1y, macd_diff_1y, volume_1y, ciclo_de_mercado, status_ciclo, frase_ciclo, data_atualizacao
    )
    SELECT
        src.ticker, src.empresa, src.subsetor_b3, src.tipo, src.market_cap, src.logo, src.preco_atual, src.p_l, src.p_vp,
        src.payout_ratio, src.crescimento_preco_5a, src.roe, src.divida_total, src.ebitda, src.divida_ebitda,
        src.beta, src.current_ratio, src.liquidez_media_diaria, src.fcf_yield, src.perfil_acao, src.lpa, src.vpa,
        src.margem_seguranca_percent, src.sentimento_gauge, src.strong_buy, src.buy, src.hold, src.sell, src.strong_sell,
        src.rsi_14_1y, src.macd_diff_1y, src.volume_1y, src.ciclo_de_mercado, src.status_ciclo, src.frase_ciclo, src.data_atualizacao
    FROM land_dw.indicadores AS src
    ON CONFLICT (ticker) DO UPDATE SET
        empresa = EXCLUDED.empresa,
        subsetor_b3 = EXCLUDED.subsetor_b3,
        tipo = EXCLUDED.tipo,
        market_cap = EXCLUDED.market_cap,
        logo = EXCLUDED.logo,
        preco_atual = EXCLUDED.preco_atual,
        p_l = EXCLUDED.p_l,
        p_vp = EXCLUDED.p_vp,
        payout_ratio = EXCLUDED.payout_ratio,
        crescimento_preco_5a = EXCLUDED.crescimento_preco_5a,
        roe = EXCLUDED.roe,
        divida_total = EXCLUDED.divida_total,
        ebitda = EXCLUDED.ebitda,
        divida_ebitda = EXCLUDED.divida_ebitda,
        beta = EXCLUDED.beta,
        current_ratio = EXCLUDED.current_ratio,
        liquidez_media_diaria = EXCLUDED.liquidez_media_diaria,
        fcf_yield = EXCLUDED.fcf_yield,
        perfil_acao = EXCLUDED.perfil_acao,
        lpa = EXCLUDED.lpa,
        vpa = EXCLUDED.vpa,
        margem_seguranca_percent = EXCLUDED.margem_seguranca_percent,
        sentimento_gauge = EXCLUDED.sentimento_gauge,
        strong_buy = EXCLUDED.strong_buy,
        buy = EXCLUDED.buy,
        hold = EXCLUDED.hold,
        sell = EXCLUDED.sell,
        strong_sell = EXCLUDED.strong_sell,
        rsi_14_1y = EXCLUDED.rsi_14_1y,
        macd_diff_1y = EXCLUDED.macd_diff_1y,
        volume_1y = EXCLUDED.volume_1y,
        ciclo_de_mercado = EXCLUDED.ciclo_de_mercado,
        status_ciclo = EXCLUDED.status_ciclo,
        frase_ciclo = EXCLUDED.frase_ciclo,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.dividendos_ano_resumo
    INSERT INTO trusted_dw.dividendos_ano_resumo (
        ticker, valor_5anos, valor_12m, data_atualizacao
    )
    SELECT
        src.ticker, src.valor_5anos, src.valor_12m, src.data_atualizacao
    FROM land_dw.dividendos_ano_resumo AS src
    WHERE src.data_atualizacao >= NOW() - INTERVAL '30 days'
    ON CONFLICT (ticker) DO UPDATE SET
        valor_5anos = EXCLUDED.valor_5anos,
        valor_12m = EXCLUDED.valor_12m,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.dividendos_ano
    INSERT INTO trusted_dw.dividendos_ano (
        id, ano, ticker, dividendo, data_atualizacao
    )
    SELECT
        src.id, src.ano, src.ticker, src.dividendo, src.data_atualizacao
    FROM land_dw.dividendos_ano AS src
    WHERE src.data_atualizacao >= NOW() - INTERVAL '30 days'
    ON CONFLICT (id) DO UPDATE SET
        ano = EXCLUDED.ano,
        ticker = EXCLUDED.ticker,
        dividendo = EXCLUDED.dividendo,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.dividend_yield
    -- Tabela de cadastro: dividend_yield — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.dividend_yield (
        ticker, dy5anos, dy12m, data_atualizacao
    )
    SELECT
        src.ticker, src.dy5anos, src.dy12m, src.data_atualizacao
    FROM land_dw.dividend_yield AS src
    ON CONFLICT (ticker) DO UPDATE SET
        dy5anos = EXCLUDED.dy5anos,
        dy12m = EXCLUDED.dy12m,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.avaliacao_setor
    -- Tabela de cadastro: avaliacao_setor — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.avaliacao_setor (
        id, setor_b3, pontuacao_setor, subsetor_b3, pontuacao_final, score_dy, score_roe,
        score_beta, score_payout, score_empresas_boas, penalidade_empresas_ruins, score_graham,
        penalidade_rj, dy_5a_medio, roe_medio, beta_medio, payout_medio, margem_graham_media,
        score_original, empresas_boas_contagem, empresas_ruins_contagem, ocorrencias_rj, data_atualizacao
    )
    SELECT
        src.id, src.setor_b3, src.pontuacao_setor, src.subsetor_b3, src.pontuacao_final, src.score_dy, src.score_roe,
        src.score_beta, src.score_payout, src.score_empresas_boas, src.penalidade_empresas_ruins, src.score_graham,
        src.penalidade_rj, src.dy_5a_medio, src.roe_medio, src.beta_medio, src.payout_medio, src.margem_graham_media,
        src.score_original, src.empresas_boas_contagem, src.empresas_ruins_contagem, src.ocorrencias_rj, src.data_atualizacao
    FROM land_dw.avaliacao_setor AS src
    ON CONFLICT (id) DO UPDATE SET
        setor_b3 = EXCLUDED.setor_b3,
        pontuacao_setor = EXCLUDED.pontuacao_setor,
        subsetor_b3 = EXCLUDED.subsetor_b3,
        pontuacao_final = EXCLUDED.pontuacao_final,
        score_dy = EXCLUDED.score_dy,
        score_roe = EXCLUDED.score_roe,
        score_beta = EXCLUDED.score_beta,
        score_payout = EXCLUDED.score_payout,
        score_empresas_boas = EXCLUDED.score_empresas_boas,
        penalidade_empresas_ruins = EXCLUDED.penalidade_empresas_ruins,
        score_graham = EXCLUDED.score_graham,
        penalidade_rj = EXCLUDED.penalidade_rj,
        dy_5a_medio = EXCLUDED.dy_5a_medio,
        roe_medio = EXCLUDED.roe_medio,
        beta_medio = EXCLUDED.beta_medio,
        payout_medio = EXCLUDED.payout_medio,
        margem_graham_media = EXCLUDED.margem_graham_media,
        score_original = EXCLUDED.score_original,
        empresas_boas_contagem = EXCLUDED.empresas_boas_contagem,
        empresas_ruins_contagem = EXCLUDED.empresas_ruins_contagem,
        ocorrencias_rj = EXCLUDED.ocorrencias_rj,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.ciclo_mercado
    -- Tabela de cadastro: ciclo_mercado — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.ciclo_mercado (
        ticker, status_ciclo, data_atualizacao
    )
    SELECT
        src.ticker, src.status_ciclo, src.data_atualizacao
    FROM land_dw.ciclo_mercado AS src
    ON CONFLICT (ticker) DO UPDATE SET
        status_ciclo = EXCLUDED.status_ciclo,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.rj
    -- Tabela de cadastro: rj — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.rj (
        id, nome, ticker, setor, data_entrada_rj, data_saida_rj, data_falencia, duracao_rj, data_atualizacao
    )
    SELECT
        src.id, src.nome, src.ticker, src.setor, src.data_entrada_rj, src.data_saida_rj, src.data_falencia, src.duracao_rj, src.data_atualizacao
    FROM land_dw.rj AS src
    ON CONFLICT (id) DO UPDATE SET
        nome = EXCLUDED.nome,
        ticker = EXCLUDED.ticker,
        setor = EXCLUDED.setor,
        data_entrada_rj = EXCLUDED.data_entrada_rj,
        data_saida_rj = EXCLUDED.data_saida_rj,
        data_falencia = EXCLUDED.data_falencia,
        duracao_rj = EXCLUDED.duracao_rj,
        data_atualizacao = EXCLUDED.data_atualizacao;

    -- Carga incremental da tabela trusted_dw.indices
    -- Tabela de cadastro: indices — insert 100% (sem filtro por data_atualizacao)
    INSERT INTO trusted_dw.indices (
        id, year, index, close, rsi, macd, volume, data_atualizacao
    )
    SELECT
        src.id, src.year, src.index, src.close, src.rsi, src.macd, src.volume, src.data_atualizacao
    FROM land_dw.indices AS src
    ON CONFLICT (id) DO UPDATE SET
        year = EXCLUDED.year,
        index = EXCLUDED.index,
        close = EXCLUDED.close,
        rsi = EXCLUDED.rsi,
        macd = EXCLUDED.macd,
        volume = EXCLUDED.volume,
        data_atualizacao = EXCLUDED.data_atualizacao;
