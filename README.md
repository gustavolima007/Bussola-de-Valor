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
A pontuação de cada ação soma critérios fundamentalistas, totalizando até **200 pontos**:

1. **Dividend Yield (DY) – até 45 pts**
   - DY 12 meses: >5% (+20), 3.5%-5% (+15), 2%-3.5% (+10), <2% (-5)
   - DY média 5 anos: >8% (+25), 6%-8% (+20), 4%-6% (+10)

2. **Valuation (P/L e P/VP) – até 35 pts**
   - P/L: <12 (+15), 12-18 (+10), >25 (-5)
   - P/VP: <0.66 (+20), 0.66-1.5 (+10), 1.5-2.5 (+5), >4 (-5)

3. **Rentabilidade e Gestão (ROE e Payout) – até 35 pts**
   - ROE (Financeiro): >15% (+25), 12%-15% (+20), 8%-12% (+10)
   - ROE (Outros): >12% (+15), 8%-12% (+5)
   - Payout: 30%-60% (+10), 60%-80% (+5), fora de 20%-80% (-5)

4. **Saúde Financeira (Endividamento) – até 20 pts**
   - Dívida/Market Cap: <0.5 (+10), 0.5-1.0 (+5), >2.0 (-5)
   - Dívida/EBITDA: <1 (+10), 1-2 (+5), >6 (-5)

5. **Crescimento e Sentimento – até 25 pts**
   - Crescimento preço 5 anos: >15% (+15), 10%-15% (+10), 5%-10% (+5), <0% (-5)
   - Sentimento do mercado: -5 a +10 (proporcional à nota de 0 a 100)

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

## 🛠️ Estrutura de diretorios:

```bash
/Bussola-de-Valor/
│
├── app/
│   │
│   ├── components/
│   │   ├── __init__.py       # Transforma a pasta em um pacote Python.
│   │   ├── filters.py        # Módulo para criar os componentes de filtro na sidebar.
│   │   └── tabs_layout.py    # Módulo para renderizar todas as abas e seus conteúdos.
│   │
│   ├── styles/
│   │   └── styles.css        # Arquivo central para toda a estilização visual.
│   │
│   ├── data_loader.py        # Módulo para carregar, unificar e pré-processar todos os dados.
│   ├── scoring.py            # Isola a lógica de cálculo do score de investimento.
│   └── app.py                # Ponto de entrada: inicializa o app e orquestra os componentes.
│
├── data/
│   ├── indicadores.csv       # Exemplo de arquivo de dados brutos.
│   └── ...                   # Outros arquivos .csv
│
├── data_engineer/
│   ├── 01_extraction.py      # Scripts para extração de dados de fontes diversas.
│   └── 02_transformation.py  # Scripts para limpeza, tratamento e engenharia de features.
│
├── .gitignore                # Especifica arquivos e pastas a serem ignorados pelo Git.
│
├── README.md                 # Documentação do projeto: o que é, como instalar e executar.
│
└── requirements.txt          # Lista todas as bibliotecas Python necessárias.

```
