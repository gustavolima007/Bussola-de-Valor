from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# Dados fictícios
df = px.data.stocks()

# Inicializar o app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Dashboard de Ações"),
    dcc.Dropdown(
        id="dropdown",
        options=[{"label": col, "value": col} for col in df.columns if col != "date"],
        value="GOOG"
    ),
    dcc.Graph(id="graph")
])

# Callback
@app.callback(
    Output("graph", "figure"),
    Input("dropdown", "value")
)
def update_graph(stock):
    fig = px.line(df, x="date", y=stock, title=f"Ação: {stock}")
    return fig

# Rodar o servidor
if __name__ == "__main__":
    app.run(debug=True)
