# Carga incremental (trusted_dw_carga_incremental.sql)

Este documento descreve como funciona o script de carga incremental localizado em `trusted_dw_carga_incremental.sql` e como utilizá-lo no Supabase/Postgres.

## Objetivo

O script realiza a sincronização das tabelas do schema `land_dw` (landing/raw) para o schema `trusted_dw` (trusted). Para a maioria das tabelas ele aplica um filtro de janela temporal (últimos 30 dias) e realiza UPSERTs (INSERT ... ON CONFLICT DO UPDATE) para inserir ou atualizar os registros.

## Tabelas classificadas como "cadastro"

Algumas tabelas são consideradas de cadastro e, por isso, o comportamento do script para essas tabelas é diferente: a cópia é feita 100% (todos os registros), sem filtrar por `data_atualizacao`. Essas tabelas são:

- `tickers_nao_mapeados`
- `rj`
- `scores`
- `precos_acoes`
- `preco_teto`
- `indices`
- `indicadores`
- `dividend_yield`
- `ciclo_mercado`
- `avaliacao_setor`
- `acoes_e_fundos`
- dividendos_ano_resumo

Para essas tabelas o script faz INSERT ... SELECT sem a cláusula WHERE que limita pela janela de 30 dias (ou seja, insere/atualiza todos os registros presentes em `land_dw`).

Tabelas Incrementais
Com base no seu contexto inicial, as tabelas incrementais (ou seja, aquelas que não são consideradas de cadastro e, portanto, devem ser atualizadas incrementalmente) são:

todos_dividendos
precos_acoes_completo
dividendos_ano

## Perguntas frequentes / Observações

- Por que usar UPSERT (ON CONFLICT)?
	- Para garantir que, ao reexecutar o script, registros já existentes sejam atualizados com novos valores sem gerar duplicatas.

- Performance: e se as tabelas de cadastro forem grandes?
	- Copiar 100% dos registros em uma tabela grande pode ser custoso. Se a tabela for muito grande, considere:
		- Fazer uma carga incremental por versão (comparar hashes/timestamps) ao invés de copiar tudo sempre;
		- Rodar a carga de cadastro em horários de baixa utilização;
		- Criar índices apropriados nas colunas usadas para ON CONFLICT;
		- Usar batch/partitioning quando permitido.

- Permissões necessárias:
	- O role que executar o script precisa ter SELECT nas tabelas `land_dw.*` e INSERT/UPDATE nas tabelas `trusted_dw.*`.

- Sobre a coluna `data_atualizacao`:
	- O filtro por janela (30 dias) depende da existência desta coluna nas tabelas `land_dw`. Certifique-se que as tabelas de origem têm `data_atualizacao TIMESTAMP`. Caso contrário, ajuste o script.

## Como testar (passo-a-passo curto)

1. No Supabase SQL editor, cole o conteúdo de `supabase/datamart/trusted_dw_carga_incremental.sql`.
2. Execute o script (ou execute por partes).
3. Verifique algumas tabelas destino com queries simples:

	 SELECT count(*) FROM trusted_dw.tickers_nao_mapeados;
	 SELECT max(data_atualizacao) FROM trusted_dw.precos_acoes_completo;

4. Se ocorrerem erros, copie a mensagem aqui para que eu ajude a diagnosticar.

## Recomendações

- Preferir listas explícitas de colunas nos INSERTs (já aplicadas no script) para evitar ambiguidade entre origem e destino.
- Evitar `SELECT *` em scripts de ETL/ELT.
- Se quiser que apenas alterações sejam aplicadas nas tabelas de cadastro, podemos implementar uma estratégia incremental por comparação (hashes, triggers, ou colunas de controle).

---

Se quiser, eu removo totalmente as cláusulas WHERE das tabelas de cadastro (já marquei no script) — diga apenas se prefere que o SELECT nessas tabelas não contenha nenhuma cláusula WHERE (para garantir 100% dos registros em cada execução). 

