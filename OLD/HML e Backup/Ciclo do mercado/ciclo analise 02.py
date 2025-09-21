import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import random

# Lista de ações brasileiras
tickers = {
    "VALE3": "VALE3.SA",
    "PETR4": "PETR4.SA",
    "TAEE4": "TAEE4.SA"
}

# Frases por ciclo de mercado
frases_por_ciclo = {
    "Pânico / Fundo": [
        {"autor": "Howard Marks", "frase": "O risco está mais baixo quando o preço está mais baixo.", "status": "Compra"},
        {"autor": "George Soros", "frase": "A reflexividade transforma medo em oportunidade.", "status": "Compra"},
        {"autor": "Luiz Barsi", "frase": "O mercado dá presentes para quem não tem medo.", "status": "Compra"},
        {"autor": "Warren Buffett", "frase": "As melhores oportunidades vêm quando ninguém quer comprar.", "status": "Compra"}
    ],
    "Neutro / Transição": [
        {"autor": "Howard Marks", "frase": "Você não pode prever, mas pode se preparar.", "status": "Observação"},
        {"autor": "George Soros", "frase": "Não é sobre estar certo, é sobre estar lucrativo.", "status": "Observação"},
        {"autor": "Luiz Barsi", "frase": "Tenha paciência: o mercado sempre volta à razão.", "status": "Observação"},
        {"autor": "Warren Buffett", "frase": "É melhor esperar por uma oportunidade clara do que agir na dúvida.", "status": "Observação"}
    ],
    "Euforia / Topo": [
        {"autor": "Howard Marks", "frase": "O maior risco surge quando tudo parece seguro.", "status": "Venda"},
        {"autor": "George Soros", "frase": "Quando todos estão certos, é hora de duvidar.", "status": "Venda"},
        {"autor": "Luiz Barsi", "frase": "Quem compra na euforia, paga caro pela empolgação.", "status": "Venda"},
        {"autor": "Warren Buffett", "frase": "Seja temeroso quando os outros são gananciosos.", "status": "Venda"}
    ]
}

# Classificação com emojis financeiros
def classificar(valor, lim_baixo, lim_alto, tipo):
    valor = float(valor)
    if tipo == "RSI":
        if valor < lim_baixo:
            return "📉 Baixo"
        elif valor > lim_alto:
            return "📈 Alto"
        else:
            return "📊 Médio"
    elif tipo == "MACD":
        if valor < lim_baixo:
            return "🐻 Baixa"
        elif valor > lim_alto:
            return "🐂 Alta"
        else:
            return "⚖️ Neutra"
    elif tipo == "Volume":
        if valor < lim_baixo:
            return "🪙 Fraco"
        elif valor > lim_alto:
            return "🏦 Forte"
        else:
            return "💰 Normal"

# Análise dos indicadores
def analisar_indicadores(df):
    close = df['Close'].dropna()
    volume = df['Volume'].dropna()

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    rsi = ta.momentum.RSIIndicator(close=close).rsi()
    macd = ta.trend.MACD(close=close).macd_diff()
    vol_mean = float(volume.mean())

    rsi_val = float(rsi.iloc[-1])
    macd_val = float(macd.iloc[-1])
    vol_val = float(volume.iloc[-1])

    rsi_status = classificar(rsi_val, 30, 70, "RSI")
    macd_status = classificar(macd_val, -0.5, 0.5, "MACD")
    vol_status = classificar(vol_val, vol_mean * 0.8, vol_mean * 1.2, "Volume")

    return {
        "RSI (Sentimento)": {"valor": rsi_val, "classificacao": rsi_status},
        "MACD (Tendência)": {"valor": macd_val, "classificacao": macd_status},
        "Volume (Convicção)": {"valor": vol_val, "classificacao": vol_status}
    }

# Classificação do ciclo
def classificar_ciclo(score):
    if score <= 30:
        return "Pânico / Fundo"
    elif score <= 60:
        return "Neutro / Transição"
    else:
        return "Euforia / Topo"

# Streamlit UI
st.set_page_config(page_title="📈 Análise Técnica Consolidada", layout="wide")
st.title("📊 Indicadores Técnicos + Score de Mercado")
st.subheader("Análise consolidada de VALE3, PETR4, TAEE4")

periodo = "1y"
tabela_consolidada = []

for nome, ticker in tickers.items():
    df = yf.download(ticker, period=periodo)

    if not df.empty:
        try:
            indicadores = analisar_indicadores(df)
            score_total = 0

            for indicador in indicadores.values():
                if "Baixo" in indicador["classificacao"] or "Fraco" in indicador["classificacao"] or "🐻" in indicador["classificacao"]:
                    score_total += 10
                elif "Médio" in indicador["classificacao"] or "Normal" in indicador["classificacao"] or "⚖️" in indicador["classificacao"]:
                    score_total += 33
                elif "Alto" in indicador["classificacao"] or "Forte" in indicador["classificacao"] or "🐂" in indicador["classificacao"]:
                    score_total += 100

            score_medio = round(score_total / 3)
            ciclo = classificar_ciclo(score_medio)
            frase_escolhida = random.choice(frases_por_ciclo[ciclo])
            status = frase_escolhida["status"]
            frase_final = f"“{frase_escolhida['frase']}” — *{frase_escolhida['autor']}*"

            tabela_consolidada.append({
                "Ação 🏢": nome,
                "RSI (Sentimento)": f"{indicadores['RSI (Sentimento)']['valor']:.2f}",
                "MACD (Tendência)": f"{indicadores['MACD (Tendência)']['valor']:.2f}",
                "Volume (Convicção)": f"{indicadores['Volume (Convicção)']['valor']:.0f}",
                "Classificação 🧭": f"{indicadores['RSI (Sentimento)']['classificacao']}, {indicadores['MACD (Tendência)']['classificacao']}, {indicadores['Volume (Convicção)']['classificacao']}",
                "Score 📈": score_medio,
                "Ciclo de Mercado": ciclo,
                "Status 🟢🔴": status,
                "Frase 💬": frase_final
            })

            st.markdown(f"### 📌 {nome}")
            for k, v in indicadores.items():
                st.write(f"**{k}:** {v['valor']:.2f} → {v['classificacao']}")
            st.markdown("---")

        except Exception as e:
            st.error(f"Erro ao analisar {nome}: {e}")
    else:
        st.error(f"Não foi possível obter dados para {nome}.")

# Exibir tabela final consolidada
df_consolidada = pd.DataFrame(tabela_consolidada)[[
    "Ação 🏢", "RSI (Sentimento)", "MACD (Tendência)", "Volume (Convicção)",
    "Classificação 🧭", "Score 📈", "Ciclo de Mercado", "Status 🟢🔴", "Frase 💬"
]]

st.subheader("📋 Tabela Consolidada de Indicadores + Score de Mercado")
st.dataframe(df_consolidada, use_container_width=True)
