# 🦆 Carga Incremental com DuckDB

Este documento descreve o processo de carga de dados incremental, desde a coleta inicial até a consolidação no banco de dados DuckDB.

## 📂 Etapa 1: Coleta e Armazenamento na Landing Zone

- **O que acontece:** Os scripts Python em `data_engineer/` são executados para coletar dados de diversas fontes.
- **Onde os dados são salvos:** Os dados brutos são salvos em formato Parquet no diretório `duckdb/land_dw/`.
- **Exemplo:** O script `data_engineer/01-acoes_e_fundos.py` coleta dados de ações e fundos e salva em `duckdb/land_dw/acoes_e_fundos.parquet`.

## ✨ Etapa 2: Transformação e Armazenamento na Trusted Zone

- **O que acontece:** Os dados da `land_dw` são lidos, transformados e preparados para análise.
- **Onde os dados são salvos:** Os dados transformados são salvos em formato Parquet no diretório `duckdb/trusted_dw/`.
- **Exemplo:** Os dados de `duckdb/land_dw/acoes_e_fundos.parquet` são processados e salvos em `duckdb/trusted_dw/acoes_e_fundos.parquet`.

## 🏦 Etapa 3: Carga no Banco de Dados DuckDB

- **O que acontece:** Os dados da `trusted_dw` são carregados no banco de dados DuckDB.
- **Onde os dados são salvos:** Os dados são salvos no arquivo `duckdb/banco_duckdb/dw.duckdb`.
- **Processo:**
    1. As tabelas no banco de dados são limpas (`DELETE FROM`).
    2. Os dados dos arquivos Parquet em `duckdb/trusted_dw/` são inseridos nas tabelas correspondentes.

## ⚖️ Tipos de Carga

Existem dois tipos de carga de dados para o banco `dw.duckdb`:

### 🚚 Carga Completa (Full Load)

Neste modo, todos os dados da tabela são apagados e uma nova carga é inserida. As seguintes tabelas seguem este modelo:

- `acoes_e_fundos`
- `avaliacao_setor`
- `ciclo_mercado`
- `dividend_yield`
- `dividendos_ano_resumo`
- `indicadores`
- `indices`
- `preco_teto`
- `precos_acoes`
- `rj`
- `scores`
- `tickers_nao_mapeados`

### 📈 Carga Incremental (Incremental Load)

Neste modo, apenas os novos registros são adicionados à tabela. As seguintes tabelas seguem este modelo:

- `todos_dividendos`
- `precos_acoes_completo`
- `dividendos_ano`

## 🔄 Fluxo de Dados

[data_engineer/*.py] --coleta--> [duckdb/land_dw/*.parquet] --transforma--> [duckdb/trusted_dw/*.parquet] --carrega--> [duckdb/banco_duckdb/dw.duckdb]
