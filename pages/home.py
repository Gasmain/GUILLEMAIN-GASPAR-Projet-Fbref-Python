import dash
from dash import html, dcc, Output, Input, callback


dash.register_page(__name__, path='/')


layout = html.Div(children=[
    html.Div([dash.html.H2(children='Dashboard')], style={}, className="heading", id="graph"),
])
