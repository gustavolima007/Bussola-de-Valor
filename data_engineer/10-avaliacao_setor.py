from pathlib import Path
import pandas as pd


def main() -> None:
    # Resolve repo root from this file location: repo_root/data_engineer/this_file.py -> repo_root
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"

    scores_path = data_dir / "scores.csv"
    acoes_path = data_dir / "acoes_e_fundos.csv"

    # Read CSVs
    scores_df = pd.read_csv(scores_path, encoding="utf-8")
    acoes_df = pd.read_csv(acoes_path, encoding="utf-8")

    # Normaliza: ticker da base de acoes vem como BBAS3.SA; convertemos para BBAS3 para casar com ticker_base
    acoes_df = acoes_df.copy()
    acoes_df["ticker_base"] = acoes_df["ticker"].str.split(".").str[0]

    # Seleciona colunas necessárias
    scores_sel = scores_df[["ticker_base", "score_total"]]
    acoes_sel = acoes_df[["ticker_base", "setor_brapi"]]

    # Join pelos tickers normalizados
    merged = (
        scores_sel.merge(acoes_sel, on="ticker_base", how="inner")
        .drop_duplicates("ticker_base")  # garante 1 linha por ticker
    )

    # Agrega: média da pontuação por setor
    setor_perf = (
        merged.groupby("setor_brapi", as_index=False)["score_total"].mean()
        .rename(columns={"setor_brapi": "setor", "score_total": "pontuacao"})
        .sort_values("pontuacao", ascending=False)
    )

    print("Desempenho por setor (média de score_total):")
    print(setor_perf)

    if not setor_perf.empty:
        melhor = setor_perf.iloc[0]
        print(f"\nMelhor setor: {melhor['setor']} (pontuação média: {melhor['pontuacao']:.2f})")


if __name__ == "__main__":
    main()