import ast
import json
import math
from sre_parse import State

import numpy as np
from dash.exceptions import PreventUpdate
import plotly.express as px
from utils import simple_functions as sf
import dash
from dash import html, dcc, Output, Input,State, callback, ALL, callback_context
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc

import app

dash.register_page(__name__, path='/squad-builder', )

FLAG_URL = "https://cdn.ssref.net/req/1637611918233-20211022/flags/"
MY_TEAM_PATH = "data/my_team.json"
FORMATION_POSITION = {
    "442": [[40, 145], [100, 105], [100, 185], [150, 240], [150, 50], [230, 185], [230, 105], [320, 50], [320, 240],
            [400, 105], [400, 185]],
    "433": [[40, 145], [100, 105], [100, 185], [150, 240], [150, 50], [280, 145], [220, 205], [220, 95], [320, 50],
            [320, 240],
            [400, 145], ]}

FORMATION_LINK = {
    "442": [["0", "1"], ["0", "2"], ["1", "2"], ["2", "3"], ["4", "1"], ["4", "7"], ["1", "6"], ["6", "7"], ["2", "5"],
            ["8", "3"], ["8", "5"], ["8", "10"], ["5", "6"], ["9", "7"], ["9", "6"], ["9", "10"], ["5", "10"]],
    "433": [["0", "1"], ["0", "2"], ["1", "2"], ["2", "3"], ["4", "1"], ["4", "7"], ["6", "7"], ["8", "10"], ["5", "6"],
            ["5", "7"], ["9", "6"], ["9", "10"], ["5", "10"], ["3", "6"], ["3", "6"], ["1", "7"], ["2", "6"],
            ["7", "8"]]
}

show_links = True
my_team = None
sidebar = ""
to_update_search_result = False
to_replace = None
team_chemistry = 0

style = [
    {
        'selector': '.red-link',
        'style': {
            'line-color': 'rgb(235, 87, 87)'
        }

    },
    {
        'selector': '.green-link',
        'style': {
            'line-color': 'rgb(39, 172, 95)'
        }

    },
    {
        'selector': '.yellow-link',
        'style': {
            'line-color': 'rgb(242, 153, 71)'
        }

    },
    {
        'selector': 'label',
        'style': {
            'content': 'data(label)',
            'color': 'white',
        }
    },
    {
        'selector': 'node',
        'style': {
            "font-size": "10px",
            'text-halign': 'bottom',
            'text-valign': 'bottom',
            'text-margin-y': '5px',
            'background-image': 'data(url)',
            'background-fit': "cover",
            "border-color": "#56657F",
            "border-width": "3",
            "color": "white"
        }
    }

]


def make_my_team_df():
    global my_team
    f = open(MY_TEAM_PATH)
    my_team = json.load(f)
    sorter = list(my_team["players"])
    temp = app.df_all_role[app.df_all_role.id.isin(my_team["players"])]
    team_df = temp.sort_values(by="id", key=lambda column: column.map(lambda e: sorter.index(e)))
    team_df = team_df.reset_index(drop=True)
    if len(team_df) != 11:
        sf.create_random_team()
        team_df = make_my_team_df()
    return team_df


my_team_df = make_my_team_df()


def build_nodes():
    global team_chemistry
    team_chemistry = 0

    elements = []
    for index, row in my_team_df.iterrows():
        elements.append({'data': {'id': str(index), 'label': row["name"],
                                  'url': row["img"], 'data': row["id"]},
                         'position': {'x': FORMATION_POSITION[my_team["formation"]][index][0],
                                      'y': FORMATION_POSITION[my_team["formation"]][index][1]},
                         'locked': True if index == 0 else False})
    if show_links:
        for link in FORMATION_LINK[my_team["formation"]]:
            same_club = True if my_team_df.iloc[int(link[0])]["club_id"] == my_team_df.iloc[int(link[1])][
                "club_id"] else False
            same_nation = True if my_team_df.iloc[int(link[0])]["nationality"] == my_team_df.iloc[int(link[1])][
                "nationality"] else False

            if same_nation or same_club :
                team_chemistry = max(0, min(team_chemistry+6, 100))

            elements.append(
                {'data': {'source': link[0], 'target': link[1]},
                 'classes': 'green-link' if same_nation or same_club else 'red-link'}
            )

    return elements


