# 📈 Bússola de Valor – Investidor Fundamentalista

Dashboard interativo em **Python + Streamlit** para análise fundamentalista de ações da B3, focado na construção de uma carteira de investimentos voltada para o recebimento de dividendos.

> **Inspirado pelas estratégias e filosofia de grandes investidores como Décio Bazin, Warren Buffett e Luiz Barsi, este portal busca unir o melhor da análise fundamentalista com tecnologia acessível para todos.**

---

## 🚀 Tecnologias Utilizadas

Este projeto utiliza um stack tecnológico moderno e integrado para coleta, armazenamento, análise e visualização de dados financeiros:

- **Python**: Linguagem principal para extração, transformação e análise de dados financeiros, utilizando bibliotecas como `pandas` para manipulação de dados e `plotly` para visualizações interativas.
- **yfinance e brapi**: APIs para obtenção de dados de mercado em tempo real e históricos da B3, incluindo preços de ações, dividendos e indicadores fundamentalistas.
- **Supabase**: Banco de dados relacional SQL (baseado em PostgreSQL) para armazenamento estruturado de dados de ações, métricas financeiras e resultados de scoring.
- **Streamlit**: Framework Python para criação do dashboard interativo, hospedado no **Streamlit Community Cloud** para acesso público via link.
- **GitHub Repository**: Repositório para versionamento do código-fonte, garantindo controle e colaboração no desenvolvimento.
- **GitHub Projects**: Ferramenta de Kanban para gerenciamento do projeto, organizando tarefas como coleta de dados, modelagem do banco e desenvolvimento do dashboard.

---

## 🧠 Filosofia do Investidor Inteligente

### Critérios de Pontuação (Score)
A pontuação de cada ação soma critérios fundamentalistas e técnicos, totalizando até **300 pontos**:

1. **Dividend Yield (DY) – até 50 pts**
   - DY 12 meses: >5% (+20), 3.5%-5% (+15), 2%-3.5% (+10), <2% (-5)
   - DY média 5 anos: >10% (+30), 8%-10% (+25), 6%-8% (+20), 4%-6% (+10)

2. **Valuation (P/L e P/VP) – até 60 pts**
   - P/L: <12 (+15), 12-18 (+10), >25 (-5)
   - P/VP: <0.50 (+45), 0.50-0.66 (+40), 0.66-1.00 (+30), 1.00-1.50 (+15), 1.50-2.50 (+5), >4.00 (-10)

3. **Rentabilidade e Gestão (ROE e Payout) – até 35 pts**
   - ROE (Setor Financeiro): >15% (+25), 12%-15% (+20), 8%-12% (+10)
   - ROE (Outros Setores): >12% (+15), 8%-12% (+5)
   - Payout: 30%-60% (+10), 60%-80% (+5), <20% ou >80% (-5)

4. **Saúde Financeira (Endividamento e Liquidez) – até 40 pts**
   - Dívida/Market Cap: <0.3 (+15), 0.3-0.7 (+10), >1.5 (-10)
   - Dívida/EBITDA: <1 (+15), 1-3 (+5), >5 (-10)
   - Current Ratio: >2 (+10), 1-2 (+5), <1 (-5)

5. **Crescimento e Sentimento – até 25 pts**
   - Crescimento Preço 5 Anos: >15% (+15), 10%-15% (+10), 5%-10% (+5), <0% (-5)
   - Sentimento do Mercado: -5 a +10 (proporcional à nota de 0 a 100)

6. **Ciclo de Mercado (Timing) – de -20 a +20 pts**
   - Análise técnica (RSI, MACD, Volume) para avaliar o momento psicológico do mercado.
   - Compra (Pânico / Medo Extremo): **+20 pontos**
   - Observação (Neutro / Incerteza): **0 pontos**
   - Venda (Euforia / Ganância Extrema): **-20 pontos**

7. **Fórmula de Graham (Margem de Segurança) – de -20 a +40 pts**
   - Análise do "preço justo" (`√(22.5 * LPA * VPA)`) em relação ao preço atual.
   - Margem > 200%: **+40 pontos**
   - Margem 150% a 200%: **+35 pontos**
   - Margem 100% a 150%: **+30 pontos**
   - Margem 50% a 100%: **+20 pontos**
   - Margem 20% a 50%: **+10 pontos**
   - Margem 0% a 20%: **+5 pontos**
   - Margem < 0%: **-20 pontos**

8. **Volatilidade (Beta) – de -10 a +10 pts**
   - Mede a volatilidade da ação em relação ao mercado (Ibovespa).
   - Beta < 1 (Baixa Volatilidade): **+10 pontos**
   - Beta > 1.5 (Alta Volatilidade): **-10 pontos**

9. **Capitalização de Mercado – até 10 pts**
   - Blue Cap (> R$ 50 bilhões): **+10 pontos**
   - Mid Cap (R$ 10B – R$ 50B): **+7 pontos**
   - Small Cap (R$ 2B – R$ 10B): **+4 pontos**
   - Micro Cap (< R$ 2 bilhões): **0 pontos**

