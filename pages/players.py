import os
from datetime import date

import dash
from datetime import datetime
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

import app


PLAYER_IMG_FOLDER = "assets/playerimg"
DEFAULT_PLAYER_IMG = "/assets/default.jpg"
FLAG_URL = "https://cdn.ssref.net/req/1637611918233-20211022/flags/"
dash.register_page(__name__)



def layout(player_id=None, **other_unknown_query_strings):
    player_page = ""
    if player_id != None:

        player = app.df_best_role[app.df_best_role['id'] == player_id].iloc[[0]]
        if os.path.exists(PLAYER_IMG_FOLDER+"/"+player_id+".jpg"):
            player_img = PLAYER_IMG_FOLDER+"/"+player_id+".jpg"
        else:
            player_img = DEFAULT_PLAYER_IMG

        player_page = html.Div([
            html.Div([
                html.Div([
                    dash.html.Img(src=player_img, height="70px", style={"margin-right":"20px"}),
                    dash.html.Div([
                        dash.html.Div([
                            dash.html.Div([
                                dash.html.Img(src=FLAG_URL + player["flag_name"] + ".svg", width="26x",
                                              style={"border-radius": "3px"})
                            ], style={"padding": "5px", "border-radius": "4px", "background-color": "#D7DEE5",
                                      "display": "flex"}),
                            dash.html.Span(player["nationality"], className="light_text")

                        ], style={"display": "flex", "align-items": "center", "gap": "10px"}),
                        dash.html.H3(calculate_age(''.join(player["birth_date"]))+" ans", className="light_text", style={"margin-top":"5px", "display":"inline-block"}),
                        dash.html.Span("("+''.join(player["birth_date"])+")", className="light_text", style={"margin-left":"3px"}),
                        dash.html.Span(player["height"]+' | '+player["height"], className="light_text",
                                       style={"display": "block"})

                    ])
                ], className="dash_block")
            ], style={"width" : "100%", "height" : "300px", "padding":"30px 0px"})
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

    result = app.df_best_role[app.df_best_role['name'].str.contains(val+"|"+val.capitalize())]

    result_hml = [dbc.ListGroupItem([html.A(row["name"], href="/players?player_id="+row["id"], className="link_list_group",style={"text-decoration" : "none", "color": "#111827"})])
              for index, row in result.iterrows()]
    return result_hml



def calculate_age(born):
    birth = datetime.strptime(born, '%Y-%m-%d')
    today = date.today()
    age =  today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return str(age)