def layout():

    team_overall, team_overall_stats = calc_team_overall()
    return html.Div(children=[
        html.Div(id="hidden-div", style={"display": "none"}),
        html.Div([dash.html.H2(children='Squad Builder')], style={"flex": "0 1 auto"}, className="heading"),
        html.Div([

            html.Div([
                dbc.Input(id="input_player2", placeholder="Search a player ...", type="text",
                          style={"flex": "0 1 auto", "height": "50px"}),
                dbc.Collapse(
                    [dbc.ListGroup(id="search_result2",
                                   style={"margin-top": "20px", "flex": "0 1 auto", "max-height": "300px",
                                          "overflow-y": "scroll"})],
                    id="collapse2",
                    is_open=False,
                ),
                html.Div(children=sidebar, id="sidebar", className="dash_block",
                    style={"flex": "1 1 auto", "width": "100%", "margin-top": "20px", "overflow": "hidden",
                           "align-items": "flex-start"})
            ], style={"height": "100%", "width": "250px", "display": "flex", "flex-direction": "column",
                      "margin-right": '20px'}),
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        ["442", "433"],
                        my_team["formation"],
                        id="dropdown",
                        style={"border": "solid 0px"}
                    ),
                    dbc.Input(id="input_team_name", placeholder=my_team.get("name", "Your team's name"), type="text",
                              style={"flex": "0 1 auto", "height": "36px", "width": "250px", "border": "solid 0px"}),
                    html.Button('Random Team', id='rdm_team', n_clicks=0, className="btn btn-primary"),
                    html.Button('Hide Links' if show_links else "Show Links", id='toggle_links', n_clicks=0,
                                className="btn btn-primary"),

                ], className="dash_block",
                    style={"height": "50px", "margin-bottom": "20px", "width": "100%", "gap": "20px",
                           "flex": "0 1 auto", "padding": "0px 30px"}),
                html.Div([
                    html.Img(src="assets/field.svg", width="650px"),
                    html.Div([
                        cyto.Cytoscape(
                            id='cytoscape',
                            zoom=1.5,
                            userZoomingEnabled=False,
                            userPanningEnabled=False,
                            layout={'name': 'preset', "fit": False, },
                            style={'width': '100%', 'height': '100%'},
                            elements=build_nodes(),
                            stylesheet=style
                        )
                    ], style={"position": "absolute", "width": "100%", "height": "100%", "top": "0px", "left": "0px"})
                ], className="dash_block",
                    style={"padding": '30px', "background-color": "#1F2937", "position": "relative",
                           'height': 'min-content', "flex": "0 1 auto"}),
                html.Div([], className="dash_block", style={"flex": "1 1 auto", "width": "100%", "margin-top": "20px"})
            ], style={"display": "flex", "flex-direction": "column"}),
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Team overall"),
                        dash.html.Div([
                            dcc.Graph(figure=sf.build_overall_pie(team_overall), config={
                                "displaylogo": False,
                                'displayModeBar': False,
                            }),
                            dash.html.H2(team_overall, style={"position": "absolute", "left": "50%", "top": "50%",
                                                              "transform": "translate(-50%,-50%)"})
                        ], style={"position": "relative"}),
                    ], className="dash_block", style={"flex-direction": "column"}),

                    html.Div([
                        html.H3("Chemistry"),
                        dash.html.Div([
                            dcc.Graph(figure=sf.build_overall_pie(team_chemistry), config={
                                "displaylogo": False,
                                'displayModeBar': False,
                            }),
                            dash.html.H2(team_chemistry, style={"position": "absolute", "left": "50%", "top": "50%",
                                                                "transform": "translate(-50%,-50%)"})
                        ], style={"position": "relative"}),
                    ], className="dash_block", style={"flex-direction": "column"}),
                ], style={"display":"flex", "gap":"20px", "margin-bottom":"20px"}),


                dash.html.Div([
                    html.H3("Team stats"),
                    dcc.Graph(figure=sf.build_overall_radar(team_overall_stats, 150), config={
                        "displaylogo": False,
                        'displayModeBar': False,
                    }),
                ], className="dash_block", style={"flex-direction":"column"}),



            ], style={
                "height":"100%", "margin-left":"20px"
            })
        ], style={"padding": "20px", "flex": "1 1 auto", "display": "flex", "flex-direction": "row"}),

    ], id="squad_builder_content",
        style={"height": "calc(100vh - 4rem)", "display": "flex", "flex-direction": "column"})


