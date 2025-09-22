# -*- coding: utf-8 -*-
"""
Avaliação de desempenho por Setor e Subsetor (padrão B3)

Este script calcula as pontuações médias (score_total) por:
- setor_b3 -> coluna resultante: pontuacao_setor
- subsetor_b3 -> coluna resultante: pontuacao_subsetor

Saída: data/avaliacao_setor.csv com as colunas:
- setor_b3
- subsetor_b3
- pontuacao_setor (média por setor_b3)
- pontuacao_subsetor (média por subsetor_b3)

Observações:
- O script depende de data/scores.csv (com colunas: ticker_base, score_total)
  e data/acoes_e_fundos.csv (com colunas: ticker, setor_b3, subsetor_b3).
- O merge é feito via ticker_base (ticker normalizado para maiúsculas).
"""

from pathlib import Path
import pandas as pd


def main() -> None:
    # --- Paths ---
    data_dir = Path(__file__).resolve().parent.parent / "data"
    scores_path = data_dir / "scores.csv"
    acoes_path = data_dir / "acoes_e_fundos.csv"
    rj_path = data_dir / "rj.csv"
    output_path = data_dir / "avaliacao_setor.csv"

    # --- Load data ---
    print(f"Carregando scores: {scores_path}")
    scores_df = pd.read_csv(scores_path)
    print(f"Carregando acoes_e_fundos: {acoes_path}")
    acoes_df = pd.read_csv(acoes_path)
    print(f"Carregando dados de RJ: {rj_path}")
    rj_df = pd.read_csv(rj_path)

    # --- Preparação e Merge ---
    print("Preparando chaves de merge (ticker_base)...")
    acoes_df["ticker_base"] = acoes_df["ticker"].astype(str).str.upper().str.strip()
    if "ticker_base" not in scores_df.columns:
        # Caso o arquivo de scores tenha a coluna 'ticker' em vez de 'ticker_base'
        if "ticker" in scores_df.columns:
            scores_df["ticker_base"] = scores_df["ticker"].astype(str).str.upper().str.strip()
        else:
            raise ValueError("scores.csv precisa conter 'ticker_base' ou 'ticker'.")

    # Seleciona apenas colunas necessárias
    cols_necessarias_acoes = ["ticker_base", "setor_b3", "subsetor_b3"]
    faltantes = [c for c in ["setor_b3", "subsetor_b3"] if c not in acoes_df.columns]
    if faltantes:
        raise ValueError(
            f"Colunas ausentes em acoes_e_fundos.csv: {faltantes}. "
            "Certifique-se de ter executado 01-acoes_e_fundos.py atualizado."
        )

    merged_df = (
        pd.merge(
            scores_df[["ticker_base", "score_total"]],
            acoes_df[cols_necessarias_acoes],
            on="ticker_base",
            how="inner",
        )
        .drop_duplicates("ticker_base")
    )

    if merged_df.empty:
        print("Nenhum dado após o merge. Verifique os arquivos de entrada.")
        return

    # --- Cálculo das pontuações ---
    print("Calculando média por setor_b3 (pontuacao_setor)...")
    por_setor = (
        merged_df.groupby("setor_b3")["score_total"].mean().reset_index()
        .rename(columns={"score_total": "pontuacao_setor"})
    )

    print("Calculando média por subsetor_b3 (pontuacao_subsetor)...")
    por_subsetor = (
        merged_df.groupby("subsetor_b3")["score_total"].mean().reset_index()
        .rename(columns={"score_total": "pontuacao_original_subsetor"})
    )

    # --- Cálculo da Penalidade por Recuperação Judicial ---
    print("Calculando penalidade por RJ...")
    # O campo 'setor' no rj.csv corresponde ao 'subsetor_b3'
    rj_counts = rj_df['setor'].value_counts().reset_index()
    rj_counts.columns = ['subsetor_b3', 'ocorrencias_rj']

    # Merge com os subsetores para aplicar a penalidade
    por_subsetor = pd.merge(por_subsetor, rj_counts, on='subsetor_b3', how='left')
    por_subsetor['ocorrencias_rj'].fillna(0, inplace=True)

    # Cálculo da penalidade normalizada e ajustada
    min_ocorrencias = por_subsetor['ocorrencias_rj'].min()
    max_ocorrencias = por_subsetor['ocorrencias_rj'].max()
    
    # Evita divisão por zero se todos os setores tiverem o mesmo número de ocorrências
    if (max_ocorrencias - min_ocorrencias) > 0:
        por_subsetor['penalidade_normalizada'] = (por_subsetor['ocorrencias_rj'] - min_ocorrencias) / (max_ocorrencias - min_ocorrencias)
    else:
        por_subsetor['penalidade_normalizada'] = 0

    # Aplica o fator de impacto de 20 pontos
    por_subsetor['penalidade_rj'] = por_subsetor['penalidade_normalizada'] * 20
    
    # Calcula a pontuação final do subsetor aplicando a penalidade
    por_subsetor['pontuacao_subsetor'] = por_subsetor['pontuacao_original_subsetor'] - por_subsetor['penalidade_rj']
    
    # Remove colunas intermediárias
    por_subsetor.drop(columns=['ocorrencias_rj', 'penalidade_normalizada'], inplace=True)

    # --- Monta base final por combinação de Setor x Subsetor ---
    print("Compondo base final por Setor x Subsetor...")
    base_chaves = (
        merged_df[["setor_b3", "subsetor_b3"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )

    resultado = (
        base_chaves
        .merge(por_setor, on="setor_b3", how="left")
        .merge(por_subsetor, on="subsetor_b3", how="left")
    )

    # Arredonda
    for col in ["pontuacao_setor", "pontuacao_original_subsetor", "pontuacao_subsetor", "penalidade_rj"]:
        if col in resultado.columns:
            resultado[col] = resultado[col].round(2)

    # Ordena por melhor setor e subsetor
    resultado = resultado.sort_values(
        by=["pontuacao_setor", "pontuacao_subsetor"], ascending=[False, False]
    )

    # --- Salva ---
    resultado.to_csv(output_path, index=False, float_format="%.2f")
    print(f"OK. Arquivo salvo em: {output_path}")


if __name__ == "__main__":
    main()