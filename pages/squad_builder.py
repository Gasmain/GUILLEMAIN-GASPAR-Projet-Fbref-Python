import ast
import json
from sre_parse import State
from utils import simple_functions as sf
import dash
from dash import html, dcc, Output, Input, callback, ALL
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc

import app

dash.register_page(__name__, path='/squad-builder', )

FLAG_URL = "https://cdn.ssref.net/req/1637611918233-20211022/flags/"
MY_TEAM_PATH = "data/my_team.json"
FORMATION_POSITION = {
    "442": [[40, 145], [100, 105], [100, 185], [150, 240], [150, 50], [230, 185], [230, 105], [320, 50], [320, 240],
            [400, 105], [400, 185]],
    "443": [[40, 145], [100, 105], [100, 185], [150, 240], [150, 50], [220, 145],[260, 185], [260, 105], [320, 50], [320, 240],
            [400, 145],]}


FORMATION_LINK = {
    "442": [["0", "1"], ["0", "2"], ["1", "2"], ["2", "3"], ["4", "1"], ["4", "7"], ["1", "6"], ["6", "7"], ["2", "5"],
            ["8", "3"], ["8", "5"], ["8", "10"], ["5", "6"], ["9", "7"], ["9", "6"], ["9", "10"], ["5", "10"]]}

show_links = True
my_team = None

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
    f = open(MY_TEAM_PATH)
    my_team = json.load(f)
    sorter = list(my_team["players"])
    team_df = app.df_all_role[app.df_all_role.id.isin(my_team["players"])]
    team_df.sort_values(by="id", key=lambda column: column.map(lambda e: sorter.index(e)), inplace=True)
    team_df = team_df.reset_index(drop=True)
    if len(team_df) != 11:
        sf.create_random_team()
        team_df = make_my_team_df()
    return team_df

my_team_df = make_my_team_df()

def build_nodes():
    elements = []
    for index, row in my_team_df.iterrows():
        elements.append({'data': {'id': str(index), 'label': row["name"],
                                  'url': row["img"], 'data':row["id"]},
                         'position': {'x': FORMATION_POSITION["442"][index][0],
                                      'y': FORMATION_POSITION["442"][index][1]},
                         'locked': True if index == 0 else False})
    if show_links:
        for link in FORMATION_LINK["442"]:
            same_club = True if my_team_df.iloc[int(link[0])]["club_id"] == my_team_df.iloc[int(link[1])][
                "club_id"] else False
            same_nation = True if my_team_df.iloc[int(link[0])]["nationality"] == my_team_df.iloc[int(link[1])][
                "nationality"] else False
            elements.append(
                {'data': {'source': link[0], 'target': link[1]},
                 'classes': 'green-link' if same_nation or same_club else 'red-link'}
            )

    return elements


def layout():
    return html.Div(children=[
        html.Div([dash.html.H2(children='Squad Builder')], style={"flex": "0 1 auto"}, className="heading"),
        html.Div([

            html.Div([
                dbc.Input(id="input_player2", placeholder="Search a player ...", type="text", style={"flex": "0 1 auto", "height":"50px"}),
                dbc.Collapse(
                    [dbc.ListGroup(id="search_result2",
                                   style={"margin-top": "20px", "flex": "0 1 auto", "max-height": "300px",
                                          "overflow-y": "scroll"})],
                    id="collapse2",
                    is_open=False,
                ),
                html.Div([

                ],id="sidebar", className="dash_block", style={"flex": "1 1 auto", "width":"100%","margin-top":"20px","overflow":"hidden","align-items":"flex-start"})
            ], style={"height":"100%", "width":"250px","display":"flex", "flex-direction":"column", "margin-right":'20px'}),
            html.Div([
                html.Div([
                    html.Button('Random Team', id='rdm_team', n_clicks=0, className="btn btn-primary"),
                    html.Button('Hide Links' if show_links else "Show Links", id='toggle_links', n_clicks=0, className="btn btn-primary"),
                ], className="dash_block", style={ "height":"50px", "margin-bottom":"20px", "width":"100%", "gap":"20px","flex": "0 1 auto"}),
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
                           'height': 'min-content',"flex": "0 1 auto"}),
                html.Div([], className="dash_block", style={"flex": "1 1 auto", "width":"100%","margin-top":"20px"})
            ], style={"display":"flex", "flex-direction":"column"}),
        ], style={"padding": "20px", "flex": "1 1 auto", "display": "flex", "flex-direction": "row"})

    ], id="squad_builder_content", style={"height": "calc(100vh - 4rem)", "display": "flex", "flex-direction": "column"})





@dash.callback(
    Output("squad_builder_content", "children"),
    Input("rdm_team", "n_clicks"),
    Input("toggle_links", "n_clicks"),
    prevent_initial_call=True,
)
def reload_data(rdm_team, toggle_links):
    global my_team_df, show_links
    button_id = dash.ctx.triggered_id

    if button_id == "rdm_team":
        sf.create_random_team()
        my_team_df = make_my_team_df()
    elif button_id == "toggle_links":
        if show_links:
            show_links = False
        else:
            show_links = True

    return layout()


@dash.callback(Output('sidebar', 'children'),
               Input('cytoscape', 'tapNodeData'),
               prevent_initial_call=True,
               )
def displayTapNodeData(data):
    print(data)
    if data is not None:
        player = app.df_all_role[app.df_all_role['id'] == data["data"]]
        role = ast.literal_eval(player["roles"].iloc[0])[0]
        player_physique = sf.get_physique(player)
        overall, overall_stats, stats_col = sf.get_overall(player, role)

        sidebar = html.Div([
            html.A([html.H3(player["name"].iloc[0])],href="/players?player_id=" + player["id"].iloc[0], style={"color":"#111827", "margin-bottom":"15px","display":"flex"}),
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
                            style={"display": "block", "font-size":"10px"})
                    ],style={"margin-right":"25px"}),
                    dash.html.H2(str(overall), style={"margin":"0px"})
                ], style={"display":"flex","align-items":"center", "margin-bottom":"5px"}), ])
        return sidebar


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

    result_hml = [dbc.ListGroupItem([html.A(row["name"],
                                            className="link_list_group",
                                            style={"text-decoration": "none", "color": "#111827"})])
                  for index, row in result.iterrows()]
    return result_hml