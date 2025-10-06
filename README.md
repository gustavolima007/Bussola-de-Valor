# 📈 Bússola de Valor – Investidor Fundamentalista

Dashboard interativo em **Python + Streamlit** para análise fundamentalista de ações da B3, focado na construção de uma carteira de investimentos voltada para o recebimento de dividendos.

> **Inspirado pelas estratégias e filosofia de grandes investidores como Décio Bazin, Warren Buffett e Luiz Barsi, este portal busca unir o melhor da análise fundamentalista com tecnologia acessível para todos.**

---

## 🚀 Como Utilizar

### Pré-requisitos
- Python 3.10+
- Git

### Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/Bussola-de-Valor.git
   cd Bussola-de-Valor
   ```
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Executando a Aplicação
Para visualizar o dashboard, execute o aplicativo Streamlit:
```bash
streamlit run app/app.py
```

### Atualizando os Dados (Opcional)
O banco de dados (`dw.duckdb`) já vem populado no repositório. Para executar o pipeline completo de extração e transformação de dados manualmente, utilize o script principal:
```bash
python run.py
```
**Nota:** Este processo é executado automaticamente de segunda a sexta-feira via GitHub Actions, e as atualizações são enviadas para o repositório.

---

## 🏛️ Arquitetura de Dados

O projeto utiliza uma arquitetura de dados moderna em três camadas (Land, Trusted e DW) para garantir qualidade e performance.

1.  **Extração e Camada Land (Raw Data)**:
    *   Os scripts em `data_engineer/` (orquestrados por `data_engineer/loader.py`) extraem dados brutos de fontes como **brapi** e **yfinance**.
    *   Os dados são salvos em formato **Parquet** no diretório `duckdb/land_dw/`. Esta camada armazena os dados em seu estado original.

2.  **Transformação e Camada Trusted (Processed Data)**:
    *   O script `duckdb/carga/01-carga_completa.py` lê os dados da camada Land.
    *   Aplica limpezas, transformações, cálculos de indicadores e a lógica de scoring.
    *   Os dados tratados e enriquecidos são salvos em formato **Parquet** no diretório `duckdb/trusted_dw/`.

3.  **Data Warehouse (DW)**:
    *   O script `duckdb/carga/03-duckdb_dw.py` carrega os dados da camada Trusted para o data warehouse final.
    *   O DW é um único arquivo **DuckDB** (`duckdb/banco_dw/dw.duckdb`), que oferece alta performance para consultas analíticas e se integra perfeitamente com o Streamlit.

4.  **Visualização**:
    *   O aplicativo Streamlit (`app/app.py`) lê os dados diretamente do arquivo `dw.duckdb` para alimentar os gráficos e tabelas do dashboard.

---

## 🛠️ Tecnologias Utilizadas

-   **Python**: Linguagem principal para todo o projeto.
-   **Streamlit**: Framework para a criação do dashboard interativo.
-   **DuckDB**: Banco de dados analítico embutido, utilizado como Data Warehouse.
-   **Pandas**: Biblioteca para manipulação e análise de dados.
-   **Parquet**: Formato de arquivo colunar para armazenamento eficiente nas camadas Land e Trusted.
-   **brapi & yfinance**: APIs para obtenção de dados do mercado financeiro.
-   **GitHub Actions**: Para automação do pipeline de ETL e atualização diária do banco de dados.

---

## 📂 Estrutura de Diretórios

```
/Bussola-de-Valor/
│
├── app/                  # Código da aplicação Streamlit.
│   ├── components/       # Módulos da UI (filtros, abas).
│   ├── styles/           # Arquivos de estilização (CSS).
│   ├── data_loader.py    # Funções para carregar dados do DW para o app.
│   └── app.py            # Ponto de entrada da aplicação Streamlit.
│
├── data_engineer/        # Scripts do pipeline de extração (Camada Land).
│   ├── 01-acoes_e_fundos.py
│   ├── ...
│   └── loader.py         # Orquestrador que executa os scripts de extração.
│
├── duckdb/               # Contém toda a estrutura do data warehouse.
│   ├── land_dw/          # Dados brutos em formato Parquet.
│   ├── trusted_dw/       # Dados processados e enriquecidos em Parquet.
│   ├── banco_dw/         # Data Warehouse final.
│   │   └── dw.duckdb
│   └── carga/            # Scripts para o pipeline de carga (Trusted e DW).
│       ├── 01-carga_completa.py
│       └── ...
│
├── .github/workflows/    # Definição do workflow de automação (GitHub Actions).
│   └── main.yml
│
├── run.py                # Script principal para executar o pipeline de dados completo.
│
├── requirements.txt      # Lista de dependências Python.
│
└── README.md             # Esta documentação.
```

---

## 🧠 Filosofia do Investidor Inteligente

A pontuação das ações e setores é baseada em uma combinação de métricas fundamentalistas, inspirada em grandes investidores.

### Critérios de Pontuação (Score) – Ações (Máximo 1000 pontos)

| Categoria                 | Indicador                  | Pontuação Máxima | Peso  |
| ------------------------- | -------------------------- | ---------------- | ----- |
| **Dividendos**            | DY (12m e Média 5a)        | 200 pts          | 20%   |
| **Valuation**             | P/L e P/VP                 | 180 pts          | 18%   |
| **Rentabilidade**         | ROE e Payout               | 110 pts          | 11%   |
| **Saúde Financeira**      | Dívida/MCap, Dívida/EBITDA | 130 pts          | 13%   |
| **Crescimento**           | Preço (5a) e Sentimento    | 90 pts           | 9%    |
| **Timing de Mercado**     | Ciclo (Medo/Ganância)      | 70 pts           | 7%    |
| **Margem de Segurança**   | Fórmula de Graham          | 150 pts          | 15%   |
| **Volatilidade**          | Beta                       | 35 pts           | 3.5%  |
| **Capitalização**         | Market Cap                 | 35 pts           | 3.5%  |
| **Liquidez**              | Volume Médio Diário        | 35 pts           | 3.5%  |
| **Geração de Caixa**      | FCF Yield                  | 35 pts           | 3.5%  |
| **Penalidades**           | Recuperação Judicial       | -100 pts         | N/A   |


---

## 📊 Guia de Perfil da Ação

-   **Blue Chip**: Valor de Mercado > R$ 50 bi
-   **Mid Cap**: R$ 10 bi – R$ 50 bi
-   **Small Cap**: R$ 2 bi – R$ 10 bi
-   **Micro Cap**: < R$ 2 bi
-   **Penny Stock**: Preço < R$ 1,00

---

## 🏦 Setores Perenes (Foco em Dividendos)

-   **Bancos & Seguros**: Essenciais, lucrativos, pagadores consistentes.
-   **Energia Elétrica**: Demanda constante, contratos longos, receita estável.
-   **Saneamento**: Serviço essencial, monopólio natural, receita previsível.
-   **Telecomunicações**: Essencial na era digital, receitas recorrentes.