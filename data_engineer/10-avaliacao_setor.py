# -*- coding: utf-8 -*-
"""
 sectoral Performance Evaluation Script

This script evaluates the performance of different economic sectors based on the
average score of the assets that compose them.

Process Steps:
1.  Loads the scores from 'data/scores.csv' and the asset list from
    'data/acoes_e_fundos.csv'.
2.  Merges the two datasets using the ticker as a key.
3.  Groups the data by sector and calculates the average `score_total` for each.
4.  Translates the sector names from English to Portuguese using predefined
    dictionaries for a full and a summarized version.
5.  Saves the resulting sector performance ranking in
    'data/avaliacao_setor.csv'.
"""

from pathlib import Path
import pandas as pd

# --- Dictionaries for Sector Translation ---
# Full translation from English (Brapi) to Portuguese
TRADUCAO_SETORES_B3 = {
    "Energy Minerals": "Petróleo, Gás e Biocombustíveis",
    "Non-Energy Minerals": "Materiais Básicos – Mineração e Siderurgia",
    "Process Industries": "Materiais Básicos – Papel, Química e Outros",
    "Utilities": "Utilidade Pública – Energia Elétrica, Água e Saneamento",
    "Finance": "Financeiro e Outros – Bancos, Seguros, Serviços Financeiros",
    "Health Technology": "Saúde – Equipamentos e Tecnologia",
    "Health Services": "Saúde – Serviços Médicos e Hospitalares",
    "Producer Manufacturing": "Bens Industriais – Máquinas e Equipamentos",
    "Industrial Services": "Bens Industriais – Serviços Industriais",
    "Transportation": "Bens Industriais – Transporte e Logística",
    "Retail Trade": "Consumo Cíclico – Comércio Varejista",
    "Consumer Durables": "Consumo Cíclico – Bens Duráveis (Eletrodomésticos, Automóveis)",
    "Consumer Services": "Consumo Cíclico – Serviços (Educação, Turismo)",
    "Commercial Services": "Consumo Cíclico – Serviços Comerciais",
    "Electronic Technology": "Tecnologia da Informação – Hardware e Equipamentos",
    "Technology Services": "Tecnologia da Informação – Serviços de Software",
    "Communications": "Comunicações e Telecom – Telefonia, Internet e Mídia",
    "Consumer Non-Durables": "Consumo não Cíclico – Alimentos, Bebidas e Produtos Pessoais",
    "Distribution Services": "Consumo não Cíclico – Comércio e Distribuição"
}

# Summarized translation for easier display
TRADUCAO_SETORES_RESUMIDA = {
    "Petróleo, Gás e Biocombustíveis": "Petróleo, Gás e Biocombustíveis",
    "Materiais Básicos – Mineração e Siderurgia": "Mineração e Siderurgia",
    "Materiais Básicos – Papel, Química e Outros": "Papel, Química e Outros",
    "Utilidade Pública – Energia Elétrica, Água e Saneamento": "Energia Elétrica e Saneamento",
    "Financeiro e Outros – Bancos, Seguros, Serviços Financeiros": "Bancos, Seguros e Financeiros",
    "Saúde – Equipamentos e Tecnologia": "Saúde – Tecnologia e Equipamentos",
    "Saúde – Serviços Médicos e Hospitalares": "Saúde – Serviços Médicos",
    "Bens Industriais – Máquinas e Equipamentos": "Máquinas e Equipamentos Industriais",
    "Bens Industriais – Serviços Industriais": "Serviços Industriais",
    "Bens Industriais – Transporte e Logística": "Transporte e Logística",
    "Consumo Cíclico – Comércio Varejista": "Comércio Varejista",
    "Consumo Cíclico – Bens Duráveis (Eletrodomésticos, Automóveis)": "Bens Duráveis (Eletro e Autos)",
    "Consumo Cíclico – Serviços (Educação, Turismo)": "Serviços de Educação e Turismo",
    "Consumo Cíclico – Serviços Comerciais": "Serviços Comerciais",
    "Tecnologia da Informação – Hardware e Equipamentos": "Tecnologia – Hardware",
    "Tecnologia da Informação – Serviços de Software": "Tecnologia – Software",
    "Comunicações e Telecom – Telefonia, Internet e Mídia": "Telefonia, Internet e Mídia",
    "Consumo não Cíclico – Alimentos, Bebidas e Produtos Pessoais": "Alimentos, Bebidas e Higiene",
    "Consumo não Cíclico – Comércio e Distribuição": "Distribuição e Comércio"
}

def main() -> None:
    """Main function to orchestrate the sector evaluation process."""
    # --- Path Setup ---
    data_dir = Path(__file__).resolve().parent.parent / "data"
    scores_path = data_dir / "scores.csv"
    acoes_path = data_dir / "acoes_e_fundos.csv"
    output_path = data_dir / "avaliacao_setor.csv"

    # --- Data Loading ---
    print(f"Loading scores from: {scores_path}")
    scores_df = pd.read_csv(scores_path)
    print(f"Loading asset data from: {acoes_path}")
    acoes_df = pd.read_csv(acoes_path)

    # --- Data Preparation and Merging ---
    print("Merging scores with sector data...")
    # Normalize ticker in acoes_df to match scores_df (e.g., 'BBAS3.SA' -> 'BBAS3')
    acoes_df["ticker_base"] = acoes_df["ticker"].str.upper().str.strip()
    scores_df["ticker_base"] = scores_df["ticker"].str.upper().str.strip()

    # Select necessary columns and merge
    merged_df = pd.merge(
        scores_df[["ticker_base", "score_total"]],
        acoes_df[["ticker_base", "setor_brapi"]],
        on="ticker_base",
        how="inner"
    ).drop_duplicates("ticker_base")

    # --- Sector Performance Calculation ---
    print("Calculating average score per sector...")
    setor_performance = (
        merged_df.groupby("setor_brapi")["score_total"]
        .mean()
        .reset_index()
        .rename(columns={"setor_brapi": "setor", "score_total": "pontuacao"})
        .sort_values("pontuacao", ascending=False)
    )

    # --- Translation and Formatting ---
    print("Translating sector names...")
    # Apply full and summarized translations
    setor_performance['setor'] = setor_performance['setor'].map(TRADUCAO_SETORES_B3).fillna(setor_performance['setor'])
    setor_performance['setor_resumido'] = setor_performance['setor'].map(TRADUCAO_SETORES_RESUMIDA).fillna(setor_performance['setor'])
    setor_performance['pontuacao'] = setor_performance['pontuacao'].round(2)

    # --- Saving the Result ---
    setor_performance.to_csv(output_path, index=False, float_format='%.2f')
    print(f"\n✅ Sector evaluation file saved successfully at: {output_path}")

    # --- Displaying Results ---
    print("\n--- Sector Performance (Average Score) ---")
    print(setor_performance)

    if not setor_performance.empty:
        best_sector = setor_performance.iloc[0]
        print(f"\n🏆 Best Performing Sector: {best_sector['setor_resumido']} (Average Score: {best_sector['pontuacao']:.2f})")

if __name__ == "__main__":
    main()