import dash
from dash import html, dcc

dash.register_page(__name__)

layout = html.Div(children=[
    html.Div([dash.html.H2(children='Scrapping')], style={}, className="heading"),

])