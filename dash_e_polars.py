import polars as pl
import pandas as pd
from dash import Dash, html, dash_table
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

# Dados com Polars
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
    "Perfil da Ação": ["Micro Cap", "Small Cap", "Blue Chip", "Mid Cap", "Micro Cap"]
}

df_polars = pl.DataFrame(data)
df_pandas = df_polars.to_pandas()

# Estilo azul para tabelas
style_cell = {
    "backgroundColor": "#E6F0FA",
    "color": "#00008B",
    "border": "1px solid #1E90FF",
    "padding": "10px",
    "fontFamily": "Arial",
    "fontSize": "14px"
}
style_header = {
    "backgroundColor": "#ADD8E6",
    "color": "#00008B",
    "fontWeight": "bold",
    "border": "2px solid #1E90FF"
}

# App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("🔵 Modelo 1: dash_table.DataTable", style={"color": "#1E90FF"}),
    dash_table.DataTable(
        data=df_pandas.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df_pandas.columns],
        style_cell=style_cell,
        style_header=style_header,
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#F0F8FF"},
            {"if": {"state": "active"}, "backgroundColor": "#87CEEB"}
        ],
        page_size=5,
        sort_action="native"
    ),

    html.H2("🔵 Modelo 2: dash_ag_grid.AgGrid", style={"color": "#1E90FF", "marginTop": "40px"}),
    dag.AgGrid(
        rowData=df_pandas.to_dict("records"),
        columnDefs=[{"field": col} for col in df_pandas.columns],
        defaultColDef={"sortable": True, "filter": True, "resizable": True},
        dashGridOptions={"rowSelection": "single"},
        style={"height": "300px", "width": "100%", "marginBottom": "20px"},
        className="ag-theme-alpine"
    ),

    html.H2("🔵 Modelo 3: Tabela HTML personalizada", style={"color": "#1E90FF", "marginTop": "40px"}),
    html.Table([
        html.Thead(html.Tr([html.Th(col, style=style_header) for col in df_pandas.columns])),
        html.Tbody([
            html.Tr([
                html.Td(str(df_pandas.iloc[i][col]), style=style_cell)
                for col in df_pandas.columns
            ]) for i in range(len(df_pandas))
        ])
    ], style={"width": "100%", "borderCollapse": "collapse"}),

    html.H2("🔵 Modelo 4: Tabela com linhas destacadas", style={"color": "#1E90FF", "marginTop": "40px"}),
    dash_table.DataTable(
        data=df_pandas.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df_pandas.columns],
        style_cell=style_cell,
        style_header=style_header,
        style_data_conditional=[
            {
                "if": {"filter_query": "{Perfil da Ação} = 'Blue Chip'"},
                "backgroundColor": "#B0E0E6",
                "color": "#00008B",
                "fontWeight": "bold"
            }
        ],
        page_size=5
    ),

    html.H2("🔵 Modelo 5: Tabela com edição inline", style={"color": "#1E90FF", "marginTop": "40px"}),
    dash_table.DataTable(
        data=df_pandas.to_dict("records"),
        columns=[{"name": i, "id": i, "editable": True} for i in df_pandas.columns],
        editable=True,
        style_cell=style_cell,
        style_header=style_header,
        page_size=5
    )
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True)
