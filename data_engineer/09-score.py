from pathlib import Path
import pandas as pd
import numpy as np
import csv  # solicitado

# Gera pontuações (score_total e componentes) por ticker combinando indicadores,
# DY e preço teto: normaliza, faz merges e aplica regras de pontuação equivalentes
# às do app, salvando ../data/scores.csv para uso direto na interface.

# Caminhos dos arquivos de entrada/saída (relativos ao script)
SCRIPT_DIR = Path(__file__).resolve().parent
BASE = (SCRIPT_DIR.parent / "data").resolve()
FN_INDICADORES = BASE / "indicadores.csv"
FN_DY = BASE / "dividend_yield.csv"
FN_PRECO_TETO = BASE / "preco_teto.csv"
FN_OUT = BASE / "scores.csv"


def normalize_ticker_base(s: str) -> str:
    """Remove sufixo .SA e normaliza ticker para UPPER sem espaços."""
    s = str(s).strip().upper()
    if s.endswith('.SA'):
        s = s[:-3]
    return s


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    indic = pd.read_csv(FN_INDICADORES)
    dy = pd.read_csv(FN_DY)
    try:
        preco_teto = pd.read_csv(FN_PRECO_TETO)
    except FileNotFoundError:
        preco_teto = pd.DataFrame(columns=['ticker', 'preco_teto_5anos', 'diferenca_percentual'])
    return indic, dy, preco_teto


def prepare(indic: pd.DataFrame, dy: pd.DataFrame, preco_teto: pd.DataFrame) -> pd.DataFrame:
    # Normaliza chave de join
    indic['ticker_base'] = indic['ticker'].apply(normalize_ticker_base)
    dy['ticker_base'] = dy['ticker'].apply(normalize_ticker_base)
    preco_teto['ticker_base'] = preco_teto['ticker'].apply(normalize_ticker_base)

    # Merge DY
    df = indic.merge(dy[['ticker_base', 'DY12M', 'DY5anos']], on='ticker_base', how='left')

    # Merge preço teto (não pontua no score atual, apenas informativo)
    if not preco_teto.empty:
        df = df.merge(preco_teto[['ticker_base', 'preco_teto_5anos', 'diferenca_percentual']], on='ticker_base', how='left')

    # Converte colunas numéricas necessárias
    num_cols = [
        'preco_atual', 'p_l', 'p_vp', 'payout_ratio', 'crescimento_preco', 'roe',
        'divida_total', 'market_cap', 'divida_ebitda', 'sentimento_gauge',
        'strong_buy', 'buy', 'hold', 'sell', 'strong_sell',
        'DY12M', 'DY5anos'
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    return df


# --- Funções de pontuação (espelham app/app.py) ---

def score_dy_12m(v: float) -> int:
    if pd.isna(v) or v <= 0:
        return 0 if (pd.isna(v) or v == 0) else -5
    if v > 5:
        return 20
    if v > 3.5:
        return 15
    if v > 2:
        return 10
    if v < 2:
        return -5
    return 0


def score_dy_5anos(v: float) -> int:
    if pd.isna(v):
        return 0
    if v > 8:
        return 25
    if v > 6:
        return 20
    if v > 4:
        return 10
    return 0


def score_payout(v: float) -> int:
    if pd.isna(v):
        return 0
    if 30 <= v <= 60:
        return 10
    if 60 < v <= 80:
        return 5
    if (v > 0 and v < 20) or v > 80:
        return -5
    return 0


def score_roe(v: float, setor: str) -> int:
    s = str(setor).lower()
    if pd.isna(v):
        return 0
    if 'finance' in s:
        if v > 15:
            return 25
        if v > 12:
            return 20
        if v > 8:
            return 10
        return 0
    else:
        if v > 12:
            return 15
        if v > 8:
            return 5
        return 0


def score_pl(v: float) -> int:
    if pd.isna(v) or v <= 0:
        return 0
    if 0 < v < 12:
        return 15
    if 12 <= v < 18:
        return 10
    if v > 25:
        return -5
    return 0


def score_pvp(v: float) -> int:
    if pd.isna(v) or v <= 0:
        return 0
    if 0 < v < 0.66:
        return 20
    if 0.66 <= v < 1.5:
        return 10
    if 1.5 <= v < 2.5:
        return 5
    if v > 4:
        return -5
    return 0


def score_divida_marketcap(div_total: float, mcap: float, setor: str) -> int:
    s = str(setor).lower()
    if 'finance' in s:
        return 0
    if pd.isna(mcap) or mcap <= 0 or pd.isna(div_total):
        return 0
    ratio = div_total / mcap
    if ratio < 0.5:
        return 10
    if ratio < 1.0:
        return 5
    if ratio > 2.0:
        return -5
    return 0


def score_divida_ebitda(v: float, setor: str) -> int:
    s = str(setor).lower()
    if 'finance' in s:
        return 0
    if pd.isna(v) or v <= 0:
        return 0
    if v < 1:
        return 10
    if v < 2:
        return 5
    if v > 6:
        return -5
    return 0


def score_crescimento(v: float) -> int:
    if pd.isna(v):
        return 0
    if v > 15:
        return 15
    if v > 10:
        return 10
    if v > 5:
        return 5
    if v < 0:
        return -5
    return 0


def score_sentimento(v: float) -> float:
    if pd.isna(v):
        return 0.0
    if v >= 50:
        return ((v - 50) / 50.0) * 10.0
    else:
        return ((v - 50) / 50.0) * 5.0


def compute_scores(row: pd.Series) -> pd.Series:
    setor = row.get('setor_brapi', 'N/A')
    out = {}
    out['score_dy_12m'] = score_dy_12m(row.get('DY12M'))
    out['score_dy_5anos'] = score_dy_5anos(row.get('DY5anos'))
    out['score_payout'] = score_payout(row.get('payout_ratio'))
    out['score_roe'] = score_roe(row.get('roe'), setor)
    out['score_pl'] = score_pl(row.get('p_l'))
    out['score_pvp'] = score_pvp(row.get('p_vp'))
    out['score_divida_marketcap'] = score_divida_marketcap(row.get('divida_total'), row.get('market_cap'), setor)
    out['score_divida_ebitda'] = score_divida_ebitda(row.get('divida_ebitda'), setor)
    out['score_crescimento'] = score_crescimento(row.get('crescimento_preco'))
    out['score_sentimento'] = score_sentimento(row.get('sentimento_gauge'))

    total = sum([v for v in out.values() if not pd.isna(v)])
    total = max(0, min(200, total))  # clamp 0..200
    out['score_total'] = total
    return pd.Series(out)


def main() -> None:
    indic, dy, preco_teto = load_inputs()
    df = prepare(indic, dy, preco_teto)

    # Calcula scores
    scores = df.apply(compute_scores, axis=1)

    # Monta saída com identificadores e pontuações
    saida = pd.concat([
        df[['ticker_base']].copy(),  # sem .SA
        scores
    ], axis=1)

    # Ordena por score_total desc
    saida = saida.sort_values(by='score_total', ascending=False)

    # Salva CSV de scores
    FN_OUT.parent.mkdir(parents=True, exist_ok=True)
    saida.to_csv(FN_OUT, index=False)
    print(f'✅ Arquivo salvo em: {FN_OUT}')


if __name__ == '__main__':
    main()