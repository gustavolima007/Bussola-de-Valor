from pathlib import Path
from typing import List

import time
import duckdb
import pandas as pd
import streamlit as st


def get_db_path() -> Path:
    """Localiza o arquivo DuckDB na mesma pasta do script.

    Returns:
        Path: Caminho para o arquivo .duckdb encontrado.
    """
    base_dir = Path(__file__).parent
    candidate = base_dir / "dw.duckdb"
    if candidate.exists():
        return candidate
    # fallback: pega o primeiro .duckdb na pasta
    for file in base_dir.glob("*.duckdb"):
        return file
    raise FileNotFoundError("Arquivo .duckdb não encontrado na pasta do script.")


def list_tables(db_path: Path) -> List[str]:
    """Lista tabelas do banco DuckDB.

    Args:
        db_path (Path): Caminho do arquivo DuckDB.

    Returns:
        List[str]: Lista com nomes das tabelas disponíveis.
    """
    try:
        with duckdb.connect(str(db_path)) as conn:
            result = conn.execute("SHOW TABLES").fetchall()
        return [row[0] for row in result]
    except Exception:
        return []


@st.cache_data(ttl=60)
def load_table(db_path: Path, table_name: str) -> pd.DataFrame:
    """Carrega uma tabela do DuckDB para um DataFrame pandas.

    Args:
        db_path (Path): Caminho do arquivo DuckDB.
        table_name (str): Nome da tabela a ser carregada.

    Returns:
        pd.DataFrame: Dados carregados da tabela.
    """
    try:
        with duckdb.connect(str(db_path)) as conn:
            df = conn.execute(f"SELECT * FROM \"{table_name}\"").df()
        return df
    except Exception as exc:
        st.error(f"Erro ao carregar tabela '{table_name}': {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def execute_sql(db_path: Path, sql: str) -> pd.DataFrame:
    """Executa uma query SQL no arquivo DuckDB e retorna um DataFrame.

    Args:
        db_path (Path): Caminho para o arquivo DuckDB.
        sql (str): Consulta SQL a ser executada.

    Returns:
        pd.DataFrame: Resultado da consulta.
    """
    try:
        with duckdb.connect(str(db_path)) as conn:
            df = conn.execute(sql).df()
        return df
    except Exception as exc:
        # Propaga exceção para o chamador tratar e exibir mensagem amigável no Streamlit
        raise RuntimeError(f"Erro ao executar SQL: {exc}") from exc


def set_sql_for_table(table_name: str, limit: int) -> None:
    """Define um SQL padrão no session_state para a tabela selecionada.

    Args:
        table_name (str): Nome da tabela.
        limit (int): Limite de linhas a incluir no SELECT.
    """
    st.session_state["sql"] = f'SELECT * FROM "{table_name}" LIMIT {limit}'


def main() -> None:
    """Ponto de entrada do app Streamlit: exibe um DataFrame do DuckDB e permite executar SQL."""
    st.set_page_config(page_title="Preview DuckDB", layout="wide")
    st.title("Visualizador de tabela - dw.duckdb")

    try:
        db_path = get_db_path()
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    tables = list_tables(db_path)
    if not tables:
        st.warning("Nenhuma tabela encontrada no banco.")
        return

    # inicializa estado para o SQL
    if "sql" not in st.session_state:
        st.session_state["sql"] = ""

    selected_table = st.selectbox("Selecione a tabela", tables)
    max_rows = st.number_input(
        "Número máximo de linhas a mostrar",
        min_value=10,
        max_value=10000,
        value=500,
        step=10,
    )

    # layout: duas colunas — preview à esquerda, área SQL à direita
    col_preview, col_sql = st.columns([2, 1])

    with col_preview:
        df = load_table(db_path, selected_table)
        if df.empty:
            st.info("Tabela vazia ou erro ao carregar.")
        else:
            st.write(f"Tabela: {selected_table} — {df.shape[0]} linhas x {df.shape[1]} colunas")
            st.dataframe(df.head(int(max_rows)), use_container_width=True)

    with col_sql:
        st.subheader("Executar SQL")
        st.caption("Escreva uma query SQL para consultar o arquivo dw.duckdb")

        # botão para gerar SELECT padrão para a tabela selecionada
        if st.button("Gerar SELECT para tabela"):
            set_sql_for_table(selected_table, int(max_rows))

        sql_input = st.text_area(
            "SQL",
            value=st.session_state["sql"],
            height=200,
            placeholder='Ex: SELECT * FROM "minha_tabela" LIMIT 100',
            key="sql_text_area",
        )
        # atualiza session_state com o conteúdo do text_area (evita perda ao rerun)
        st.session_state["sql"] = sql_input

        if st.button("Executar SQL"):
            sql_to_run = st.session_state.get("sql", "").strip()
            if not sql_to_run:
                st.error("SQL vazio — escreva uma consulta antes de executar.")
            else:
                try:
                    start = time.time()
                    result_df = execute_sql(db_path, sql_to_run)
                    elapsed = time.time() - start
                    st.success(f"Consulta executada em {elapsed:.2f}s — {result_df.shape[0]} linhas")
                    st.dataframe(result_df, use_container_width=True)
                    # opção de exportar CSV
                    csv = result_df.to_csv(index=False).encode("utf-8")
                    st.download_button("Baixar CSV", csv, file_name="consulta.csv", mime="text/csv")
                except Exception as exc:
                    st.error(str(exc))


if __name__ == "__main__":
    main()