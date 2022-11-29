import dash
from dash import html, dcc, Output, Input, callback

from database import Database

dash.register_page(__name__, path='/')
db = Database()


layout = html.Div(children=[
    html.Div([dash.html.H2(children='Dashboard')], style={}, className="heading", id="graph"),
])