10. **Liquidez Média Diária – até 10 pts**
    - > R$ 50 milhões/dia: **+10 pontos**
    - R$ 20M – R$ 50M/dia: **+7 pontos**
    - R$ 5M – R$ 20M/dia: **+4 pontos**
    - < R$ 5 milhões/dia: **0 pontos**

11. **Geração de Caixa (FCF Yield) – até 10 pts**
    - > 8%: **+10 pontos**
    - 5%–8%: **+5 pontos**
    - < 5%: **0 pontos**

---

### Análise e Pontuação de Setores

Para evitar a compra de "cascudos" (ações de empresas ruins em setores problemáticos), o Bússola de Valor aplica uma análise criteriosa sobre o desempenho geral de cada setor e subsetor da bolsa. A pontuação final de um setor é uma soma de múltiplos fatores que refletem não apenas o score individual das empresas, mas também a saúde e o histórico do ecossistema em que elas operam.

O cálculo é feito em duas etapas:

**1. Pontuação do Subsetor**

Cada subsetor (ex: "Energia Elétrica", "Intermediários Financeiros") recebe uma `pontuacao_final` que é a soma dos seguintes componentes:

*   **Componentes Positivos (Máximo de 500 pontos)**:
    *   **Score Original (`score_original`)**: A média do `Score Total` de todas as empresas do subsetor. Pontuação máxima: **300 pontos**.
    *   **Score de Dividend Yield (`score_dy`)**: Bônus ou penalidade com base na média de Dividend Yield dos últimos 5 anos (`dy_5a_medio`). Pontuação máxima: **50 pontos**.
        *   `>= 10%`: **+50 pontos**
        *   `8% a 10%`: **+40 pontos**
        *   `6% a 8%`: **+30 pontos**
        *   `4% a 6%`: **+20 pontos**
        *   `2% a 4%`: **-10 pontos**
        *   `< 2%`: **-20 pontos**
    *   **Score de ROE (`score_roe`)**: Bônus baseado no Retorno sobre o Patrimônio Líquido médio (`roe_medio`). Pontuação máxima: **40 pontos**.
        *   `> 25%`: **+40 pontos**
        *   `20% a 25%`: **+30 pontos**
        *   `15% a 20%`: **+20 pontos**
        *   `10% a 15%`: **+10 pontos**
    *   **Score de Beta (`score_beta`)**: Bônus ou penalidade baseado na volatilidade média do subsetor (`beta_medio`). Pontuação máxima: **20 pontos**.
        *   `< 0.8`: **+20 pontos**
        *   `0.8 a 1.2`: **+10 pontos**
        *   `> 1.5`: **-10 pontos**
    *   **Score de Payout (`score_payout`)**: Bônus baseado na média de Payout (`payout_medio`). Pontuação máxima: **20 pontos**.
        *   `30% a 60%`: **+20 pontos**
        *   `20% a 30%` ou `60% a 80%`: **+10 pontos**
    *   **Bônus por Empresas Boas (`score_empresas_boas`)**: Bônus pela quantidade de empresas com `Score Total` > 150. Pontuação máxima: **40 pontos**.
        *   `>= 8 empresas`: **+40 pontos**
        *   `6 a 7 empresas`: **+30 pontos**
        *   `3 a 5 empresas`: **+20 pontos**
        *   `1 a 2 empresas`: **+10 pontos**
    *   **Score de Graham (`score_graham`)**: Bônus baseado na média da margem de segurança de Graham (`margem_graham_media`). Pontuação máxima: **30 pontos**.
        *   `> 150%`: **+30 pontos**
        *   `100% a 150%`: **+20 pontos**
        *   `50% a 100%`: **+10 pontos**

*   **Penalidades**:
    *   **Penalidade por Empresas Ruins (`penalidade_empresas_ruins`)**: Penalidade pela quantidade de empresas com `Score Total` < 50.
        *   `>= 6 empresas`: **-30 pontos**
        *   `3 a 5 empresas`: **-20 pontos**
        *   `1 a 2 empresas`: **-10 pontos**
    *   **Penalidade por Recuperação Judicial (`penalidade_rj`)**: Penalidade de até **-40 pontos** baseada no número de empresas em Recuperação Judicial no subsetor.

**Fórmula e Pontuação Máxima:**

A soma dos componentes positivos é limitada a **500 pontos**. A pontuação final é calculada como:
`pontuacao_final = min(Soma dos Componentes Positivos, 500) + penalidade_empresas_ruins + penalidade_rj`

**2. Pontuação do Setor**

A pontuação do setor principal (ex: "Financeiro", "Utilidade Pública") é a média das `pontuacao_final` de todos os seus subsetores.

Essa abordagem permite identificar setores resilientes e com bom histórico, ao mesmo tempo que alerta para aqueles com riscos sistêmicos ou má fama, ajudando o investidor a "pescar no aquário certo".

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
├── data/                 # Armazena os arquivos .csv gerados e consumidos pelo pipeline.
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
