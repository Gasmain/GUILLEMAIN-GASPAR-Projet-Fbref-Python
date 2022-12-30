import ast
import json
from utils import shared_functions as sf, Constants
import dash
from dash import html, dcc, Output, Input, State, callback, ALL, callback_context
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import app

dash.register_page(__name__, path='/squad-builder')

show_links = True
sidebar_content = ""
to_replace = None  # Variable containing the id of the player to be replaced when clicking on replace btn
team_chemistry = 0
my_team_df, my_team = sf.make_my_team_df()


def layout():
    """
    Creates the layout of the page
    :return: html div containing the content of the page
    """
    global my_team, my_team_df

    team_overall, team_overall_stats = sf.calc_team_overall(my_team, my_team_df)

    return html.Div(children=[
        html.Div(id="hidden-div", style={"display": "none"}),
        html.Div([dash.html.H2(children='Squad Builder')], style={"flex": "0 1 auto"}, className="heading"),
        html.Div([
            build_sidebar(),
            html.Div([
                build_edit_bar(),
                build_soccer_field(),
            ], style={"display": "flex", "flex-direction": "column"}),
            html.Div([
                build_team_graphs(team_overall, team_overall_stats),
            ], style={
                "height": "100%", "margin-left": "20px"
            })
        ], style={"padding": "20px", "flex": "1 1 auto", "display": "flex", "flex-direction": "row"}),

    ], id="squad_builder_content",
        style={"height": "calc(100vh - 4rem)", "display": "flex", "flex-direction": "column"})


def build_cytoscape():
    global show_links

    """
    builds the cytoscape elements, that is : nodes and links
    :return:
    """
    elements = []
    elements.extend(build_nodes())

    if show_links:
        elements.extend(build_node_links())

    return elements


def build_nodes():
    """
    Builds a node for every players in the team in the right x, y position depending on the
    team layout (442, 433)
    :return: the list of nodes
    """
    global my_team_df, my_team
    nodes = []
    for index, row in my_team_df.iterrows():
        nodes.append({'data': {'id': str(index), 'label': row["name"], 'url': Constants.PLAYER_IMG_URL.replace("player_id", row["id"]), 'data': row["id"]},
                      'position': {'x': Constants.FORMATION_POSITION[my_team["formation"]][index][0],
                                   'y': Constants.FORMATION_POSITION[my_team["formation"]][index][1]},
                      'locked': True if index == 0 else False})
    return nodes


def build_node_links():
    """
    Build a link for each links in the formation layout and define if it's a good link (player compatible) or not
    and increase team_chemistry accordingly
    :return: the list of links
    """
    global my_team, my_team_df, team_chemistry

    team_chemistry = 0
    link_list = []
    for link in Constants.FORMATION_LINK[my_team["formation"]]:
        # If the two players concerned by the link are in the same club
        same_club = True if my_team_df.iloc[int(link[0])]["club_id"] == my_team_df.iloc[int(link[1])][
            "club_id"] else False

        # If the two players concerned by the link have the same nationality
        same_nation = True if my_team_df.iloc[int(link[0])]["nationality"] == my_team_df.iloc[int(link[1])][
            "nationality"] else False

        if same_nation or same_club:
            # For each good links we increment chemistry by 6 and clamp the value between à and 100
            team_chemistry = max(0, min(team_chemistry + 6, 100))

        link_list.append(
            {'data': {'source': link[0], 'target': link[1]},
             'classes': 'green-link' if same_nation or same_club else 'red-link'}
            # Make link green if link is good red if not
        )
    return link_list


def build_sidebar():
    """
    Creates the sidebar in the layout, this contains, the search input, the search result, the sidebar content
    :return: html div containing the sidebar
    """
    global sidebar_content

    component = html.Div([dbc.Input(id="input_player2", placeholder="Search a player ...", type="text",
                                    style={"flex": "0 1 auto", "height": "50px"}),
                          dbc.Collapse(
                              [dbc.ListGroup(id="search_result2",
                                             style={"margin-top": "20px", "flex": "0 1 auto", "max-height": "300px",
                                                    "overflow-y": "scroll"})],
                              id="collapse2",
                              is_open=False,
                          ),
                          html.Div(children=sidebar_content, id="sidebar", className="dash_block",
                                   style={"flex": "1 1 auto", "width": "100%", "margin-top": "20px",
                                          "overflow": "hidden",
                                          "align-items": "flex-start"})
                          ], style={"height": "100%", "width": "250px", "display": "flex", "flex-direction": "column",
                                    "margin-right": '20px'}
                         )

    return component


