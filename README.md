# 📈 Bússola de Valor – Investidor Fundamentalista

Dashboard interativo em **Python + Streamlit** para análise fundamentalista de ações da B3, focado na construção de uma carteira de investimentos voltada para o recebimento de dividendos.

> **Inspirado pelas estratégias e filosofia de grandes investidores como Décio Bazin, Warren Buffett e Luiz Barsi, este portal busca unir o melhor da análise fundamentalista com tecnologia acessível para todos.**

---

## 🚀 Tecnologias Utilizadas

Este projeto utiliza um stack tecnológico moderno e integrado para coleta, armazenamento, análise e visualização de dados financeiros:

- **Python**: Linguagem principal para extração, transformação e análise de dados financeiros, utilizando bibliotecas como `pandas` para manipulação de dados e `plotly` para visualizações interativas.
- **yfinance e brapi**: APIs para obtenção de dados de mercado em tempo real e históricos da B3, incluindo preços de ações, dividendos e indicadores fundamentalistas.
 - **Supabase**: Banco de dados relacional SQL (baseado em PostgreSQL) para armazenamento estruturado de dados de ações, métricas financeiras e resultados de scoring (opção futura).
 - **DuckDB**: Data warehouse embutido (arquivo local `.duckdb`) usado neste projeto para armazenar o `trusted_dw`. Integração nativa com Parquet e consultas SQL locais rápidas sem servidor.
 - **Streamlit**: Framework Python para criação do dashboard interativo, hospedado no **Streamlit Community Cloud** para acesso público via link.
 - **GitHub Repository**: Repositório para versionamento do código-fonte, garantindo controle e colaboração no desenvolvimento.
 - **GitHub Projects**: Ferramenta de Kanban para gerenciamento do projeto, organizando tarefas como coleta de dados, modelagem do banco e desenvolvimento do dashboard.

---

## 🧠 Filosofia do Investidor Inteligente

### Critérios de Pontuação (Score) – Ações (Máximo 1000 pontos)

Dividend Yield (DY) – até 200 pts (20%)

DY 12 meses: &gt;5% (+60 pts), 3.5%-5% (+45 pts), 2%-3.5% (+30 pts), &lt;2% (-20 pts)
DY média 5 anos: &gt;10% (+120 pts), 8%-10% (+100 pts), 6%-8% (+80 pts), 4%-6% (+40 pts), &lt;3% (-20 pts), &lt;1% (-30 pts)


Valuation (P/L e P/VP) – até 180 pts (18%)

P/L: &lt;12 (+45 pts), 12-18 (+30 pts), &gt;25 (-15 pts)
P/VP: &lt;0.50 (+135 pts), 0.50-0.66 (+120 pts), 0.66-1.00 (+90 pts), 1.00-1.50 (+45 pts), 1.50-2.50 (+15 pts), &gt;4.00 (-30 pts)


Rentabilidade e Gestão (ROE e Payout) – até 110 pts (11%)

ROE (Setor Financeiro): &gt;15% (+80 pts), 12%-15% (+60 pts), 8%-12% (+30 pts)
ROE (Outros Setores): &gt;12% (+45 pts), 8%-12% (+15 pts)
Payout: 30%-60% (+30 pts), 60%-80% (+15 pts), &lt;20% ou &gt;80% (-15 pts)


Saúde Financeira (Endividamento e Liquidez) – até 130 pts (13%)

Dívida/Market Cap: &lt;0.3 (+45 pts), 0.3-0.7 (+30 pts), &gt;1.5 (-30 pts)
Dívida/EBITDA: &lt;1 (+45 pts), 1-3 (+15 pts), &gt;5 (-30 pts)
Current Ratio: &gt;2 (+40 pts), 1-2 (+20 pts), &lt;1 (-15 pts)


Crescimento e Sentimento – até 90 pts (9%)

Crescimento Preço 5 Anos: &gt;15% (+50 pts), 10%-15% (+35 pts), 5%-10% (+20 pts), &lt;0% (-20 pts)
Sentimento do Mercado: -20 a +40 pts (proporcional)


