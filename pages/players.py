import os
from datetime import date
import ast
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from datetime import datetime
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

import app

PLAYER_IMG_FOLDER = "assets/playerimg"
TEAM_IMG_FOLDER = "assets/teamimg"
DEFAULT_PLAYER_IMG = "/assets/default.jpg"
DEFAULT_TEAM_IMG = "/assets/default_team.png"

FLAG_URL = "https://cdn.ssref.net/req/1637611918233-20211022/flags/"
dash.register_page(__name__)


def layout(player_id=None,role=None, **other_unknown_query_strings):
    player_page = ""
    if player_id is None:
        player = app.df_all_role.sample()
        player_id = player["id"].iloc[0]
    else:
        player = app.df_all_role[app.df_all_role['id'] == player_id]

    if role is None:
        role = ast.literal_eval(player["roles"].iloc[0])[0]
    else:
        if role not in ast.literal_eval(player["roles"].iloc[0]):
            role = ast.literal_eval(player["roles"].iloc[0])[0]

    if player["stats."+role+".overall"].iloc[0] is None:
        overall = 0
    else:
        overall = player["stats."+role+".overall"].iloc[0]

    position_buttons = []
    for pos in ast.literal_eval(player["roles"].iloc[0]):
        if pos == role:
            position_buttons.append(html.A([html.Button(pos, className="btn btn-primary")],href="/players?player_id="+player_id+"&role="+pos))
        else:
            position_buttons.append(html.A([html.Button(pos, className="btn btn-secondary")],href="/players?player_id="+player_id+"&role="+pos))



    overall_pie = go.Figure(data=[go.Pie(labels=["progress", "rest"], values=[overall, 100-overall], hole=0.85,marker=dict(colors=['#6265F0', '#D7DEE5']), direction ='clockwise', sort=False)])
    overall_pie.update(layout_showlegend=False)
    overall_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=75,width=75)
    overall_pie.update_traces(textinfo='none', hoverinfo='skip', hovertemplate=None)

    if " " in player["name"].iloc[0]:
        player_name = dash.html.H2(
            [player["name"].iloc[0].split(' ', 1)[0], html.Br(), player["name"].iloc[0].split(' ', 1)[1]],
            style={"max-width": "200px", "margin-left": "30px"})
    else:
        player_name = dash.html.H2(
            [player["name"].iloc[0]],
            style={"max-width": "200px", "margin-left": "30px"})

    if os.path.exists(PLAYER_IMG_FOLDER + "/" + player_id + ".jpg"):
        player_img = PLAYER_IMG_FOLDER + "/" + player_id + ".jpg"
    else:
        player_img = DEFAULT_PLAYER_IMG

    if os.path.exists(TEAM_IMG_FOLDER + "/" + player["club_id"].iloc[0] + ".png"):
        team_img = TEAM_IMG_FOLDER + "/" + player["club_id"].iloc[0] + ".png"
    else:
        team_img = DEFAULT_TEAM_IMG

    player_page = html.Div([
        html.Div([
            html.Div([
                dash.html.Img(src=player_img, height="70px", style={"margin-right": "30px"}),
                dash.html.Div([
                    dash.html.Div([
                        dash.html.Div([
                            dash.html.Img(src=FLAG_URL + player["flag_name"].iloc[0] + ".svg", width="26x",
                                          style={"border-radius": "3px"})
                        ], style={"padding": "5px", "border-radius": "4px", "background-color": "#D7DEE5",
                                  "display": "flex"}),
                        dash.html.Span(player["nationality"].iloc[0], className="light_text")

                    ], style={"display": "flex", "align-items": "center", "gap": "10px"}),
                    dash.html.H3(calculate_age(str(player["birth_date"].iloc[0])) + " ans", className="light_text",
                                 style={"margin-top": "5px", "display": "inline-block"}),
                    dash.html.Span("(" + player["birth_date"].iloc[0] + ")", className="light_text",
                                   style={"margin-left": "3px"}),
                    dash.html.Span(
                        str(int(player["height"].iloc[0])) + ' cm | ' + str(int(player["weight"].iloc[0])) + " kg",
                        className="light_text",
                        style={"display": "block"})
                ]),
                player_name,
                dash.html.Div(className="separator"),
                dash.html.Img(src=team_img, height="60px", style={"margin-right": "10px"})

            ], className="dash_block"),
            dash.html.Div([
                dash.html.Div([
                    dcc.Graph(figure=overall_pie, config={
                        "displaylogo": False,
                        'displayModeBar': False,
                    }),
                    dash.html.H2(overall, style={"position":"absolute", "left":"50%", "top":"50%", "transform":"translate(-50%,-50%)"})
                ], style={"position":"relative"}),
                html.Div(position_buttons, style={"margin-left":"30px", "display":"flex", "gap":"10px"})
            ], className="dash_block")
        ], style={"width": "100%", "padding": "30px 0px","display":"flex", "gap": "20px"}),

    ])

    layout = html.Div(children=[
        html.Div([dash.html.H2(children='Players')], style={}, className="heading"),
        html.Div([
            dbc.Input(id="input", placeholder="Search a player ...", type="text"),
            dbc.Collapse(
                [dbc.ListGroup(id="search_result",
                               style={"margin-top": "20px", "max-height": "300px", "overflow-y": "scroll"})],
                id="collapse",
                is_open=False,
            ),
            player_page

        ], style={"padding": "30px"}),

    ])
    return layout


@callback(
    Output("collapse", "is_open"),
    [Input("input", "value")]
)
def toggle_collapse(val):
    if val == "" or val is None:
        return False
    return True


@callback(
    Output("search_result", "children"),
    [Input("input", "value")]
)
def fill_search_result(val):
    if val == "" or val is None:
        return None

    result = app.df_best_role[app.df_best_role['name'].str.contains(val + "|" + val.capitalize())]

    result_hml = [dbc.ListGroupItem([html.A(row["name"], href="/players?player_id=" + row["id"],
                                            className="link_list_group",
                                            style={"text-decoration": "none", "color": "#111827"})])
                  for index, row in result.iterrows()]
    return result_hml


def calculate_age(born):
    birth = datetime.strptime(born, '%Y-%m-%d')
    today = date.today()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return str(age)
