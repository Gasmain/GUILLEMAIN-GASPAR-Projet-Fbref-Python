import json

import pandas as pd
import numpy as np
import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Output, Input
from flask.helpers import get_root_path

PLAYER_FILE_JSON = "data/player.json"
PLAYER_FILE_CSV = "data/player.csv"
MY_LOGO = "assets/logo.png"


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


    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavLink([dash.html.I(className="bi bi-house-door-fill", style={"margin-right": "10px"}), "Dashboard"],
                        href="/", active="exact"),
            dbc.NavLink([dash.html.I(className="bi bi-person-fill", style={"margin-right": "10px"}), "Players"],
                        href="/players", active="exact"),
            dbc.NavLink([dash.html.I(className="bi bi-cloud-arrow-down-fill", style={"margin-right": "10px"}), "Scrapping"],
                        href="/scrapping", active="exact")
        ],
        color="dark",
        dark=True,
        brand="Dash",
        brand_href="/",
        brand_style={"color":"#6265F0", "font-weight" : "700", "font-size":"25px"}
    )



    content = dash.html.Div([dash.page_container],id="pages-content")


    app.layout = dash.html.Div([dash.dcc.Location(id="url"), navbar, content])

    app.run_server(debug=False, port=3005)


def build_data_frame():
    f = open(PLAYER_FILE_JSON)
    data = json.load(f)
    df = pd.json_normalize(data)
    return df


