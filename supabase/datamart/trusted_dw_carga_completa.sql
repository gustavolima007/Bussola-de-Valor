-- Carga completa da tabela trusted_dw.acoes_e_fundos
INSERT INTO trusted_dw.acoes_e_fundos SELECT * FROM land_dw.acoes_e_fundos;

-- Carga completa da tabela trusted_dw.todos_dividendos
INSERT INTO trusted_dw.todos_dividendos SELECT * FROM land_dw.todos_dividendos;

-- Carga completa da tabela trusted_dw.tickers_nao_mapeados
INSERT INTO trusted_dw.tickers_nao_mapeados SELECT * FROM land_dw.tickers_nao_mapeados;

-- Carga completa da tabela trusted_dw.scores
INSERT INTO trusted_dw.scores SELECT * FROM land_dw.scores;

-- Carga completa da tabela trusted_dw.precos_acoes_completo
INSERT INTO trusted_dw.precos_acoes_completo SELECT * FROM land_dw.precos_acoes_completo;

-- Carga completa da tabela trusted_dw.precos_acoes
INSERT INTO trusted_dw.precos_acoes SELECT * FROM land_dw.precos_acoes;

-- Carga completa da tabela trusted_dw.preco_teto
INSERT INTO trusted_dw.preco_teto SELECT * FROM land_dw.preco_teto;

-- Carga completa da tabela trusted_dw.indicadores
INSERT INTO trusted_dw.indicadores SELECT * FROM land_dw.indicadores;

-- Carga completa da tabela trusted_dw.dividendos_ano_resumo
INSERT INTO trusted_dw.dividendos_ano_resumo SELECT * FROM land_dw.dividendos_ano_resumo;

-- Carga completa da tabela trusted_dw.dividendos_ano
INSERT INTO trusted_dw.dividendos_ano SELECT * FROM land_dw.dividendos_ano;

-- Carga completa da tabela trusted_dw.dividend_yield
INSERT INTO trusted_dw.dividend_yield SELECT * FROM land_dw.dividend_yield;

-- Carga completa da tabela trusted_dw.avaliacao_setor
INSERT INTO trusted_dw.avaliacao_setor SELECT * FROM land_dw.avaliacao_setor;

-- Carga completa da tabela trusted_dw.ciclo_mercado
INSERT INTO trusted_dw.ciclo_mercado SELECT * FROM land_dw.ciclo_mercado;

-- Carga completa da tabela trusted_dw.rj
INSERT INTO trusted_dw.rj SELECT * FROM land_dw.rj;

-- Carga completa da tabela trusted_dw.indices
INSERT INTO trusted_dw.indices SELECT * FROM land_dw.indices;