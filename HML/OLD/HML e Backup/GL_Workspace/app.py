# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta

# ---------------------------
# Config da página
# ---------------------------
st.set_page_config(
    page_title="Tabela 5x5 caprichada",
    page_icon="📊",
    layout="wide",
)

# Verifica se matplotlib está instalado (para usar background_gradient se disponível)
try:
    import matplotlib  # noqa: F401
    HAS_MPL = True
except Exception:
    HAS_MPL = False

# ---------------------------
# Dados iniciais FIXOS (5x5)
# ---------------------------
linhas = [f"L{i}" for i in range(1, 6)]
hoje = date.today()

# Progresso fixo solicitado: 1%, 2%, 6%, 70%, 50%
progresso_fixos = [1.0, 2.0, 6.0, 70.0, 50.0]  # em %

# Você pode ajustar os demais valores se quiser; aqui estou usando exemplos estáveis
initial_df = pd.DataFrame(
    {
        "Métrica": [f"M{i}" for i in range(1, 6)],
        "Valor": [4370.86, 9556.43, 7587.95, 6387.93, 2404.17],
        "Variação %": [-0.1220, -0.1709, 0.2330, 0.1006, 0.1540],  # -12,20%, -17,09%, ...
        "Progresso": progresso_fixos,  # <<< FIXO
        "Atualizado em": [
            hoje - timedelta(days=4),
            hoje,
            hoje - timedelta(days=9),
            hoje - timedelta(days=5),
            hoje - timedelta(days=8),
        ],
    },
    index=linhas,
)

# Persistimos o DF limpo na sessão (para Editor e CSV)
if "data" not in st.session_state:
    st.session_state.data = initial_df.copy()

# ---------------------------
# Barra lateral (opções)
# ---------------------------
st.sidebar.header("Opções da Tabela")
modo = st.sidebar.radio(
    "Modo de exibição",
    [
        "DataFrame (com column_config)",
        "DataFrame + Styler (com barra vermelha/verde)",
        "Editor (opcional)",
    ],
    index=0,
)
altura = st.sidebar.slider("Altura da grade (px)", 200, 700, 380, 20)
mostrar_index = st.sidebar.toggle("Mostrar índice (L1…L5)", value=False)
tooltips_on = st.sidebar.toggle("Ativar tooltips (Styler)", value=True, help="Se desativar, evita a injeção de <span class='pd-t'>.")

