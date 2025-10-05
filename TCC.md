# Trabalho de Conclusão de Curso (TCC)

RESUMO

Este relatório apresenta a implementação da "Bússola de Valor", uma ferramenta de apoio à decisão para investidores focados em renda por dividendos. Descreve a coleta e padronização de dados, a modelagem do Data Warehouse local em DuckDB, o cálculo de scores fundamentados e o desenvolvimento de um dashboard interativo em Streamlit. Foram gerados artefatos reproducíveis (ETL, datasets e tabelas materializadas) e validada a operação local com baixo custo operacional; o DW é atualizado automaticamente via workflow do GitHub Actions.

Palavras‑chave

dividendos, duckdb, streamlit

## I. Introdução

### 1. Contexto
Atualmente, a análise fundamentalista é uma abordagem consolidada para investidores que buscam retorno consistente e segurança na preservação de capital. Este trabalho apresenta a implementação e avaliação de uma ferramenta de apoio à decisão para investidores focados em renda por dividendos, chamada "Bússola de Valor".

A Bússola de Valor é um dashboard interativo desenvolvido em Python com Streamlit que agrega, processa e pontua (scoring) ações negociadas na B3, combinando métricas de dividendos, valuation, saúde financeira, crescimento, liquidez e volatilidade.

### 2. Objetivo

- Desenvolver uma aplicação de apoio à decisão que: (i) colete e consolide dados financeiros de múltiplas fontes; (ii) calcule um score fundamentado por critérios econômicos e de investimento; (iii) apresente visualmente rankings, detalhes por ativo e avaliações por setor/subsetor.

### 3. Motivação

- Auxiliar investidores pessoa física a identificar ações que combinam boa geração de dividendos com fundamentos robustos, apoiando a alocação de portfólios orientados à renda.
- Integrar conceitos de investidores clássicos (Décio Bazin, Benjamin Graham, Warren Buffett, Luiz Barsi) com práticas técnicas modernas (ETL, dashboards interativos, versionamento de código).

### 4. Materiais

Este trabalho foi realizado utilizando os seguintes recursos tecnológicos e bibliotecas:
- Linguagem: Python 3.11+ (o repositório recomenda 3.13.7 em instruções internas).
- Bibliotecas principais: pandas, numpy, plotly, streamlit, yfinance, joblib, python-dotenv, ta, tqdm, deep_translator.
- Infraestrutura de dados: arquivos Parquet/CSV em `data/` e Data Warehouse local em `data/bussola.duckdb` (DuckDB).
- Ferramentas de desenvolvimento: Git/GitHub para versionamento. O dashboard continua em Streamlit (sem uso de Power BI) e o arquivo DuckDB será atualizado automaticamente via GitHub Actions diariamente às 07:00.
- Scripts de ETL: presentes em `data_engineer/` (ex.: `01-acoes_e_fundos.py`, `09-score.py`, `loader.py`).

### 5. Metodologia do Trabalho

O trabalho seguiu as etapas listadas abaixo:
- Coleta e padronização de dados públicos e de APIs (yfinance / brapi) e arquivos históricos gerados pelo pipeline.
- ETL: construção de scripts para transformação e geração de artefatos CSV, seguindo a ordem numérica em `data_engineer/`.
- Cálculo de Score: implementação de regras objetivas que atribuem pontos (até 1000) por critério (DY, Valuation, ROE, Payout, Endividamento, Crescimento, Graham, etc.).
- Desenvolvimento do Dashboard: interface em Streamlit para filtragem, visualização de rankings, detalhes por ativo e painéis setoriais.
- Validação: testes manuais e execução local do pipeline para verificar coerência entre dados de entrada e as métricas exibidas.

---

## II. Revisão de Tecnologias e Práticas

### 1. Coleta de Dados e APIs
- `yfinance`: usado para preços e histórico de dividendos quando necessário.
- `brapi` / fontes CSV: integração para enriquecer atributos como setor, perfil de ação e indicadores financeiros.

### 2. ETL e Armazenamento
- Os scripts em `data_engineer/` seguem uma ordem numérica que garante dependências corretas entre passos (extração → transformação → indicadores → scoring).
- Formato de persistência: arquivos Parquet e um DW local em DuckDB (`data/bussola.duckdb`). A escolha por DuckDB dispensa servidor próprio e reduz custos operacionais. Não foi escolhida modelagem em MySQL/SQL Server por custos de hospedagem e necessidade de servidor dedicado.

### 3. Análise e Modelagem
- A modelagem de score é uma combinação de regras financeiras consagradas e heurísticas pragmáticas. A pontuação é modular e compreende componentes para dividendos, valuation, rentabilidade, saúde financeira, crescimento, volatilidade e liquidez.

### 4. Visualização e Interação
- Streamlit e Plotly são usados para construir uma interface interativa com filtros na sidebar (`app/components/filters.py`) e painéis principais (`app/components/tabs_layout.py`).

---

## III. Desenvolvimento

Nesta seção detalha-se a implementação técnica.

### 1. Arquitetura do Sistema
- Pasta `app/`: contém a aplicação Streamlit (`app.py`), o carregador de dados (`data_loader.py`) e o módulo de cálculo de score (`scoring.py`).
- Pasta `data_engineer/`: contém scripts numerados de ETL que geram os CSVs consumidos pelo app.
- Pasta `data/`: armazena os CSVs consolidados usados como entrada do dashboard.

