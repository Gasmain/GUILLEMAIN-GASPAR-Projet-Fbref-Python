import json

import pandas as pd
import numpy as np
from dash import Dash, html, dcc
import plotly.express as px

PLAYER_FILE_JSON = "data/player.json"
PLAYER_FILE_CSV = "data/player.csv"


#Shoot, Pass, deffense, dribble


"""
Creates a plotly dashboard
"""

def create():
    app = Dash(__name__)
    df = build_data_frame()

    colors = {
        'background': '#111111',
        'text': '#7FDBFF'
    }

    df = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })
    fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )

    app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H1(
            children='Hello Dash',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.Div(children='Dash: A web application framework for your data.', style={
            'textAlign': 'center',
            'color': colors['text']
        }),

        dcc.Graph(
            id='example-graph-2',
            figure=fig
        )
    ])

    app.run_server(debug=True)


def build_data_frame():
    f = open(PLAYER_FILE_JSON)
    data = json.load(f)
    df = pd.json_normalize(data)
    return df

