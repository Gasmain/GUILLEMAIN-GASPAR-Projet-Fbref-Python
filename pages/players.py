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
from utils import shared_functions as sf
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

    overall, overall_stats, stats_col = sf.get_overall(player.iloc[0], role)

    position_buttons = []
    for pos in ast.literal_eval(player["roles"].iloc[0]):
        if pos == role:
            position_buttons.append(html.A([html.Button(pos, className="btn btn-primary")],
                                           href="/players?player_id=" + player_id + "&role=" + pos))
        else:
            position_buttons.append(html.A([html.Button(pos, className="btn btn-secondary")],
                                           href="/players?player_id=" + player_id + "&role=" + pos))

    player_physique = sf.get_physique(player)

    overall_pie = sf.build_overall_pie(overall)

    overall_radar = sf.build_overall_radar(overall_stats)




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
                        dash.html.H3(str(sf.calculate_age(str(player["birth_date"].iloc[0]))) + " ans", className="light_text",
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

            ], style={"padding": "20px 0px", "display": "flex", "gap": "20px", "flex": "0 1 auto",
                      "width": "min-content"}),
            html.Div([
                html.Div([
                    dash.html.Div([
                        dcc.Graph(figure=overall_radar, config={
                            "displaylogo": False,
                            'displayModeBar': False,
                        })

                    ], className="dash_block"),
                    html.Div([
                        html.H3("Similar players :", style={"flex": "0 1 auto"}),
                        build_similar_player_list(player)
                    ], className="dash_block",
                        style={"display": "flex", "flex-direction": "column", "align-items": "flex-start",
                               "margin": "20px 0px 0px 0px", "width": "100%", "flex": "1 1 auto"}),
                ], style={"display": "flex", "flex-direction": "column", "flex": "0 1 auto"}),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span(name.replace("stats." + role + ".", "").replace("_percentile", "")),
                                html.Div([
                                    html.Div(
                                        [html.Div(
                                            style={"width": str(int(player[name].iloc[0])) + "%", "height": "100%",
                                                   "background-color": get_color_by_rate(int(player[name].iloc[0]))})],
                                        style={"height": "10px", "background-color": "#D7DEE5", "flex": "1 1 auto"}),
                                    html.Span(str(int(player[name].iloc[0])),
                                              style={"margin-left": "20px", "flex": "0 1 auto", "display": "block",
                                                     "width": "30px", "font-weight":"700", "color":get_color_by_rate(int(player[name].iloc[0]))})
                                ], style={"display": "flex", "width": "100%", "align-items": "center"})
                            ], style={"display": "flex", "align-items": "flex-start", "width": "100%",
                                      "flex-direction": "column", "margin-bottom": "5px"})
                            for name in stats_col
                        ], style={"position": "absolute", "height": "100%", "width": "100%"})
                    ], style={"height": "100%", "width": "100%", "position": "relative"})
                ], className="dash_block", style={"flex": "1 1 auto", "display": "flex", "flex-direction": "column",
                                                  "align-items": "flex-start", "gap": "10px", "overflow-y": "scroll"})

            ], style={"display": "flex", "gap": "20px", "flex": "1 1 auto"}),
        ], style={"display": "flex", "flex-direction": "column", "width": "min-content", "height": "100%"}),
        html.Div([
            html.Div([
                html.Div([])

            ], className="dash_block", style={"height": "100%", "width": "100%"})
        ], style={"flex": "1 1 auto", "padding": "20px 0px 0px 20px"})

    ], style={"flex": "1 1 auto", "display": "flex"})

    layout = html.Div(children=[
        html.Div([dash.html.H2(children='Players')], style={"flex": "0 1 auto"}, className="heading"),
        html.Div([
            dbc.Input(id="input", placeholder="Search a player ...", type="text", style={"flex": "0 1 auto"}),
            dbc.Collapse(
                [dbc.ListGroup(id="search_result",
                               style={"margin-top": "20px", "flex": "0 1 auto", "max-height": "300px",
                                      "overflow-y": "scroll"})],
                id="collapse",
                is_open=False,
            ),
            player_page

        ], style={"padding": "20px", "flex": "1 1 auto", "display": "flex", "flex-direction": "column"}),

    ], style={"height": "calc(100vh - 4rem)", "display": "flex", "flex-direction": "column"})
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





def build_similar_player_list(player):
    similar_players = app.df_best_role[app.df_all_role['id'].isin(ast.literal_eval(player["similar_players"].iloc[0]))]
    similar_players = similar_players.reset_index(drop=True)
    similar_player_img = []

    for index, row in similar_players.iterrows():
        if os.path.exists(PLAYER_IMG_FOLDER + "/" + row["id"] + ".jpg"):
            similar_player_img.append(PLAYER_IMG_FOLDER + "/" + row["id"] + ".jpg")
        else:
            similar_player_img.append(DEFAULT_PLAYER_IMG)

    result = html.Div(html.Div([
        html.A([
            html.Img(src=similar_player_img[index], height="30px", style={"margin-right": "10px"}),
            dash.html.Div([
                dash.html.Img(src=FLAG_URL + row["flag_name"] + ".svg", width="14x",
                              style={"border-radius": "1px"})
            ], style={"padding": "5px", "border-radius": "2px", "background-color": "#D7DEE5",
                      "display": "flex", "margin-right": "10px"}),
            html.Span(row["name"],
                      style={"max-width": "120px", "display": "block", "color": "#111827", "text-overflow": "ellipsis",
                             "overflow": "hidden", "white-space": "nowrap"}),
        ], style={"display": "flex", "align-items": "center", "margin": "10px 0px"},
            href="/players?player_id=" + row["id"])
        for index, row in similar_players.iterrows()

    ], style={"position": "absolute"}),
        style={"flex": "1 1 auto", "position": "relative", "width": "100%", "overflow-y": "scroll"})
    return result


def get_color_by_rate(rate):
    if rate >= 75:
        return "#27AC5F"
    elif rate >= 50:
        return "#B8D640"
    elif rate >= 25:
        return "#F29947"
    else:
        return "#EB5757"
