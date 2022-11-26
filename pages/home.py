import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(children=[

    html.Div([dash.html.H2(children='Dashboard')], style={"width": "100%", "height" : "87px", "background-color":"white"}),

    html.H1(children='This is our Home page'),

    html.Div(children='''
        This is our Home page content.
    '''),

])