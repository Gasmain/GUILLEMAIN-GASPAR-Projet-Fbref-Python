import json
import os

import pandas as pd
import numpy as np
import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Output, Input
from flask.helpers import get_root_path

PLAYER_FILE_JSON = "data/player.json"
PLAYER_FILE_CSV = "data/player.csv"
PLAYER_FILE_CSV2 = "data/player2.csv"
MY_LOGO = "assets/football.png"

# TODO : Shoot, Pass, deffense, dribble


"""
Creates a plotly dashboard
"""


def create():
    # df_role contains stats of player according to their position and df_best_pos its stats for its best position
    df_role, df_best_pos = build_data_frame()

    app = dash.Dash(
        __name__,
        use_pages=True,
        external_stylesheets=[dbc.icons.FONT_AWESOME, "https://rsms.me/inter/inter.css"]
        # Loads icons css and Inter font
    )



    navbar = create_nav_bar()
    content = dash.html.Div([dash.page_container], id="pages-content")
    app.layout = dash.html.Div([dash.dcc.Location(id="url"), navbar, content])

    app.run_server(debug=False, port=3005)


def build_data_frame():
    f = open(PLAYER_FILE_JSON)
    data = json.load(f)
    df_role = pd.json_normalize(data)
    for player in data:
        best_pos_stats = player["stats"][list(player["stats"].keys())[0]]
        player.pop('stats', None)
        player["stats"] = best_pos_stats
    df_best_pos = pd.json_normalize(data)
    return df_role, df_best_pos


def create_nav_bar():
    navbar = dbc.NavbarSimple(
        children=[
            dash.html.A(
                # Use row and col to control vertical alignment of logo / brand
                [dash.html.Img(src=MY_LOGO, height="40px")],
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavLink([dash.html.I(className="fa-solid fa-house", style={"margin-right": "10px"}), "Dashboard"],
                        href="/", active="exact"),
            dbc.NavLink([dash.html.I(className="fa-solid fa-user", style={"margin-right": "10px"}), "Players"],
                        href="/players", active="exact"),
            dbc.NavLink([dash.html.I(className="fa-solid fa-circle-down", style={"margin-right": "10px"}), "Scrapping"],
                        href="/scrapping", active="exact")
        ],
        color="dark",
        dark=True
    )

    return navbar