Ciclo de Mercado (Timing) – de -70 a +70 pts (7%)

Compra (Pânico / Medo Extremo): +70 pontos
Venda (Euforia / Ganância Extrema): -70 pontos


Fórmula de Graham (Margem de Segurança) – de -70 a +150 pts (15%)

Margem &gt; 200%: +150 pontos
Margem 150% a 200%: +130 pontos
Margem 100% a 150%: +110 pontos
Margem 50% a 100%: +70 pontos
Margem 20% a 50%: +35 pontos
Margem 0% a 20%: +20 pontos
Margem &lt; 0%: -70 pontos


Volatilidade (Beta) – de -35 a +35 pts (3.5%)

Beta &lt; 1: +35 pontos
Beta &gt; 1.5: -35 pontos


Capitalização de Mercado – até 35 pts (3.5%)

Blue Cap: +35 pts
Mid Cap: +25 pts
Small Cap: +15 pts


**Liquidez Média Diária – até 35 pts (3.5%)**
- > R$ 50 milhões/dia: +35 pts
- R$ 20M – R$ 50M/dia: +25 pts
- R$ 5M – R$ 20M/dia: +15 pts


**Geração de Caixa (FCF Yield) – até 35 pts (3.5%)**
- > 8%: +35 pontos
- 5%–8%: +20 pontos

---

### Pontuação de Setores (Máximo 1000 pontos)

1. Pontuação do Subsetor

Componentes Positivos (Máximo 1000 pontos):

Score Original (score_original) – até 550 pts (55%): Média do Score Total das empresas do subsetor.
Score de Dividend Yield (score_dy) – até 150 pts (15%): Bônus ou penalidade com base na média de Dividend Yield dos últimos 5 anos (dy_5a_medio).

&gt;= 10%: +150 pontos
8% a 10%: +120 pontos
6% a 8%: +90 pontos
4% a 6%: +60 pontos
2% a 4%: -30 pontos
&lt; 2%: -60 pontos
&lt; 1%: -90 pontos


Score de ROE (score_roe) – até 75 pts (7.5%): Bônus baseado no Retorno sobre o Patrimônio Líquido médio (roe_medio).

&gt; 25%: +75 pontos
20% a 25%: +55 pontos
15% a 20%: +35 pontos
10% a 15%: +20 pontos


Score de Beta (score_beta) – até 35 pts (3.5%): Bônus ou penalidade baseado na volatilidade média do subsetor (beta_medio).

&lt; 0.8: +35 pontos
0.8 a 1.2: +20 pontos
&gt; 1.5: -20 pontos


Score de Payout (score_payout) – até 35 pts (3.5%): Bônus baseado na média de Payout (payout_medio).

30% a 60%: +35 pontos
20% a 30% ou 60% a 80%: +20 pontos


Bônus por Empresas Boas (score_empresas_boas) – até 75 pts (7.5%): Bônus pela quantidade de empresas com Score Total &gt; 300.

&gt;= 8 empresas: +75 pontos
6 a 7 empresas: +55 pontos
3 a 5 empresas: +35 pontos
1 a 2 empresas: +20 pontos


Score de Graham (score_graham) – até 55 pts (5.5%): Bônus baseado na média da margem de segurança de Graham (margem_graham_media).

&gt; 150%: +55 pontos
100% a 150%: +35 pontos
50% a 100%: +20 pontos




Penalidades:

Penalidade por Empresas Ruins (penalidade_empresas_ruins) – até -60 pts (6%): Penalidade pela quantidade de empresas com Score Total &lt; 100.

&gt;= 6 empresas: -60 pontos
3 a 5 empresas: -40 pontos
1 a 2 empresas: -20 pontos


Penalidade por Recuperação Judicial (penalidade_rj) – até -80 pts (8%): Penalidade baseada no número de empresas em Recuperação Judicial no subsetor.