def calc_team_overall():
    roles = sf.FORMATIONS[my_team["formation"]]
    team_overall = 0
    team_overall_stats = []
    for index, player in my_team_df.iterrows():
        role = roles[my_team.get("players", []).index(player.get("id", ""))]
        overall, overall_stats, stats_col = sf.get_overall(player, role)
        team_overall += overall
        if role not in player["roles"]:
            role = ast.literal_eval(player["roles"])[0]
            overall, overall_stats, stats_col = sf.get_overall(player, role)
        if index != 0:
            team_overall_stats.append(overall_stats)
    team_overall /= 11
    team_overall_stats = np.mean(np.array(team_overall_stats), axis=0)

    return round(team_overall), team_overall_stats


def create_sidebar_content(player_id):
    player = app.df_all_role[app.df_all_role['id'] == player_id]
    roles = sf.FORMATIONS[my_team["formation"]]
    try:
        role = roles[my_team.get("players", []).index(player.iloc[0].get("id", ""))]
    except:
        role = ast.literal_eval(player["roles"].iloc[0])[0]

    player_physique = sf.get_physique(player)
    overall, overall_stats, stats_col = sf.get_overall(player.iloc[0], role)

    sidebar = html.Div([
        html.A([html.H3(player["name"].iloc[0])], href="/players?player_id=" + player["id"].iloc[0],
               style={"color": "#111827", "display": "flex", "margin-bottom": "0px", "width":"100%"}),
        html.Div([
            html.Span(r, style={"margin-right":"5px"})
            for r in ast.literal_eval(player["roles"].iloc[0])
        ], style={"margin-bottom": "25px", "width":"100%"}),
        html.Div([
            dash.html.Img(src=player["img"].iloc[0], height="50px", style={"margin-right": "10px"}),
            dash.html.Div([
                dash.html.Div([
                    dash.html.Div([
                        dash.html.Img(src=FLAG_URL + player["flag_name"].iloc[0] + ".svg", width="18px",
                                      style={"border-radius": "1px"})
                    ], style={"padding": "3px", "border-radius": "3px", "background-color": "#D7DEE5",
                              "display": "flex"}),
                ], style={"display": "flex", "align-items": "center", "gap": "10px"}),
                dash.html.H4(sf.calculate_age(str(player["birth_date"].iloc[0])) + " ans", className="light_text",
                             style={"margin": "0px", "display": "inline-block"}),
                dash.html.Span(
                    player_physique,
                    className="light_text",
                    style={"display": "block", "font-size": "10px"})
            ], style={"margin-right": "25px"}),
            dash.html.H2(str(overall), style={"margin": "0px"})
        ], style={"display": "flex", "align-items": "center", "margin-bottom": "5px"}),
        dcc.Graph(figure=sf.build_overall_radar(overall_stats,150), config={
            "displaylogo": False,
            'displayModeBar': False,
        }, style={"margin":"20px 0px"}),
        html.Button('Replace', id="replace_btn", name=player["id"].iloc[0], n_clicks=0, className="btn btn-primary"),

    ], style={"display":"flex", "flex-direction":"column", "align-items":"center"})
    return sidebar


