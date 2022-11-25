import json

import pandas as pd
import numpy as np
import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from flask.helpers import get_root_path

PLAYER_FILE_JSON = "data/player.json"
PLAYER_FILE_CSV = "data/player.csv"
MY_LOGO = "r'assets/soccer_logo.png"


#TODO : Shoot, Pass, deffense, dribble


"""
Creates a plotly dashboard
"""

def create():
    df = build_data_frame()
    app = dash.Dash(
        __name__,
        use_pages=True,
        external_stylesheets=[dbc.icons.BOOTSTRAP]
    )

    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "25 rem",
        "padding": "2rem 2rem",
    }

    CONTENT_STYLE = {
        "margin-top": "20rem",
        "padding": "2rem 2rem",
    }

    navbar = dbc.NavbarSimple(
        children=[
            dash.html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(dash.html.Img(src=MY_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Navbar", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/"
            ),
            dbc.NavLink([dash.html.I(className="bi bi-house-door-fill", style={"margin-right": "10px"}), "Dashboard"],
                        href="/", active="exact"),
            dbc.NavLink([dash.html.I(className="bi bi-person-fill", style={"margin-right": "10px"}), "Players"],
                        href="/players", active="exact"),
            dbc.NavLink([dash.html.I(className="bi bi-download", style={"margin-right": "10px"}), "Scrapping"],
                        href="/scrapping", active="exact")
        ],
        color="dark",
        dark=True,
    )



    content = dash.html.Div([dash.page_container],id="pages-content", style=CONTENT_STYLE)

    app.layout = dash.html.Div([dash.dcc.Location(id="url"), navbar, content])

    app.run_server(debug=False, port=3005)


def build_data_frame():
    f = open(PLAYER_FILE_JSON)
    data = json.load(f)
    df = pd.json_normalize(data)
    return df