Fórmula e Pontuação Máxima:
A pontuação final é calculada como:
pontuacao_final = Soma dos Componentes Positivos + penalidade_empresas_ruins + penalidade_rj
2. Pontuação do Setor
A pontuação do setor principal é a média das pontuacao_final de todos os seus subsetores.

---

## 📊 Guia de Perfil da Ação

Classificação por porte e preço:
- **Blue Chip**: Valor de Mercado > R$ 50 bi
- **Mid Cap**: R$ 10 bi – R$ 50 bi
- **Small Cap**: R$ 2 bi – R$ 10 bi
- **Micro Cap**: < R$ 2 bi
- **Penny Stock**: Preço < R$ 1,00

---

## 🏛️ Setores perenes (Foco em Dividendos)

**Bancos & Seguros**
- ✔️ Essenciais, lucrativos, pagadores consistentes
- ❌ Sensíveis a crises e concorrência de fintechs

**Energia Elétrica**
- ✔️ Demanda constante, contratos longos, receita estável
- ❌ Forte regulação e risco político

**Saneamento**
- ✔️ Serviço essencial, monopólio natural, receita previsível
- ❌ Regulação intensa, alta necessidade de capital

**Telecomunicações**
- ✔️ Essencial na era digital, receitas recorrentes
- ❌ Competição acirrada, investimentos constantes, regulação forte

---

## 🛠️ Gerenciamento do Projeto

- **GitHub Projects**: Utilizado para organizar o desenvolvimento em um quadro Kanban, com tarefas divididas em fases como coleta de dados, modelagem do banco e desenvolvimento do dashboard.
- **Exemplo de uso**:
  - Crie um projeto no GitHub Projects com colunas: `To Do`, `In Progress`, `Done`.
  - Adicione tarefas como:
    - "Configurar Supabase e criar tabelas".
    - "Implementar extração de dados com yfinance e brapi".
    - "Desenvolver gráficos de scores no Streamlit com Plotly".

  **Decisão de modelagem**: adotamos DuckDB para o DW local (arquivo `data/bussola.duckdb`) em vez de MySQL/SQL Server por não exigir servidor dedicado e por reduzir custos. O DW é atualizado automaticamente por um workflow GitHub Actions agendado diariamente às 07:00.

  ### Por que DuckDB (resumo)
  - Integração nativa com Parquet e alta performance para consultas analíticas locais.
  - Opera como arquivo local sem necessidade de infraestrutura e integra-se bem ao Streamlit.

## 🛠️ Estrutura de Diretórios

```bash
/Bussola-de-Valor/
│
├── app/                  # Contém o código da aplicação Streamlit.
│   ├── components/       # Módulos que renderizam partes específicas da UI (filtros, abas).
│   │   ├── filters.py
│   │   └── tabs_layout.py
│   ├── styles/           # Arquivos de estilização (CSS).
│   │   └── styles.css
│   ├── data_loader.py    # Funções para carregar e unificar os dados para o app.
│   └── app.py            # Ponto de entrada principal da aplicação Streamlit.
│
├── data/                 # Armazena arquivos Parquet/CSV gerados e o DW local `data/bussola.duckdb`.
│   ├── parquet/
│   ├── bussola.duckdb
│   ├── acoes_e_fundos.csv
│   ├── indicadores.csv
│   ├── scores.csv
│   └── ...
│
├── data_engineer/        # Scripts do pipeline de ETL (Extração, Transformação e Carga).
│   ├── 01-nome_script.py # Scripts são numerados para garantir a ordem de execução.
│   ├── ...
│   ├── 09-score.py       # Script que calcula o score final de cada ação.
│   └── loader.py         # Orquestrador que executa todos os scripts do pipeline em sequência.
│
├── .github/              # Arquivos de configuração do GitHub (ex: instruções para o Copilot).
│
├── HML/                  # Pasta para homologação e testes de novas funcionalidades.
│
├── .gitignore                # Especifica arquivos e pastas a serem ignorados pelo Git.
│
├── README.md                 # Documentação do projeto: o que é, como instalar e executar.
│
└── requirements.txt          # Lista todas as bibliotecas Python necessárias.

```
