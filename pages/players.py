import math
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


def layout(player_id=None, role=None, **other_unknown_query_strings):
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

    if player["stats." + role + ".overall"].iloc[0] is None:
        overall = 0
    else:
        overall = player["stats." + role + ".overall"].iloc[0]

    overall_stats = [player["stats." + role + ".atk_overall"].iloc[0],
                     player["stats." + role + ".dribble_overall"].iloc[0],
                     player["stats." + role + ".pass_overall"].iloc[0],
                     player["stats." + role + ".mental_overall"].iloc[0],
                     player["stats." + role + ".def_overall"].iloc[0]]


    position_buttons = []
    for pos in ast.literal_eval(player["roles"].iloc[0]):
        if pos == role:
            position_buttons.append(html.A([html.Button(pos, className="btn btn-primary")],
                                           href="/players?player_id=" + player_id + "&role=" + pos))
        else:
            position_buttons.append(html.A([html.Button(pos, className="btn btn-secondary")],
                                           href="/players?player_id=" + player_id + "&role=" + pos))

    if not math.isnan(player["height"].iloc[0]) and not math.isnan(player["weight"].iloc[0]):
        player_physique = str(int(player["height"].iloc[0])) + ' cm | ' + str(int(player["weight"].iloc[0])) + " kg"
    elif not math.isnan(player["height"].iloc[0]):
        player_physique = str(int(player["height"].iloc[0])) + ' cm'
    elif not math.isnan(player["weight"].iloc[0]):
        player_physique = str(int(player["weight"].iloc[0])) + " kg"
    else:
        player_physique = ""

    overall_pie = go.Figure(data=[go.Pie(labels=["progress", "rest"], values=[overall, 100 - overall], hole=0.85,
                                         marker=dict(colors=['#6265F0', '#D7DEE5']), direction='clockwise',
                                         sort=False)])
    overall_pie.update(layout_showlegend=False)
    overall_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=75, width=75)
    overall_pie.update_traces(textinfo='none', hoverinfo='skip', hovertemplate=None)

    overall_radar = go.Figure(data=go.Scatterpolar(
        r=overall_stats,
        theta=['ATK', 'DRI', 'PAS', 'MTL', 'DEF'],
        fill='toself'
    ))
    overall_radar.update(layout_showlegend=False)
    overall_radar.update_layout(margin=dict(t=10, b=10, l=30, r=30), height=200, width=200, polar=dict(
        radialaxis=dict(
            visible=False,
            range=[0, 99]
        )))

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

    try:
        if os.path.exists(TEAM_IMG_FOLDER + "/" + player["club_id"].iloc[0] + ".png"):
            team_img = TEAM_IMG_FOLDER + "/" + player["club_id"].iloc[0] + ".png"
        else:
            team_img = DEFAULT_TEAM_IMG
    except:
        team_img = DEFAULT_TEAM_IMG

    player_page = html.Div([
        html.Div([
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
                            player_physique,
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
                        dash.html.H2(overall, style={"position": "absolute", "left": "50%", "top": "50%",
                                                     "transform": "translate(-50%,-50%)"})
                    ], style={"position": "relative"}),
                    html.Div(position_buttons, style={"margin-left": "30px", "display": "flex", "gap": "10px"})
                ], className="dash_block"),

            ], style={"padding": "20px 0px", "display": "flex", "gap": "20px", "flex": "0 1 auto" , "width":"min-content"}),
            html.Div([
                html.Div([
                    dash.html.Div([
                        dcc.Graph(figure=overall_radar, config={
                            "displaylogo": False,
                            'displayModeBar': False,
                        })

                    ], className="dash_block"),
                    html.Div([
                        html.H3("Similar players :"),
                        build_similar_player_list(player)
                    ], className="dash_block", style={"display":"flex","flex-direction":"column","align-items":"flex-start","margin":"20px 0px 0px 0px","width":"100%", "flex": "1 1 auto", "overflow-y":"hidden"}),
                ], style={"display":"flex","flex-direction":"column", "flex": "0 1 auto"}),
                html.Div([

                ], className="dash_block", style={"flex": "1 1 auto"})

            ], style={ "display": "flex", "gap": "20px", "flex": "1 1 auto"}),
        ], style={"display":"flex", "flex-direction":"column", "width":"min-content", "height":"100%"}),
        html.Div([
            html.Div([

            ], className="dash_block", style={"height":"100%", "width":"100%"})
        ], style={"flex": "1 1 auto", "padding":"20px 0px 0px 20px"})

    ], style={"flex": "1 1 auto","display":"flex"})

    layout = html.Div(children=[
        html.Div([dash.html.H2(children='Players')], style={"flex": "0 1 auto"}, className="heading"),
        html.Div([
            dbc.Input(id="input", placeholder="Search a player ...", type="text", style={"flex": "0 1 auto"}),
            dbc.Collapse(
                [dbc.ListGroup(id="search_result",
                               style={"margin-top": "20px", "flex": "0 1 auto","max-height": "300px", "overflow-y": "scroll"})],
                id="collapse",
                is_open=False,
            ),
            player_page

        ], style={"padding": "20px", "flex": "1 1 auto", "display":"flex", "flex-direction":"column"}),

    ], style={"height":"calc(100vh - 4rem)", "display":"flex", "flex-direction":"column"})
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

def build_similar_player_list(player):

    similar_players = app.df_best_role[app.df_all_role['id'].isin(ast.literal_eval(player["similar_players"].iloc[0]))]
    similar_players = similar_players.reset_index(drop=True)
    similar_player_img = []

    for index, row in similar_players.iterrows():
        if os.path.exists(PLAYER_IMG_FOLDER + "/" + row["id"] + ".jpg"):
            similar_player_img.append(PLAYER_IMG_FOLDER + "/" + row["id"] + ".jpg")
        else:
            similar_player_img.append(DEFAULT_PLAYER_IMG)


    result = html.Div([
        html.A([
            html.Img(src=similar_player_img[index], height="30px", style={"margin-right": "10px"}),
            dash.html.Div([
                dash.html.Img(src=FLAG_URL + row["flag_name"] + ".svg", width="14x",
                              style={"border-radius": "1px"})
            ], style={"padding": "5px", "border-radius": "2px", "background-color": "#D7DEE5",
                      "display": "flex", "margin-right":"10px"}),
            html.Span(row["name"], style={"max-width": "120px", "display":"block", "color":"#111827", "text-overflow": "ellipsis", "overflow": "hidden", "white-space": "nowrap"}),
        ], style={"display":"flex", "align-items":"center", "margin":"10px 0px"}, href="/players?player_id=" + row["id"])
        for index, row in similar_players.iterrows()

    ], style={"position":"absolute"})
    return result