@dash.callback(
    Output("squad_builder_content", "children"),
    Input("rdm_team", "n_clicks"),
    Input("toggle_links", "n_clicks"),
    Input('dropdown', 'value'),
    Input('cytoscape', 'tapNodeData'),
    prevent_initial_call=True,
)
def reload_data(rdm_team, toggle_links, value, data):
    global my_team_df, show_links, to_replace, sidebar
    trigger_id = dash.ctx.triggered_id


    if trigger_id == "rdm_team":
        sf.create_random_team()
        my_team_df = make_my_team_df()
    elif trigger_id == "toggle_links":
        if show_links:
            show_links = False
        else:
            show_links = True
    elif trigger_id == "dropdown":
        if value is not None and value != my_team["formation"]:
            my_team["formation"] = value
            with open("data/my_team.json", "w", encoding="utf-8") as file:
                json.dump(my_team, file)
            my_team_df = make_my_team_df()
    elif trigger_id == "cytoscape":
        if to_replace is not None :
            player1 = to_replace
            player2 = data["data"]
            index1 = None
            index2 = None
            if player1 in my_team["players"]:
                index1 = my_team["players"].index(player1)
            if player2 in my_team["players"]:
                index2 = my_team["players"].index(player2)

            if index1 is not None :
                my_team["players"][index1] = player2

            if index2 is not None :
                my_team["players"][index2] = player1

            with open("data/my_team.json", "w", encoding="utf-8") as file:
                json.dump(my_team, file)

            to_replace = None
            my_team_df = make_my_team_df()
        else :
            sidebar = create_sidebar_content(data["data"])


    return layout()

@dash.callback(
    Output("collapse2", "is_open"),
    [Input("input_player2", "value")]
)
def toggle_collapse(val):
    if val == "" or val is None:
        return False
    return True


@dash.callback(
    Output("search_result2", "children"),
    [Input("input_player2", "value")]
)
def fill_search_result(val):
    if val == "" or val is None:
        return None
    result = app.df_best_role[app.df_best_role['name'].str.contains(val + "|" + val.capitalize())]

    result_hml = [dbc.ListGroupItem(row["name"],
                                    className="link_list_group",
                                    id={"type": "list-group-item", "index": row["id"]},
                                    style={"text-decoration": "none", "color": "#111827"})
                  for index, row in result.iterrows()]
    return result_hml


@dash.callback(Output('sidebar', 'children'),
               Output("input_player2", "value"),
               Input({'type': 'list-group-item', 'index': ALL}, 'n_clicks'),
               State("input_player2", "value"),
               prevent_initial_call=True,
               )
def display_tap_node_data(n_clicks, value):
    global sidebar, to_update_search_result, to_replace
    if callback_context.triggered[0]['value'] is not None :
        if len(callback_context.triggered) == 1 and callback_context.triggered[0]['value'] > 0:
            clicked_id = callback_context.triggered[0]["prop_id"]
            clicked_id = json.loads(clicked_id.split(".")[0])["index"]
            sidebar = create_sidebar_content(clicked_id)
            return sidebar, ""



@dash.callback(
    Output("hidden-div", "children"),
    Input("input_team_name", "value"),

)
def change_name(value):
    if value is not None and value != "":
        my_team["name"] = value
        with open("data/my_team.json", "w", encoding="utf-8") as file:
            json.dump(my_team, file)
    return ""


@dash.callback(
    Output("replace_btn", "children"),
    Output("replace_btn", "className"),
    Input("replace_btn", "n_clicks"),
    State("replace_btn", "name")
)
def change_name(n_clicks, name):
    global to_replace
    if n_clicks%2 == 0 :
        to_replace = None
        return "Replace", "btn btn-primary"
    else:
        to_replace = name
        return "Cancel", "btn btn-danger"