def build_edit_bar():
    """
    Builds the bar above the soccer field, containing the call to action button, the input to choose formation
    and the editable name of the team.
    :return: a div containing the top bar block
    """
    component = html.Div([
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
                    className="btn btn-primary")],
        className="dash_block",
        style={"height": "50px", "margin-bottom": "20px", "width": "100%", "gap": "20px",
               "flex": "0 1 auto", "padding": "0px 30px"}
    )
    return component


def build_soccer_field():
    """
    Builds the soccer field that is : the soccer field image and the cytoscape ( nodes and links for players )
    :return: a div containing both the soccer field image and cytoscape
    """
    component = html.Div([
        html.Img(src="assets/field.svg", width="650px"),
        html.Div([
            cyto.Cytoscape(
                id='cytoscape',
                zoom=1.5,
                userZoomingEnabled=False,
                userPanningEnabled=False,
                layout={'name': 'preset', "fit": False, },
                style={'width': '100%', 'height': '100%'},
                elements=build_cytoscape(),
                stylesheet=Constants.NODE_STYLE
            )
        ], style={"position": "absolute", "width": "100%", "height": "100%", "top": "0px", "left": "0px"})
    ], className="dash_block",
        style={"padding": '30px', "background-color": "#1F2937", "position": "relative",
               'height': 'min-content', "flex": "0 1 auto"})
    return component


def build_pie_block(value, name):
    """
    Builds a block containing a pie representing the value passed in arg
    :param value: the value of the overall
    :param name: The text to display in the span
    :return: a div containing the block
    """
    component = html.Div([
        html.H3(name, style={"flex": "0 0 auto"}),
        dash.html.Div([
            dcc.Graph(figure=sf.build_overall_pie(value), config={
                "displaylogo": False,
                'displayModeBar': False,
            }),
            dash.html.H2(value, style={"position": "absolute", "left": "50%", "top": "50%",
                                       "transform": "translate(-50%,-50%)"})
        ], style={"position": "relative", "flex": "1 1 auto", "display": "flex", "align-items": "center"}),
    ], className="dash_block", style={"flex-direction": "column"})

    return component


def build_team_graphs(team_overall, team_overall_stats):
    """
    Builds both of the pies ( overall and chemistry ) and the radar
    :param team_overall: value of the overall to display in the pie
    :param team_overall_stats: list of stat to display in the radar
    :return: a div containing the graphs
    """
    global team_chemistry

    component = html.Div([
        build_pie_block(team_overall, "Team Overall"),
        build_pie_block(team_chemistry, "Team Chemistry"),
        dash.html.Div([
            html.H3("Team stats"),
            dcc.Graph(figure=sf.build_overall_radar(team_overall_stats, 150), config={
                "displaylogo": False,
                'displayModeBar': False,
            }),
        ], className="dash_block", style={"flex-direction": "column"}),
    ], style={"display": "flex", "gap": "20px", "margin-bottom": "20px", "flex-wrap": "wrap"})

    return component


def build_sidebar_player_info(player, overall):
    """
    builds in the sidebar the player's info (age , flag, overall and physique)
    :param player: the player displayed in the sidebar
    :param overall: the player's overall
    :return: returns a list of dash html elements
    """
    component = html.Div([
        dash.html.Img(src=Constants.PLAYER_IMG_URL.replace("player_id", player["id"].iloc[0]), height="50px", style={"margin-right": "10px"}),
        dash.html.Div([
            dash.html.Div([
                dash.html.Div([
                    dash.html.Img(src=Constants.FLAG_URL + player["flag_name"].iloc[0] + ".svg", width="18px",
                                  style={"border-radius": "1px"})
                ], style={"padding": "3px", "border-radius": "3px", "background-color": "#D7DEE5",
                          "display": "flex"}),
            ], style={"display": "flex", "align-items": "center", "gap": "10px"}),
            dash.html.H4(str(sf.calculate_age(str(player["birth_date"].iloc[0]))) + " ans", className="light_text",
                         style={"margin": "0px", "display": "inline-block"}),
            dash.html.Span(
                sf.get_physique(player),
                className="light_text",
                style={"display": "block", "font-size": "10px"})
        ], style={"margin-right": "25px"}),
        dash.html.H2(str(overall), style={"margin": "0px"})],
        style={"display": "flex", "align-items": "center", "margin-bottom": "5px"})
    return component


