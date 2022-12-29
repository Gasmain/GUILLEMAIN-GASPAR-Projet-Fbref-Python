import os
import ast
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from utils import shared_functions as sf, Constants
import app

dash.register_page(__name__)

player = None
player_id = None
role = None


# In arguments are passed the get query passed in url. Ex : ?player_id_url="xuz80ed" -> layout("xuz80ed")
def layout(player_id_url=None, role_url=None, **other_unknown_query_strings):
    global player, player_id, role

    player_page = ""

    set_player(player_id_url)  # Defines the player to be shown
    set_role(role_url)  # Defines the role of the player to be used
    overall, overall_stats = sf.get_overall(player.iloc[0], role)
    stats_col = sf.get_player_stats(player.iloc[0], role)  # All the player's stats
    try:
        if os.path.exists(Constants.TEAM_IMG_FOLDER + "/" + player["club_id"].iloc[0] + ".png"):
            team_img = Constants.TEAM_IMG_FOLDER + "/" + player["club_id"].iloc[0] + ".png"
        else:
            team_img = Constants.DEFAULT_TEAM_IMG
    except:
        team_img = Constants.DEFAULT_TEAM_IMG

    # TODO : DO THE SAME THAN FOR PLAYER["IMG"]

    player_page = build_player_page(team_img, overall, overall_stats, stats_col)

    content = html.Div(children=[
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
    return content


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

    result_hml = [dbc.ListGroupItem([html.A(row["name"], href="/players?player_id_url=" + row["id"],
                                            className="link_list_group",
                                            style={"text-decoration": "none", "color": "#111827"})])
                  for index, row in result.iterrows()]
    return result_hml


def build_similar_player_list():
    """
    Returns a list of the similar players
    :return: the a div with the list of the similar players
    """
    global player, player_id, role

    # Make a df containing the similar players found for players
    # We use ast.literal_eval to convert to array the string given by player["similar..."]
    # "[...,...,...]" -> [...,...,...]
    similar_players = app.df_best_role[app.df_all_role['id'].isin(ast.literal_eval(player["similar_players"].iloc[0]))]
    similar_players = similar_players.reset_index(drop=True)

    result = html.Div(html.Div([
        html.A([
            html.Img(src=row["img"], height="30px", style={"margin-right": "10px"}),
            dash.html.Div([
                dash.html.Img(src=Constants.FLAG_URL + row["flag_name"] + ".svg", width="14x",
                              style={"border-radius": "1px"})
            ], style={"padding": "5px", "border-radius": "2px", "background-color": "#D7DEE5",
                      "display": "flex", "margin-right": "10px"}),
            html.Span(row["name"],
                      style={"max-width": "120px", "display": "block", "color": "#111827", "text-overflow": "ellipsis",
                             "overflow": "hidden", "white-space": "nowrap"}),
        ], style={"display": "flex", "align-items": "center", "margin": "10px 0px"},
            href="/players?player_id_url=" + row["id"])
        for index, row in similar_players.iterrows()

    ], style={"position": "absolute"}),
        style={"flex": "1 1 auto", "position": "relative", "width": "100%", "overflow-y": "scroll"})
    return result


def get_color_by_rate(rate):
    """
    Returns a color depending on the rate given
    :param rate: a rate between 0 and 100
    :return: returns the hex value of the color
    """
    if rate >= 75:
        return "#27AC5F"
    elif rate >= 50:
        return "#B8D640"
    elif rate >= 25:
        return "#F29947"
    else:
        return "#EB5757"


def set_player(player_id_url):
    """
    initialize the player thanks to the player_id_url
    and if player_id_url is none it picks a random player
    :param player_id_url: the player_id passed in url and none if no player_id was given
    """
    global player, player_id

    if player_id_url is None:
        # If no player id were passed in url, we pick a random player to display
        player = app.df_all_role.sample()
        player_id = player["id"].iloc[0]
    else:
        player = app.df_all_role[app.df_all_role['id'] == player_id_url]
        player_id = player_id_url


def set_role(role_url):
    """
    initialize the player's role thanks to the role_url
    and if role_url is none or is not in player's role it picks the player's best role
    :param role_url: the role passed in url and none if no role was given
    """
    global role

    if role_url is None:
        role = ast.literal_eval(player["roles"].iloc[0])[0]
    else:
        if role_url not in ast.literal_eval(player["roles"].iloc[0]):
            role = ast.literal_eval(player["roles"].iloc[0])[0]
        else:
            role = role_url


def build_position_buttons():
    """
    Builds a button for each role the player can play, the current role is displayed in the primary ui color
    and the others in the secondary ui color
    :return: the list of buttons
    """
    global player, player_id, role
    position_buttons = [
        html.A([html.Button(r, className="btn btn-primary" if r == role else "btn btn-secondary")],
               href="/players?player_id_url=" + player_id + "&role_url=" + r)
        for index, r in enumerate(ast.literal_eval(player["roles"].iloc[0]))
    ]
    return position_buttons


def build_player_name_h2():
    """
    builds an h2 with the player's name. If their is a space in his name, the first space is replaced with
    a break line
    :return:
    """
    global player

    if " " not in player["name"].iloc[0]:
        player_name = [player["name"].iloc[0]]
    else:
        # else takes the part before the first space then adds a break line and finally puts the rest of the name
        player_name = [player["name"].iloc[0].split(' ', 1)[0], html.Br(), player["name"].iloc[0].split(' ', 1)[1]]

    player_h2 = dash.html.H2(
        player_name,
        style={"max-width": "200px", "margin-left": "30px"})

    return player_h2


def build_player_page(team_img, overall, overall_stats, stats_col):
    global player, player_id, role
    player_page = html.Div([
        html.Div([
            html.Div([
                build_player_info_section(team_img),
                build_overall_block(overall)
            ], style={"padding": "20px 0px", "display": "flex", "gap": "20px", "flex": "0 1 auto",
                      "width": "min-content"}),
            html.Div([
                html.Div([
                    build_radar_block(overall_stats),
                    build_similar_player_block()
                ], style={"display": "flex", "flex-direction": "column", "flex": "0 1 auto"}),
                build_stat_list_block(stats_col)
            ], style={"display": "flex", "gap": "20px", "flex": "1 1 auto"}),
        ], style={"display": "flex", "flex-direction": "column", "width": "min-content", "height": "100%"})
    ], style={"flex": "1 1 auto", "display": "flex"})
    return player_page


def build_player_info_section(team_img):
    """
    Builds the block containing all the player info ( Name, age, club ... )
    :param team_img: path to the image of the player's team
    :return: the info block
    """
    global player, player_id, role
    section = html.Div([
        dash.html.Img(src=player["img"].iloc[0], height="70px", style={"margin-right": "30px"}),
        dash.html.Div([
            build_nation_flag(),
            dash.html.H3(str(sf.calculate_age(str(player["birth_date"].iloc[0]))) + " ans",
                         className="light_text",
                         style={"margin-top": "5px", "display": "inline-block"}),
            dash.html.Span("(" + player["birth_date"].iloc[0] + ")", className="light_text",
                           style={"margin-left": "3px"}),
            dash.html.Span(
                sf.get_physique(player),
                className="light_text",
                style={"display": "block"})
        ]),
        build_player_name_h2(),
        dash.html.Div(className="separator"),
        dash.html.Img(src=team_img, height="60px", style={"margin-right": "10px"})

    ], className="dash_block")
    return section


def build_nation_flag():
    """
    Builds the block containing the flag and the nation name
    :return: html div
    """
    global player, player_id, role

    return dash.html.Div([
        dash.html.Div([
            dash.html.Img(src=Constants.FLAG_URL + player["flag_name"].iloc[0] + ".svg",
                          width="26x",
                          style={"border-radius": "3px"})
        ], style={"padding": "5px", "border-radius": "4px", "background-color": "#D7DEE5",
                  "display": "flex"}),
        dash.html.Span(player["nationality"].iloc[0], className="light_text")

    ], style={"display": "flex", "align-items": "center", "gap": "10px"})


def build_overall_block(overall):
    """
    Builds the block containing the overall pie and the role buttons
    :param overall: the value of the overall
    :return: return the overall block
    """
    global player, player_id, role

    return dash.html.Div([
        dash.html.Div([
            dcc.Graph(figure=sf.build_overall_pie(overall), config={
                "displaylogo": False,
                'displayModeBar': False,
            }),
            dash.html.H2(overall, style={"position": "absolute", "left": "50%", "top": "50%",
                                         "transform": "translate(-50%,-50%)"})
        ], style={"position": "relative"}),
        html.Div(build_position_buttons(), style={"margin-left": "30px", "display": "flex", "gap": "10px"})
    ], className="dash_block")


def build_radar_block(overall_stats):
    """
    Builds the block containing the radar
    :param overall_stats: the stats to build the radar
    :return: the radar block
    """

    return dash.html.Div([
        dcc.Graph(figure=sf.build_overall_radar(overall_stats), config={
            "displaylogo": False,
            'displayModeBar': False,
        })

    ], className="dash_block")


def build_similar_player_block():
    """
    Build the block containing the similar players
    :return: the block
    """
    return html.Div([
        html.H3("Similar players :", style={"flex": "0 1 auto"}),
        build_similar_player_list()
    ], className="dash_block",
        style={"display": "flex", "flex-direction": "column", "align-items": "flex-start",
               "margin": "20px 0px 0px 0px", "width": "100%", "flex": "1 1 auto"})


def build_stat_list_block(stats_col):
    """
    Builds a block with all the player's stats
    :param stats_col: the list of stats
    :return: the block of stats
    """
    component = html.Div([
        html.Div([
            build_stat_component(name)
            for name in stats_col
        ], style={"position": "absolute", "height": "100%", "width": "100%"})
    ], className="dash_block", style={"flex": "1 1 auto", "display": "flex", "flex-direction": "column",
                                      "align-items": "flex-start", "gap": "10px", "overflow-y": "scroll",
                                      "position": "relative"})
    return component


def build_stat_component(name):
    """
    Builds a div containing a progress bar and a value representing the stat passed in arguments
    :param name: the name of the stat
    :return: a div containing the representation of the stat
    """
    global player, role

    component = html.Div([
        html.Span(name.replace("stats." + role + ".", "").replace("_percentile", "")),
        html.Div([
            html.Div(
                [html.Div(
                    style={"width": str(int(player[name].iloc[0])) + "%", "height": "100%",
                           "background-color": get_color_by_rate(int(player[name].iloc[0]))})],
                style={"height": "10px", "background-color": "#D7DEE5", "flex": "1 1 auto"}),
            html.Span(str(int(player[name].iloc[0])),
                      style={"margin-left": "20px", "flex": "0 1 auto", "display": "block",
                             "width": "30px", "font-weight": "700",
                             "color": get_color_by_rate(int(player[name].iloc[0]))})
        ], style={"display": "flex", "width": "calc(100% - 50px)", "align-items": "center"})
    ], style={"display": "flex", "align-items": "flex-start", "width": "100%",
              "flex-direction": "column", "margin-bottom": "5px"})

    return component
