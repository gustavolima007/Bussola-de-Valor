# app/app.py
import streamlit as st
from pathlib import Path

# Importando os módulos refatorados
from data_loader import load_and_merge_data, load_ibov_score
from components.filters import render_sidebar_filters
from components.tabs_layout import render_tabs

def apply_external_css():
    """Carrega e aplica o arquivo de CSS externo."""
    css_path = Path(__file__).resolve().parent / 'styles' / 'styles.css'
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Arquivo styles/styles.css não encontrado.")

def main():
    """
    Função principal que executa a aplicação Streamlit.
    """
    # --- Configuração Inicial da Página ---
    st.set_page_config(
        page_title="Bússola de Valor - Análise de Ações",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Configurar tema escuro para Plotly
    import plotly.io as pio
    pio.templates["dark_custom"] = {
        "layout": {
            "paper_bgcolor": "#1b1f2a",  # Cor de fundo do cartão (secondaryBackgroundColor)
            "plot_bgcolor": "#1b1f2a",   # Cor de fundo do gráfico
            "font": {"color": "#ffffff"}, # Cor do texto (textColor)
            "xaxis": {
                "gridcolor": "#4B5563",
                "zerolinecolor": "#4B5563",
                "linecolor": "#4B5563"
            },
            "yaxis": {
                "gridcolor": "#4B5563",
                "zerolinecolor": "#4B5563",
                "linecolor": "#4B5563"
            },
            # Paleta de cores para combinar com o tema
            "colorway": ["#36b37e", "#D4AF37", "#82A9B1", "#E5E7EB", "#9CA3AF", "#4B5563"],
        }
    }
    pio.templates.default = "dark_custom"
    
    apply_external_css()

    # --- Título e Subtítulo ---
    st.title("🧭 Bússola de Valor")
    st.markdown(
        "Plataforma de análise e ranking de ações baseada nos princípios de **Barsi, Bazin, Buffett, Lynch e Graham**."
    )
    
    # --- Carregamento e Processamento de Dados ---
    data_path = Path(__file__).resolve().parent.parent / 'data'
    df, all_data = load_and_merge_data(data_path)
    ibov_score = load_ibov_score(data_path)

    if df.empty:
        st.warning("O DataFrame principal está vazio. A aplicação não pode continuar.")
        st.stop()

    # --- Renderização da Sidebar e Filtros ---
    # O módulo de filtros cuida de toda a lógica da sidebar
    df_filtrado, ticker_foco = render_sidebar_filters(df, ibov_score)

    # --- Renderização das Abas de Conteúdo ---
    # O módulo de layout de abas cuida da exibição de todo o conteúdo principal
    render_tabs(df, df_filtrado, all_data, ticker_foco)


if __name__ == "__main__":
    main()