def create_sidebar_content(player_id):
    """
    Builds the content to display in the sidebar
    :param player_id: the id of the player to display
    :return: the div containing the content
    """
    player = app.df_all_role[app.df_all_role['id'] == player_id]  # Finds the player corresponding to id passed in arg

    # if players is in the team, we define role as his current position in team
    # else role is defined as the player's best role
    roles = Constants.FORMATIONS[my_team["formation"]]
    try:
        role = roles[my_team.get("players", []).index(player.iloc[0].get("id", ""))]
    except:
        role = ast.literal_eval(player["roles"].iloc[0])[0]

    overall, overall_stats = sf.get_overall(player.iloc[0], role)

    sidebar = html.Div([
        html.A([html.H3(player["name"].iloc[0])], href="/players?player_id=" + player["id"].iloc[0],
               style={"color": "#111827", "display": "flex", "margin-bottom": "0px", "width": "100%"}),
        html.Div([
            html.Span(r, style={"margin-right": "5px"})
            for r in ast.literal_eval(player["roles"].iloc[0])
        ], style={"margin-bottom": "25px", "width": "100%"}),

        build_sidebar_player_info(player, overall),

        dcc.Graph(figure=sf.build_overall_radar(overall_stats, 150), config={
            "displaylogo": False,
            'displayModeBar': False,
        }, style={"margin": "20px 0px"}),

        html.Button('Replace', id="replace_btn", name=player["id"].iloc[0], n_clicks=0, className="btn btn-primary"),

    ], style={"display": "flex", "flex-direction": "column", "align-items": "center"})
    return sidebar


def replace_player(player_id):
    """
    Replace the player to be replace stored in to_replace by the player passed in arg
    :param player_id: the id of the player to replace with the one stored in to_replace
    """
    global to_replace, my_team, my_team_df

    player1 = to_replace
    player2 = player_id
    index1 = None
    index2 = None
    if player1 in my_team["players"]:
        index1 = my_team["players"].index(player1)
    if player2 in my_team["players"]:
        index2 = my_team["players"].index(player2)

    if index1 is not None:
        my_team["players"][index1] = player2

    if index2 is not None:
        my_team["players"][index2] = player1

    with open("data/my_team.json", "w", encoding="utf-8") as file:
        json.dump(my_team, file)

    to_replace = None
    my_team_df, my_team = sf.make_my_team_df()


@dash.callback(
    Output("squad_builder_content", "children"),
    Input("rdm_team", "n_clicks"),
    Input("toggle_links", "n_clicks"),
    Input('dropdown', 'value'),
    Input('cytoscape', 'tapNodeData'),
    prevent_initial_call=True,
)
def reload_data(rdm_team, toggle_links, value, data):
    """
    This function is called when a node is cliked, when the formation is changed, when links have been disabled or
    when a random team has been created. The function treats each case and reloads the layout
    :param rdm_team: number of clicks the btn has been clicked (not used but is needed, else the callback won't work)
    :param toggle_links: number of clicks the btn has been clicked (not used but is needed, else the callback won't work)
    :param value: new value of the input ( is a string containing the new formation layout Ex : 442)
    :param data: the data contained by a node
    :return: new content of the page
    """
    global my_team_df, my_team, show_links, to_replace, sidebar_content

    trigger_id = dash.ctx.triggered_id  # Tells which input triggered the callback

    if trigger_id == "rdm_team":
        # Create a random team and update our df and our team dict
        sf.create_random_team()
        my_team_df, my_team = sf.make_my_team_df()

    elif trigger_id == "toggle_links":
        # Toggle the show_link variable
        if show_links:
            show_links = False
        else:
            show_links = True

    elif trigger_id == "dropdown":
        # if formation layout changed we change it in my_team and saves it in the json and we remake our df to take
        # modifications in account
        if value is not None and value != my_team["formation"]:
            my_team["formation"] = value
            with open(Constants.MY_TEAM_FILE, "w", encoding="utf-8") as file:
                json.dump(my_team, file)
            my_team_df, my_team = sf.make_my_team_df()

    elif trigger_id == "cytoscape":
        if to_replace is not None:
            replace_player(data["data"])
        else:
            # If no replace was executed no need to reload layout so we prevent update
            raise dash.exceptions.PreventUpdate

    return layout()


