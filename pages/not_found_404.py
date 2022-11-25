import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__)

layout = html.Div(children=[
    dbc.Alert(
                [
                    html.I(className="bi bi-x-octagon-fill me-2"),
                    "404 Error : Page was not found",
                ],
                color="danger",
                className="d-flex align-items-center",
            )
])
