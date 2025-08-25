import pandas as pd
import random
from dash import Dash, html, Input, Output
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.express as px
import dash.dcc as dcc

# Dados com Score aleatório
data = {
    "Ticker": ["CEBR3", "UNIP6", "VALE3", "CMIG4", "KEPL3"],
    "Empresa": [
        "Companhia Energética de Brasil - CEB",
        "Unipar Carbocloro S.A.",
        "Vale S.A.",
        "Companhia Energética de Minas Gerais - CEMIG",
        "Kepler Weber S.A."
    ],
    "Setor": [
        "Energia Elétrica e Saneamento",
        "Papel, Química e Outros",
        "Mineração e Siderurgia",
        "Energia Elétrica e Saneamento",
        "Máquinas e Equipamentos Industriais"
    ],
    "Perfil da Ação": ["Micro Cap", "Small Cap", "Blue Chip", "Mid Cap", "Micro Cap"],
    "Score": [random.randint(0, 100) for _ in range(5)]
}

df_pandas = pd.DataFrame(data)

# App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    html.H2("🔵 Modelo 2: dash_ag_grid.AgGrid com Score Visual", style={"color": "#1E90FF", "marginTop": "20px"}),

    dbc.Tabs(
        id="tabs",
        active_tab="tab-geral",
        children=[
            dbc.Tab(label="🏆 Rank Geral", tab_id="tab-geral"),
            dbc.Tab(label="📋 Rank Detalhado", tab_id="tab-detalhado"),
            dbc.Tab(label="🔬 Análise Individual", tab_id="tab-individual"),
            dbc.Tab(label="✨ Insights Visuais", tab_id="tab-insights"),
            dbc.Tab(label="🔍 Análise de Dividendos", tab_id="tab-dividendos"),
            dbc.Tab(label="🏗️ Rank Setores", tab_id="tab-setores"),
            dbc.Tab(label="🧭 Guia da Bússola", tab_id="tab-bussola"),
        ],
        className="mb-4"
    ),

    html.Div(id="tab-content")
], fluid=True)

# Callback para renderizar conteúdo por aba
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    # Tabela com barra de Score
    grid = dag.AgGrid(
        rowData=df_pandas.to_dict("records"),
        columnDefs=[
            {"field": "Ticker"},
            {"field": "Empresa"},
            {"field": "Setor"},
            {"field": "Perfil da Ação"},
            {
                "field": "Score",
                "headerName": "Score (%)",
                "cellRenderer": "function(params) {\
                    const value = params.value;\
                    const barColor = value > 70 ? '#1E90FF' : value > 40 ? '#87CEFA' : '#ADD8E6';\
                    return `<div style='width: 100%; display: flex; align-items: center;'>\
                        <div style='flex: 1; background: #f0f0f0; height: 12px; border-radius: 6px; overflow: hidden;'>\
                            <div style='width: ${value}%; background: ${barColor}; height: 100%;'></div>\
                        </div>\
                        <div style='margin-left: 8px; font-weight: bold;'>${value}%</div>\
                    </div>`;\
                }"
            }
        ],
        defaultColDef={"sortable": True, "filter": True, "resizable": True},
        dashGridOptions={"rowSelection": "single"},
        style={"height": "350px", "width": "100%", "marginBottom": "20px"},
        className="ag-theme-alpine"
    )

    # Gráficos
    bar_fig = px.bar(df_pandas, x="Empresa", y="Score", color="Setor", title="Score por Empresa")
    pie_fig = px.pie(df_pandas, names="Setor", title="Distribuição por Setor")
    scatter_fig = px.scatter(df_pandas, x="Score", y="Empresa", color="Perfil da Ação", size="Score", title="Score vs Empresa")

    # Conteúdo por aba
    if active_tab == "tab-geral":
        return html.Div([grid])
    elif active_tab == "tab-detalhado":
        return html.Div([grid, dcc.Graph(figure=bar_fig)])
    elif active_tab == "tab-individual":
        return html.Div([dcc.Graph(figure=scatter_fig)])
    elif active_tab == "tab-insights":
        return html.Div([dcc.Graph(figure=pie_fig)])
    elif active_tab == "tab-dividendos":
        return html.Div([html.P("🔍 Ainda não há dados de dividendos disponíveis.")])
    elif active_tab == "tab-setores":
        return html.Div([dcc.Graph(figure=bar_fig)])
    elif active_tab == "tab-bussola":
        return html.Div([html.P("🧭 Guia da Bússola em construção...")])
    else:
        return html.Div([grid])

if __name__ == "__main__":
    app.run(debug=True)
