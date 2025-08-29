# -*- coding: utf-8 -*-
"""
📈 Ciclo de Mercado - Transformação de Dados

- Remove Streamlit e yfinance: este script agora apenas lê dados existentes e produz um CSV consolidado.
- Fonte dos dados: utiliza data/indicadores.csv (gerado pelo 08-indicadores.py),
  especificamente as colunas técnicas: rsi_14_1y, macd_diff_1y e volume_1y.
- Saída: data/ciclo_mercado.csv com classificações e frases por ciclo.
"""

from pathlib import Path
import pandas as pd
import random

# --- Parâmetros de caminhos ---
BASE = Path(__file__).resolve().parent.parent / 'data'
ARQ_INDICADORES = BASE / 'indicadores.csv'
ARQ_SAIDA = BASE / 'ciclo_mercado.csv'

# --- Frases por ciclo de mercado ---
frases_por_ciclo = {
    "Pânico / Fundo": [
        {"autor": "Howard Marks", "frase": "O risco está mais baixo quando o preço está mais baixo.", "status": "Compra"},
        {"autor": "George Soros", "frase": "A reflexividade transforma medo em oportunidade.", "status": "Compra"},
        {"autor": "Luiz Barsi", "frase": "O mercado dá presentes para quem não tem medo.", "status": "Compra"},
        {"autor": "Warren Buffett", "frase": "As melhores oportunidades vêm quando ninguém quer comprar.", "status": "Compra"},
    ],
    "Neutro / Transição": [
        {"autor": "Howard Marks", "frase": "Você não pode prever, mas pode se preparar.", "status": "Observação"},
        {"autor": "George Soros", "frase": "Não é sobre estar certo, é sobre estar lucrativo.", "status": "Observação"},
        {"autor": "Luiz Barsi", "frase": "Tenha paciência: o mercado sempre volta à razão.", "status": "Observação"},
        {"autor": "Warren Buffett", "frase": "É melhor esperar por uma oportunidade clara do que agir na dúvida.", "status": "Observação"},
    ],
    "Euforia / Topo": [
        {"autor": "Howard Marks", "frase": "O maior risco surge quando tudo parece seguro.", "status": "Venda"},
        {"autor": "George Soros", "frase": "Quando todos estão certos, é hora de duvidar.", "status": "Venda"},
        {"autor": "Luiz Barsi", "frase": "Quem compra na euforia, paga caro pela empolgação.", "status": "Venda"},
        {"autor": "Warren Buffett", "frase": "Seja temeroso quando os outros são gananciosos.", "status": "Venda"},
    ],
}

# --- Classificadores ---

def classificar(valor: float, lim_baixo: float, lim_alto: float, tipo: str) -> str:
    """Classifica um valor conforme o tipo do indicador."""
    if pd.isna(valor):
        return "N/A"
    v = float(valor)
    if tipo == "RSI":
        if v < lim_baixo:
            return "📉 Baixo"
        elif v > lim_alto:
            return "📈 Alto"
        else:
            return "📊 Médio"
    elif tipo == "MACD":
        if v < lim_baixo:
            return "🐻 Baixa"
        elif v > lim_alto:
            return "🐂 Alta"
        else:
            return "⚖️ Neutra"
    elif tipo == "Volume":
        if v < lim_baixo:
            return "🪙 Fraco"
        elif v > lim_alto:
            return "🏦 Forte"
        else:
            return "💰 Normal"
    return "N/A"


def classificar_ciclo(score: float) -> str:
    if pd.isna(score):
        return "Neutro / Transição"
    if score <= 30:
        return "Pânico / Fundo"
    elif score <= 60:
        return "Neutro / Transição"
    else:
        return "Euforia / Topo"


# --- Núcleo de transformação ---

def montar_ciclo_mercado(df_ind: pd.DataFrame) -> pd.DataFrame:
    """Monta a tabela consolidada de ciclo do mercado usando indicadores já calculados."""
    if df_ind.empty:
        return pd.DataFrame()

    # Normaliza nome do ticker base
    df = df_ind.copy()
    if 'ticker' in df.columns:
        df['Ticker'] = df['ticker'].astype(str).str.upper().str.replace('.SA', '', regex=False).str.strip()
    elif 'Ticker' not in df.columns:
        raise ValueError("Coluna de ticker não encontrada em indicadores.csv")

    # Médias globais p/ referência (Volume)
    vol_mean = pd.to_numeric(df.get('volume_1y'), errors='coerce').mean()

    linhas = []
    for _, row in df.iterrows():
        rsi_val = pd.to_numeric(row.get('rsi_14_1y'), errors='coerce')
        macd_val = pd.to_numeric(row.get('macd_diff_1y'), errors='coerce')
        vol_val = pd.to_numeric(row.get('volume_1y'), errors='coerce')

        rsi_status = classificar(rsi_val, 30, 70, "RSI")
        macd_status = classificar(macd_val, -0.5, 0.5, "MACD")
        vol_status = classificar(vol_val, vol_mean * 0.8, vol_mean * 1.2, "Volume")

        # Score simples a partir das classes
        score_total = 0
        for cls in (rsi_status, macd_status, vol_status):
            if any(key in str(cls) for key in ["Baixo", "Fraco", "🐻"]):
                score_total += 10
            elif any(key in str(cls) for key in ["Médio", "Normal", "⚖️"]):
                score_total += 33
            elif any(key in str(cls) for key in ["Alto", "Forte", "🐂"]):
                score_total += 100
        score_medio = round(score_total / 3)

        ciclo = classificar_ciclo(score_medio)
        frase = random.choice(frases_por_ciclo[ciclo])
        frase_final = f"“{frase['frase']}” — {frase['autor']}"

        linhas.append({
            "Ticker": row['Ticker'],
            "RSI (Sentimento)": None if pd.isna(rsi_val) else f"{rsi_val:.2f}",
            "MACD (Tendência)": None if pd.isna(macd_val) else f"{macd_val:.3f}",
            "Volume (Convicção)": None if pd.isna(vol_val) else f"{vol_val:.0f}",
            "Classificação 🧭": f"{rsi_status}, {macd_status}, {vol_status}",
            "Score 📈": score_medio,
            "Ciclo de Mercado": ciclo,
            "Status 🟢🔴": frase["status"],
            "Frase 💬": frase_final,
        })

    cols = [
        "Ticker", "RSI (Sentimento)", "MACD (Tendência)", "Volume (Convicção)",
        "Classificação 🧭", "Score 📈", "Ciclo de Mercado", "Status 🟢🔴", "Frase 💬",
    ]
    return pd.DataFrame(linhas)[cols]


def main():
    if not ARQ_INDICADORES.exists():
        print(f"❌ Arquivo de indicadores não encontrado: {ARQ_INDICADORES}")
        return 1

    df_ind = pd.read_csv(ARQ_INDICADORES)
    df_out = montar_ciclo_mercado(df_ind)

    if df_out.empty:
        print("⚠️ Nenhum dado disponível para ciclo de mercado.")
        return 0

    ARQ_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(ARQ_SAIDA, index=False, encoding='utf-8-sig')
    print(f"✅ Ciclo de mercado salvo em: {ARQ_SAIDA} ({len(df_out)} tickers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())