# 🧭 DW Explorer - Bússola de Valor

Explorador visual do Data Warehouse (DuckDB) da Bússola de Valor.

## 🚀 Como usar

### Executar o aplicativo

```bash
streamlit run dw.py
```

Ou a partir da raiz do projeto:

```bash
streamlit run duckdb/banco_dw/dw.py
```

## 📋 Funcionalidades

### 1. Preview de Tabelas
- Visualize rapidamente os dados de qualquer tabela
- Ajuste o número de linhas exibidas
- Veja métricas como número de linhas e colunas

### 2. Executor SQL
- Execute consultas SQL personalizadas
- Interface dividida: SQL à esquerda, resultado à direita
- Gere automaticamente SELECT para a tabela selecionada
- Exporte resultados em CSV

## 🎨 Visual

O DW Explorer segue o padrão visual da Bússola de Valor:
- Tema escuro com verde primário (#36b37e)
- Layout responsivo e moderno
- Ícones intuitivos para melhor UX

## 📊 Tabelas Disponíveis

- `indicadores` - Indicadores fundamentalistas das ações
- `dividend_yield` - Dados de dividend yield
- `scores` - Pontuações calculadas
- `preco_teto` - Preços teto calculados
- `precos_acoes` - Histórico de preços
- `avaliacao_setor` - Avaliação por setor
- `ciclo_mercado` - Dados de ciclo de mercado
- `indices` - Índices de mercado
- E outras...

## 💡 Exemplos de Consultas SQL

### Buscar ações específicas
```sql
SELECT * FROM "indicadores" 
WHERE ticker LIKE '%PETR%' 
LIMIT 100
```

### Top 10 ações por dividend yield
```sql
SELECT ticker, "DY12m", "DY5anos" 
FROM "dividend_yield" 
ORDER BY "DY12m" DESC 
LIMIT 10
```

### Análise de setor
```sql
SELECT subsetor_b3, COUNT(*) as total_acoes, AVG(roe) as roe_medio
FROM "indicadores"
GROUP BY subsetor_b3
ORDER BY roe_medio DESC
```

## 🔧 Configuração

O arquivo `.streamlit/config.toml` contém as configurações de tema e servidor.