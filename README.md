# 📈 Finance Manager: Análise de Ações e Carteira de Dividendos

Dashboard interativo em **Python + Streamlit** para análise fundamentalista de ações da B3, focado na construção de uma carteira de investimentos voltada para o recebimento de dividendos.

> **Inspirado pelas estratégias e filosofia de grandes investidores como Décio Bazin, Warren Buffett e Luiz Barsi, este portal busca unir o melhor da análise fundamentalista com tecnologia acessível para todos.**

---

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.8 ou superior
- Acesso a dados de mercado (ex.: via [yfinance](https://github.com/ranaroussi/yfinance) ou arquivo CSV)
- Vontade de construir uma carteira de dividendos que te faça sorrir todo mês! 😄

### 2. Instale as Dependências
Crie um arquivo `requirements.txt` com:
```
streamlit
pandas
yfinance
plotly
```
Instale os pacotes:
```bash
pip install -r requirements.txt
```

### 3. Execute o Dashboard
Rode o script principal:
```bash
streamlit run app.py
```
> **Dica:** Use o script `transform.py` para gerar um arquivo CSV com os dados mais recentes da B3, base para o dashboard.

---

## 🌟 Evolução do Projeto

- **Fase 1:** Dashboards iniciais em Power BI para controle de orçamento e investimentos.
- **Fase 2:** Migração para Python/Streamlit para análises em tempo real de ações e fundos.
- **Próximos Passos:** Modo "Big Dividend Hunter", integração com APIs premium e otimização dos modelos de scoring. Fique ligado!

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
- **Blue Chip:** Valor de Mercado > R$ 50 bi
- **Mid Cap:** R$ 10 bi – R$ 50 bi
- **Small Cap:** R$ 2 bi – R$ 10 bi
- **Micro Cap:** < R$ 2 bi
- **Penny Stock:** Preço < R$ 1,00

---

## 🏛️ Análise Setorial (Foco em Dividendos)

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
