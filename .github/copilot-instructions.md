# Copilot Instructions for Bussola-de-Valor

## Linguagem e Versão
- Usar **Python 3.13.7**.
- Seguir as boas práticas da **PEP8**.
- Sempre usar **type hints** em todas as funções.

## Estrutura do Projeto
- O código da aplicação principal fica em `app/`.
- Os scripts de engenharia de dados ficam em `data_engineer/`.
- Os dados brutos ficam em `data/`.
- O ponto de entrada da aplicação é `app/app.py`.

## Estilo de Código
- Usar `snake_case` para variáveis e funções.
- Usar `PascalCase` para classes.
- Importações sempre organizadas: primeiro libs padrão, depois libs externas, por fim módulos locais.
- Evitar funções muito longas; preferir funções curtas e coesas.
- Comentários e docstrings devem ser **em português**.

## Boas Práticas
- Incluir **docstrings** no formato Google em todas as funções.
- Tratar erros com `try/except` quando houver operações de I/O, rede ou parsing de dados.
- Evitar variáveis globais.
- Priorizar legibilidade sobre otimização prematura.

## Bibliotecas
- Para análise e manipulação de dados: `pandas`, `numpy`.
- Para gráficos: `plotly`.
- Para indicadores financeiros: `yfinance`, `fundamentus`, `ta`.
- Para ETL: usar `SQLAlchemy`, `pandas` e scripts em `data_engineer/`.
- Para interface: `streamlit`.
- Para tradução e normalização de texto: `deep-translator`, `unidecode`.
- Para progresso em loops: `tqdm`.

## Estilo Visual
- Toda a estilização deve ser centralizada em `app/styles/styles.css`.
- O layout da aplicação deve ser construído em `app/components/`.