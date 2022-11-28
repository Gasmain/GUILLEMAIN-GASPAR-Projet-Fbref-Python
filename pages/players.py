import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

import app

dash.register_page(__name__)

layout = html.Div(children=[
    html.Div([dash.html.H2(children='Players')], style={}, className="heading"),
    #dbc.Input(id="input",
          #placeholder="Search for a player ...",
          #type="text"
    #)


])


@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)


@callback(Output("output", "children"), [Input("input", "value")])
def output_text(value):
    return value
