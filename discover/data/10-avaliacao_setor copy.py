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

    # Print selected columns
    print("scores.csv -> [ticker_base, score_total]")
    print(scores_df[["ticker_base", "score_total"]])

    print("\nacoes_e_fundos.csv -> [ticker, setor_brapi]")
    print(acoes_df[["ticker", "setor_brapi"]])


if __name__ == "__main__":
    main()