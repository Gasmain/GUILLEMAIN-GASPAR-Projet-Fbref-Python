import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__)

layout = html.Div(children=[
    dbc.Alert(
                [
                    html.I(className="fa-solid fa-triangle-exclamation", style={"margin-right" : "10px"}),
                    "404 Error : Page was not found",
                ],
                color="danger",
                style= {"margin":"20px", "max-width" : "700px"}
            )
])