Fluxo simplificado:
1. Executar ETL (scripts em `data_engineer/` ou usar CSVs já gerados em `data/`).
2. `app/data_loader.py` carrega e unifica os CSVs, calcula colunas derivadas (ex.: Dívida/Market Cap, Val 1M/6M) e carrega scores externos quando presente (`scores.csv`).
3. `app/scoring.py` implementa a lógica de fallback para calcular o score quando `scores.csv` não existe; há também uma versão paralela (`calculate_scores_in_parallel`) que utiliza `joblib`.
4. `app/app.py` monta a interface Streamlit, aplica CSS, configura tema Plotly e delega a renderização dos filtros e abas aos componentes.

### 2. Lógica de Scoring (resumo)
- Dividend Yield (DY): peso alto (até 200 pts), com DY médio 5 anos tendo impacto maior que o DY de 12 meses.
- Valuation (P/L e P/VP): até 180 pts, favorecendo empresas com baixo P/VP e P/L moderado.
- Rentabilidade/Gestão (ROE e Payout): até 110 pts, com regras diferenciadas para o setor financeiro.
- Saúde Financeira (Dívida/MarketCap, Dívida/EBITDA, Current Ratio): até 130 pts.
- Crescimento, Sentimento e Graham: componentes adicionais que ajustam a pontuação final.
- Outros: Beta, Liquidez média diária, FCF Yield e capitalização de mercado adicionam ajustes menores.

### 3. Boas práticas implementadas
- Carga com cache (`@st.cache_data`) para acelerar recarregamentos em Streamlit.
- Tratamento de tipos numéricos, datas e proteção contra divisão por zero no `data_loader`.
- Mensagens informativas ao usuário quando arquivos opcionais não são encontrados (ex.: `scores.csv`, `precos_acoes.csv`).

---

## IV. Resultados e Análise

### 1. Artefatos gerados
- CSVs em `data/` (ex.: `indicadores.csv`, `dividend_yield.csv`, `scores.csv`, `precos_acoes.csv`, `avaliacao_setor.csv`) que representam a base de dados consolidada.
- Dashboard Streamlit executável via `streamlit run app/app.py` que apresenta:
	- Tabela com ranking por `Score Total` e detalhes por critério (coluna `Score Details`).
	- Gráficos de DY histórico, distribuição de scores por setor e painéis de preço (1M, 6M).
	- Painel de avaliação por subsetor (pontuação final por subsetor) quando disponível em `avaliacao_setor.csv`.

### 2. Validação e Verificação
- A função `calculate_score_and_details` foi usada como referência para validar os scores quando `scores.csv` não está presente.
- O pipeline de cálculo paralelo (`calculate_scores_in_parallel`) garante escalabilidade para dezenas/centenas de tickers usando múltiplos núcleos.
- Verificações implementadas no `data_loader` asseguram coerência de tipos e evitam crashes por arquivos ausentes.

### 3. Limitações Observadas
- Dependência de dados de terceiros (yfinance/brapi) que podem mudar formato ou disponibilidade.
- Alguns campos opcionais (ex.: `Current Ratio`, `FCF Yield`, `Dívida/EBITDA`) podem não estar completos para todas as empresas, impactando a pontuação.
- O método de scoring é baseado em regras heurísticas — não é um modelo estatístico ou de machine learning; resultados refletem as escolhas de pesos e cortes definidas no projeto.

---

## V. Conclusão

O projeto "Bússola de Valor" entrega uma ferramenta operacional que combina práticas clássicas de análise fundamentalista com engenharia de dados e visualização interativa. Ele facilita a comparação entre empresas da B3 com foco em geração de dividendos e permite ao usuário investigar justificativas por critério (detalhes do score).

Recomenda-se para trabalhos futuros:
- Validar e calibrar os pesos do score com séries históricas e análise de performance (backtest de carteiras geradas pelo ranking).
- Manter o DW em DuckDB para operações locais e sem custo; avaliar migração para um banco gerenciado apenas se houver necessidade de escrita concorrente ou escalabilidade muito além do ambiente local.
- Complementar com alertas automáticos e testes automatizados do pipeline de ETL.

### 1. Dificuldades Encontradas
- Normalização dos diversos formatos de entrada e tratamento de valores faltantes.
- Definição consensual dos limites e pesos do score — exige julgamento financeiro e testes empíricos.

### 10. Aplicabilidade do Trabalho
- Ferramenta útil para investidores pessoa física que buscam compor carteiras de dividendos.
- Base para projetos acadêmicos que estudem eficácia de estratégias fundamentadas em regras.
- Pode ser apropriada para pequenos gestores ou assessorias que desejem um ranking customizável.

---

## VI. Bibliografia

Livros e referências indicadas durante o desenvolvimento e base teórica do scoring:
- Bazin, D. (Décio) — Faça fortuna com ações antes que seja tarde.
- Kiyosaki, R. T. — Pai Rico, Pai Pobre.
- Fisher, P. — Ações Comuns, Lucros Extraordinários.
- Clason, G. S. — O Homem Mais Rico da Babilônia.
- Trump, D. — A Arte da Negociação (referência citada no README).

Livros (Oracle / Banco de Dados) — sugestões para fundamentar a parte de banco de dados e engenharia:
- Loney, K. — Oracle Database 12c: The Complete Reference (ou edições mais recentes equivalentes).
- Feuerstein, S. — Oracle PL/SQL Programming.
- Kyte, T. — Expert Oracle Database Architecture.

Artigos e documentação técnica:
- Documentação do Streamlit: https://docs.streamlit.io
- pandas e numpy: documentação oficial e guias de boas práticas.
- yfinance e bibliotecas de mercado: documentação e exemplos.

---