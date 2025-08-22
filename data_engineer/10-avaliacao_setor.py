from pathlib import Path
import pandas as pd

# Dicionário fixo para tradução dos setores B3 (EN -> PT)
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

# Dicionário para setores resumidos
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

    # Tradução dos setores (EN->PT) usando dicionário fixo
    setor_perf['setor'] = setor_perf['setor'].map(TRADUCAO_SETORES_B3).fillna(setor_perf['setor'])

    # Adiciona coluna setor_resumido
    setor_perf['setor_resumido'] = setor_perf['setor'].map(TRADUCAO_SETORES_RESUMIDA).fillna(setor_perf['setor'])

    print("Desempenho por setor (média de score_total):")
    print(setor_perf)

    # Salva resultado em CSV na pasta data
    out_path = data_dir / "avaliacao_setor.csv"
    # Arredonda a pontuação para 2 casas e salva com ponto decimal
    setor_perf['pontuacao'] = pd.to_numeric(setor_perf['pontuacao'], errors='coerce').round(2)
    setor_perf.to_csv(out_path, index=False, encoding="utf-8", float_format='%.2f')
    print(f"Arquivo salvo em: {out_path}")

    if not setor_perf.empty:
        melhor = setor_perf.iloc[0]
        print(f"\nMelhor setor: {melhor['setor']} (pontuação média: {melhor['pontuacao']:.2f})")


if __name__ == "__main__":
    main()