@dash.callback(
    Output("collapse2", "is_open"),
    [Input("input_player2", "value")]
)
def toggle_collapse(val):
    """
    Close the collapse if the search input is empty by putting is open to false
    Open the collapse if search input is not empty by putting is open to true
    :param val: the content of the search input
    :return: boolean determining state of collapse : true -> open , false -> close
    """
    if val == "" or val is None:
        return False
    return True


@dash.callback(
    Output("search_result2", "children"),
    [Input("input_player2", "value")]
)
def fill_search_result(val):
    """
    Feeds the list group with the result of the research. Finds players that contains the search value in their names
    :param val: search input value
    :return: search results as listGroupItem
    """
    if val == "" or val is None:
        return None

    # Get players containing the value of the search
    result = app.df_best_role[app.df_best_role['name'].str.contains(val + "|" + val.capitalize())]

    result_hml = [dbc.ListGroupItem(row["name"],
                                    className="link_list_group",
                                    # index and type very important for callback, type allows to get input for all items
                                    # and index allows to identify the item
                                    id={"type": "list-group-item", "index": row["id"]},
                                    style={"text-decoration": "none", "color": "#111827"},
                                    n_clicks=0)
                  for index, row in result.iterrows()]
    return result_hml


@dash.callback(Output('sidebar', 'children'),
               Output("input_player2", "value"),
               Input({'type': 'list-group-item', 'index': ALL}, 'n_clicks'),
               Input('cytoscape', 'tapNodeData'),
               prevent_initial_call=True,
               )
def display_player_sidebar(n_clicks, data):
    """
    Feeds the sidebar content with the player clicked on
    Gets called when a search result item is clicked or when a node is clicked

    Caution : callbacks get called when search results are created as well

    :param n_clicks: list of clicks for all the search result items
    :param data: data returned by a node (is always None)
    :return: returns the new content of the sidebar
    """
    global sidebar_content, to_replace

    trigger_id = dash.ctx.triggered_id  # Used to tell which input triggered callback

    if trigger_id == "cytoscape":
        if to_replace is None:  # If cytoscape wasn't clicked on te be replace but to be shown
            sidebar_content = create_sidebar_content(callback_context.triggered[0]['value']["data"])
            return sidebar_content, ""
    else:
        # If n_clicks contains 1 this means callback was triggered by a click and not the creation of result items
        if 1 in n_clicks:
            # Get the index of the item clicked on ( index is the player id )
            clicked_id = callback_context.triggered[0]["prop_id"]
            clicked_id = json.loads(clicked_id.split(".")[0])["index"]

            sidebar_content = create_sidebar_content(clicked_id)
            return sidebar_content, ""  # We clear the search input

    # If callback was triggered by creation of search result or cytoscape was clicked to be replaced
    # We don't want to update the side bar and the search input, so we prevent update
    raise dash.exceptions.PreventUpdate


@dash.callback(
    Output("hidden-div", "children"),
    Input("input_team_name", "value"),
)
def change_name(value):
    """
    Triggers when the team name input changes. Saves the value as the new team name in the json
    Outputs nothing to a hidden div as we have nothing to output
    :param value:
    :return:
    """
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
def toggle_replace_btn(n_clicks, name):
    """
    Saves the id of the player in to_replace if button replaced was clicked
    and removes it if button was in cancel state

    toggle states on each click, goes from "replace" to "cancel"
    :param n_clicks: number of times the button was clicked
    :param name: contains the player id
    :return: returns the text to display on the button, and the his class that dictates his color
    """
    global to_replace
    # If button was clicked a peer number of times  that means it was in cancel state so we remove to_replace
    # And put button back to replace state
    if n_clicks % 2 == 0:
        to_replace = None
        return "Replace", "btn btn-primary"
    # Opposite here
    else:
        to_replace = name
        return "Cancel", "btn btn-danger"
