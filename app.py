import os
import dash
from dash import dcc, html

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "FAST Conflict Forecasts"
server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id="page-content")
    ],
    style={"maxWidth": "1400px", "margin": "0 auto"}
)

import callbacks

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="127.0.0.1", port=port, debug=True)