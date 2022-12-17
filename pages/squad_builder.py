import dash
from dash import html, dcc

dash.register_page(__name__, path='/squad-builder',)

layout = html.Div(children=[
    html.Div([dash.html.H2(children='Squad Builder')], style={}, className="heading"),

])