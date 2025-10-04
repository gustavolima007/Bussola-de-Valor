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
        with duckdb.connect(str(db_path), read_only=True) as conn:
            result = conn.execute("SHOW TABLES").fetchall()
        return [row[0] for row in result]
    except Exception as exc:
        st.error(f"Erro ao listar tabelas: {exc}")
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
        with duckdb.connect(str(db_path), read_only=True) as conn:
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
        with duckdb.connect(str(db_path), read_only=True) as conn:
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


def load_custom_css() -> None:
    """Carrega o CSS customizado da Bússola de Valor."""
    css_path = Path(__file__).parent.parent.parent / "app" / "styles" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main() -> None:
    """Ponto de entrada do app Streamlit: exibe um DataFrame do DuckDB e permite executar SQL."""
    st.set_page_config(
        page_title="DW Explorer - Bússola de Valor",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Carrega CSS customizado
    load_custom_css()
    
    # Cabeçalho
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0 2rem 0;'>
            <h1 style='color: #36b37e; margin-bottom: 0.5rem;'>🧭 DW Explorer</h1>
            <p style='color: #9CA3AF; font-size: 1.1rem;'>Explorador de Data Warehouse - Bússola de Valor</p>
        </div>
    """, unsafe_allow_html=True)

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

    # --- Sidebar: Configurações ---
    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        
        selected_table = st.selectbox(
            "📊 Selecione a tabela",
            tables,
            help="Escolha uma tabela para visualizar seus dados"
        )
        
        max_rows = st.number_input(
            "📏 Linhas máximas",
            min_value=10,
            max_value=10000,
            value=500,
            step=10,
            help="Número máximo de linhas a exibir na prévia"
        )
        
        st.markdown("---")
        st.markdown(f"**📁 Banco:** `{db_path.name}`")
        st.markdown(f"**📋 Tabelas:** {len(tables)}")

    # --- Seção 1: Preview da Tabela ---
    st.markdown("### 📋 Preview da Tabela")
    
    df = load_table(db_path, selected_table)
    if df.empty:
        st.info("Tabela vazia ou erro ao carregar.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Tabela", selected_table)
        with col2:
            st.metric("📏 Linhas", f"{df.shape[0]:,}")
        with col3:
            st.metric("📐 Colunas", df.shape[1])
        
        st.dataframe(
            df.head(int(max_rows)),
            use_container_width=True,
            height=400
        )

    # --- Seção 2: Executor SQL ---
    st.markdown("---")
    st.markdown("### 💻 Executor SQL")
    st.caption("Execute consultas SQL personalizadas no Data Warehouse")

    # Layout: SQL à esquerda, Resultado à direita
    col_sql, col_result = st.columns([1, 1])

    with col_sql:
        st.markdown("#### 📝 Query SQL")
        
        # Botão para gerar SELECT padrão
        if st.button("🔄 Gerar SELECT para tabela selecionada", use_container_width=True):
            set_sql_for_table(selected_table, int(max_rows))
            st.rerun()

        sql_input = st.text_area(
            "Digite sua consulta SQL:",
            value=st.session_state["sql"],
            height=300,
            placeholder='Ex: SELECT * FROM "indicadores" WHERE ticker LIKE \'%PETR%\' LIMIT 100',
            key="sql_text_area",
            help="Escreva uma query SQL válida para o DuckDB"
        )
        
        # Atualiza session_state com o conteúdo do text_area
        st.session_state["sql"] = sql_input

        execute_button = st.button("▶️ Executar SQL", type="primary", use_container_width=True)

    with col_result:
        st.markdown("#### 📊 Resultado")
        
        if execute_button:
            sql_to_run = st.session_state.get("sql", "").strip()
            if not sql_to_run:
                st.error("❌ SQL vazio — escreva uma consulta antes de executar.")
            else:
                try:
                    with st.spinner("⏳ Executando consulta..."):
                        start = time.time()
                        result_df = execute_sql(db_path, sql_to_run)
                        elapsed = time.time() - start
                    
                    st.success(f"✅ Consulta executada em {elapsed:.2f}s")
                    
                    # Métricas do resultado
                    res_col1, res_col2 = st.columns(2)
                    with res_col1:
                        st.metric("📏 Linhas retornadas", f"{result_df.shape[0]:,}")
                    with res_col2:
                        st.metric("📐 Colunas", result_df.shape[1])
                    
                    # Exibe o resultado
                    st.dataframe(
                        result_df,
                        use_container_width=True,
                        height=400
                    )
                    
                    # Botão de download
                    csv = result_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Baixar resultado (CSV)",
                        csv,
                        file_name=f"consulta_{int(time.time())}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                except Exception as exc:
                    st.error(f"❌ {str(exc)}")
        else:
            st.info("👈 Digite uma consulta SQL e clique em 'Executar SQL' para ver os resultados aqui.")

    # --- Footer ---
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #9CA3AF; padding: 1rem 0;'>
            <p>🧭 <strong>Bússola de Valor</strong> | Data Warehouse Explorer</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()