# ---------------------------
# CSS leve para polir a aparência
# ---------------------------
st.markdown(
    """
    <style>
    .stDataFrame, .stDataEditor {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(49, 51, 63, 0.35);
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }
    .block-container { padding-top: 1.1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Tabela 5×5 no tema escuro")
st.caption("Inclui: formatos, gradientes e **barra condicional** em Progresso (vermelha ≤ 3%, verde > 3%) no modo Styler.")

# ---------------------------
# Formatação & estilos auxiliares
# ---------------------------
def fmt_percent(x):
    if pd.isna(x):
        return ""
    return f"{x:.1%}"

def fmt_money(x):
    if pd.isna(x):
        return ""
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Gradiente manual para "Valor" (dispensa matplotlib)
def manual_gradient_for_valor(col: pd.Series):
    vmin, vmax = float(col.min()), float(col.max())
    rng = vmax - vmin if vmax != vmin else 1.0
    styles = []
    for v in col:
        t = (float(v) - vmin) / rng
        g = int(90 + t * 165)   # 90..255 (verde)
        a = 0.18 + 0.32 * t     # alpha 0.18..0.50
        styles.append(f"background-color: rgba(0, {g}, 0, {a});")
    return styles

# Barra condicional em "Progresso" (vermelho <= 3, verde > 3) — proporcional ao valor
def style_progress_bar(series: pd.Series):
    out = []
    for v in series:
        if pd.isna(v):
            out.append("")
            continue
        width = max(0.0, min(100.0, float(v)))  # clamp 0..100
        color = "255, 0, 0" if v <= 3 else "0, 170, 0"
        style = (
            f"background: linear-gradient(90deg, rgba({color},0.75) {width}%, rgba(0,0,0,0) {width}%);"
            "border: 1px solid rgba(255,255,255,0.08);"
            "border-radius: 6px;"
            "padding: 2px 6px;"
            "color: #ffffff;"
            "text-align: center;"
            "white-space: nowrap;"
        )
        out.append(style)
    return out

# ---------------------------
# Qual DF está “em uso” agora?
# ---------------------------
df_in_use = st.session_state.data.copy()

# ---------------------------
# Download sempre usa o DF limpo da sessão (sem HTML)
# ---------------------------
csv_df = df_in_use.copy()
csv_df["Variação %"] = (csv_df["Variação %"] * 100).round(2)  # em %
st.download_button(
    "⤓ Baixar CSV (limpo)",
    data=csv_df.to_csv(index=mostrar_index, sep=";", decimal=",").encode("utf-8"),
    file_name="tabela_5x5.csv",
    mime="text/csv",
)
st.divider()

# ---------------------------
# Modo 1: st.dataframe com column_config
# ---------------------------
if modo == "DataFrame (com column_config)":
    st.subheader("DataFrame com `column_config`")
    st.caption("Aqui o Progresso mostra seus valores fixos: 1%, 2%, 6%, 70%, 50% (barra padrão do Streamlit).")
    st.dataframe(
        df_in_use,
        use_container_width=True,
        height=altura,
        hide_index=not mostrar_index,
        column_config={
            "Métrica": st.column_config.TextColumn("Métrica", help="Nome curto da métrica.", width="small"),
            "Valor": st.column_config.NumberColumn("Valor", help="Valor monetário.", format="R$ %0.2f", step=0.01),
            "Variação %": st.column_config.NumberColumn("Variação %", help="Percentual.", format="%0.1f%%", width="medium"),
            "Progresso": st.column_config.ProgressColumn("Progresso", help="0–100.", min_value=0, max_value=100),
            "Atualizado em": st.column_config.DateColumn("Atualizado em", help="Última atualização.", format="DD/MM/YYYY", width="medium"),
        },
    )

# ---------------------------
# Modo 2: DataFrame + Styler (com barra condicional)
# ---------------------------
elif modo == "DataFrame + Styler (com barra vermelha/verde)":
    st.subheader("DataFrame com estilos (`pandas.Styler`)")
    st.caption("Progresso: **vermelho** se ≤ 3% e **verde** se > 3% (barra proporcional via CSS).")

    sdf = df_in_use.copy()
    styler = (
        sdf.style
        .format(subset=["Valor"], formatter=fmt_money)
        .format(subset=["Variação %"], formatter=fmt_percent)
        .format(subset=["Progresso"], formatter=lambda x: f"{x:.1f}%")
        .format(subset=["Atualizado em"], formatter=lambda d: d.strftime("%d/%m/%Y"))
        .set_table_styles(
            [
                {"selector": "th", "props": "position: sticky; top: 0; background: rgba(30,30,30,0.95);"},
                {"selector": "thead th.col_heading", "props": "font-weight: 600;"},
                {"selector": "tbody td", "props": "border-top: 1px solid rgba(255,255,255,0.07);"},
            ]
        )
    )

    # Gradiente em "Valor": usa pandas se houver matplotlib; senão, fallback manual
    if HAS_MPL:
        styler = styler.background_gradient(subset=["Valor"], cmap="Greens")
    else:
        styler = styler.apply(manual_gradient_for_valor, subset=["Valor"])

    # Barra condicional em "Progresso"
    styler = styler.apply(style_progress_bar, subset=["Progresso"])

    # Barra simétrica em "Variação %"
    styler = styler.bar(subset=["Variação %"], align="mid", vmin=-0.3, vmax=0.3)

    # Tooltips opcionais (se desligar, não injeta <span class="pd-t">)
    if tooltips_on:
        styler = styler.set_tooltips(
            pd.DataFrame(
                {
                    "Métrica": [f"Clique para ver detalhes de {m}" for m in sdf["Métrica"]],
                    "Valor": [f"Valor atual: {fmt_money(v)}" for v in sdf["Valor"]],
                    "Variação %": [f"Tendência: {fmt_percent(p)}" for p in sdf["Variação %"]],
                    "Progresso": [f"{p:.1f}% concluído" for p in sdf["Progresso"]],
                    "Atualizado em": [f"Atualizado em {d.strftime('%d/%m/%Y')}" for d in sdf["Atualizado em"]],
                },
                index=sdf.index,
            )
        )

    if not mostrar_index:
        styler = styler.hide(axis="index")

    st.dataframe(styler, use_container_width=True, height=altura)

# ---------------------------
# Modo 3: Editor (opcional)
# ---------------------------
else:
    st.subheader("Editor (opcional)")
    st.caption("Edite células; suas alterações ficam salvas em `session_state` e também no CSV.")

    edited = st.data_editor(
        df_in_use,
        use_container_width=True,
        height=altura,
        hide_index=not mostrar_index,
        num_rows="fixed",
        column_config={
            "Métrica": st.column_config.TextColumn("Métrica", help="Nome curto da métrica.", width="small"),
            "Valor": st.column_config.NumberColumn("Valor", help="Valor monetário.", format="R$ %0.2f", step=0.01),
            "Variação %": st.column_config.NumberColumn("Variação %", help="Percentual.", format="%0.1f%%", step=0.1),
            "Progresso": st.column_config.NumberColumn("Progresso", help="0–100", min_value=0, max_value=100, step=1),
            "Atualizado em": st.column_config.DateColumn("Atualizado em", help="Selecione a data.", format="DD/MM/YYYY"),
        },
        key="editor",
    )

    # Atualiza o DF limpo da sessão (para persistir e para o CSV)
    st.session_state.data = edited.copy()

st.divider()
st.caption(
    "Na aba **column_config**, Progresso usa a barra padrão do Streamlit com seus valores fixos. "
    "No modo **Styler**, a barra é colorida: vermelho (≤ 3%) e verde (> 3%). "
    "O download sempre sai limpo (sem HTML)."
)
