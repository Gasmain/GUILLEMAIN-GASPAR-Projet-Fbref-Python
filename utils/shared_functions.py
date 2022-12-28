import ast
import math
import plotly.graph_objects as go
import os
import random
import pandas as pd
import json
from datetime import date
from datetime import datetime
import pycountry
import app
from utils import Constants

def build_data_frame():
    """
        Loads the json Data and creates 2 Dataframe from this data, one with all the possible roles for each players, and
        one with only the best role of each player. This makes data manipulation much easier
    """
    f = open(Constants.PLAYER_FILE_JSON)
    data_json = json.load(f)
    for player in data_json:
        for role in player["roles"]:
            stat_list = get_stat_list(role)
            player = build_overall(player, role, stat_list)

    # Creates a Dataframe by flattening the json  data : { stats : { hello :  "foo"}} would create a column,
    # data.stats.hello
    df_role = pd.json_normalize(data_json)

    # here we build the second df with only the best role, so we only keep the stats of the first role
    for player in data_json:
        best_pos_stats = player["stats"][list(player["stats"].keys())[0]]
        player["stats"] = best_pos_stats
        best_pos_rol = player["roles"][0]
        player["roles"] = best_pos_rol

    df_best_pos = pd.json_normalize(data_json)

    # We save both df in csv to be used later
    df_best_pos.to_csv(Constants.PLAYER_BEST_ROLE_FILE_CSV, encoding='utf-8', index=False)
    df_role.to_csv(Constants.PLAYER_ALL_ROLE_FILE_CSV, encoding='utf-8', index=False)


def get_stat_list(role):
    """
    Returns the right list of stats for each roles
    :param role: String ex : "CB"
    :return: list of json objects
    """
    if role == "CB":
        return Constants.CB_OVERALL_STATS
    elif role == "FB":
        return Constants.FB_OVERALL_STATS
    elif role == "FW":
        return Constants.FW_OVERALL_STATS
    elif role == "AM":
        return Constants.AM_OVERALL_STATS
    elif role == "GK":
        return Constants.GK_OVERALL_STATS
    elif role == "MF":
        return Constants.MF_OVERALL_STATS
    return []


def build_overall(player, role, stat_list):
    """
    Add for a given player and role adds his overall (general stat) and his overall stats for each categories
    (Attack, Defense, Dribbling, Passing, Mental)

    :param player: json object representing a player
    :param role: the player's role
    :param stat_list: the list of stats used to determine it's overall
    :return: returns the player
    """
    overall = 0
    overall = calc_overall(player, role, stat_list)
    player["stats"][role].update({"overall": overall})

    if role != "GK":  # Goalkeepers don't have these stats so we don't build them for Goalkeepers
        player["stats"][role].update({"atk_overall": calc_overall(player, role, Constants.ATK_OVERALL_STATS)})
        player["stats"][role].update({"dribble_overall": calc_overall(player, role, Constants.DRB_OVERALL_STATS)})
        player["stats"][role].update({"pass_overall": calc_overall(player, role, Constants.PASS_OVERALL_STATS)})
        player["stats"][role].update({"mental_overall": calc_overall(player, role, Constants.MENTAL_OVERALL_STATS)})
        player["stats"][role].update({"def_overall": calc_overall(player, role, Constants.DEF_OVERALL_STATS)})
    else:
        player["stats"][role].update({"atk_overall": 0})
        player["stats"][role].update({"dribble_overall": 0})
        player["stats"][role].update({"pass_overall": 0})
        player["stats"][role].update({"mental_overall": 0})
        player["stats"][role].update({"def_overall": 0})

    return player


def calc_overall(player, role, stat_list):
    count = 0
    overall = 0
    for stat in stat_list.keys():
        if stat + "_percentile" in player["stats"][role]:
            overall += int(player["stats"][role][stat + "_percentile"]) * stat_list[stat]
        else:
            overall += 50 * stat_list[stat]
        count += stat_list[stat]
    overall = overall / count
    if overall > 50:
        overall += (100 - overall) / 4
    elif overall < 50:
        overall -= overall / 4
    overall = round(overall)
    return overall


def create_random_team():
    """
        Creates a random team, stores it in a json file and saves it
    """
    my_team = {}

    key, value = random.choice(list(Constants.FORMATIONS.items()))  # Picks a random player formation (Layout) ex 4-4-2
    my_team["formation"] = key

    players = []
    f = open(Constants.PLAYER_FILE_JSON)
    data_json = json.load(f)

    # For each roles needed in the formation we pick a random player in our database that can play this role
    for role in value:
        player_role = ""
        while role not in player_role:  # While the randomly picked player doesn't match the role we pick again
            value = random.choice(data_json)
            player_role = value["roles"]

        players.append(value["id"])
    my_team["players"] = players
    # Now we have picked all the players we save the team json file
    with open(Constants.MY_TEAM_FILE, "w", encoding="utf-8") as file:
        json.dump(my_team, file)


def temp():
    f = open(Constants.PLAYER_FILE_JSON)
    data_json = json.load(f)
    for player in data_json:
        if os.path.exists(Constants.PLAYER_IMG_FOLDER + "/" + player["id"] + ".jpg"):
            player_img = Constants.PLAYER_IMG_FOLDER + "/" + player["id"] + ".jpg"

        else:
            player_img = Constants.DEFAULT_PLAYER_IMG
        player["img"] = player_img

    with open(Constants.PLAYER_FILE_JSON, "w", encoding="utf-8") as file:
        json.dump(data_json, file)


def calculate_age(born):
    """
    For a given birthdate it returns the age of the player
    :param born: a birthdate in string of type Y-m-d
    :return: an int representing the age
    """
    birth = datetime.strptime(born, '%Y-%m-%d')
    today = date.today()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return age


def get_overall(player, role):
    if player["stats." + role + ".overall"] is None or math.isnan(player["stats." + role + ".overall"]):
        overall_role = 0
    else:
        overall_role = player["stats." + role + ".overall"]

    stats_col = [col for col in player.keys() if
                 'stats.' + role in col and "percentile" in col and not math.isnan(player[col])]
    if len(stats_col) == 0:
        best_role = ast.literal_eval(player["roles"])[0]
        stats_col = [col for col in player.keys() if
                     'stats.' + best_role in col and "percentile" in col and not math.isnan(player[col])]

    overall = 0
    count = 0
    top_stat_count = 0
    for s in stats_col:
        if int(player[s]) >= 98:
            overall += int(player[s]) * 3
            count += 3
            top_stat_count += 1
        else:
            overall += int(player[s])
            count += 1

    overall = round(((overall / count) + overall_role) / 2)

    if overall > 50:
        overall += (100 - overall) / 4
    elif overall < 50:
        overall -= overall / 4

    overall = round(overall)
    overall = max(0, min(overall, 100))

    overall_stats = [player["stats." + role + ".atk_overall"],
                     player["stats." + role + ".dribble_overall"],
                     player["stats." + role + ".pass_overall"],
                     player["stats." + role + ".mental_overall"],
                     player["stats." + role + ".def_overall"]]

    return overall, overall_stats, stats_col


def get_physique(player):
    """
    Returns builds a string with the player's physical attributes
    :param player:
    :return: String of type  : 189 cm | 80 kg
    """

    # if all attributes are floats and not NaN
    if not math.isnan(player["height"].iloc[0]) and not math.isnan(player["weight"].iloc[0]):
        player_physique = str(int(player["height"].iloc[0])) + ' cm | ' + str(int(player["weight"].iloc[0])) + " kg"
    # if height is a floats and and weight is NaN
    elif not math.isnan(player["height"].iloc[0]):
        player_physique = str(int(player["height"].iloc[0])) + ' cm'
    # if height is a Nan and and weight is float
    elif not math.isnan(player["weight"].iloc[0]):
        player_physique = str(int(player["weight"].iloc[0])) + " kg"
    else:
        player_physique = ""
    return player_physique


def build_overall_radar(overall_stats, size=200):
    """
    Builds a plotly radar for a giving list of stat
    :param overall_stats:
    :param size: Default size of the radar is 200px but can be specified to something else
    :return: returns the plotly radar
    """
    overall_radar = go.Figure(data=go.Scatterpolar(
        r=overall_stats,
        theta=['ATK', 'DRI', 'PAS', 'MTL', 'DEF'],
        fill='toself'
    ))
    overall_radar.update(layout_showlegend=False)
    overall_radar.update_layout(margin=dict(t=10, b=10, l=30, r=30), height=size, width=size, polar=dict(
        radialaxis=dict(
            visible=False,
            range=[0, 99]
        )))

    return overall_radar


def build_overall_pie(overall):
    """
    Builds a plotly pie in a progress circle bat form for a giving stat
    :param overall:
    :return: plotly pie
    """
    #  Hole defines the thickness of the border (more exactly the size of the hole in the center of the pie)
    overall_pie = go.Figure(data=[go.Pie(labels=["progress", "rest"], values=[overall, 100 - overall], hole=0.85,
                                         marker=dict(colors=['#6265F0', '#D7DEE5']), direction='clockwise',
                                         sort=False)])
    overall_pie.update(layout_showlegend=False)
    overall_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=75, width=75)
    overall_pie.update_traces(textinfo='none', hoverinfo='skip', hovertemplate=None)
    return overall_pie



def build_map_csv():
    """
        builds a dataframe with each country as a row and the amount of player in col
        this dataframe is used to build the choropleth map later
    """
    nations = {}

    for index, player in app.df_best_role.iterrows():
        code = ""
        country = ""
        if player["nationality"] in Constants.error_countries:
            # If nationality is in the error list, set code variable to the given code. Ex Ireland : code = IRL
            code = Constants.error_countries[player["nationality"]]
            country = player["nationality"]
        elif player["nationality"] in Constants.no_countries:
            # For countries not in the map skip. Ex : Cape Verde
            print("skipped : " + player["nationality"])
            continue
        else:
            # Other wise search the country in pycountry lib and get the code
            result = pycountry.countries.search_fuzzy(player["nationality"])
            code = result[0].alpha_3
            country = result[0].name

        # if code is not in nation {} we add the country to nation
        # Else we increment it's number of player
        if code not in nations:
            nations[code] = {"player_nb": 1, "name": country}
        else:
            nations[code]["player_nb"] += 1

    # Build the df from nation {}, we reorganise the df and save it
    nation_df = pd.DataFrame.from_dict(nations, orient='index')
    nation_df["code"] = nation_df.index
    nation_df.rename(columns={0: 'player_nb'}, inplace=True)
    nation_df = nation_df.reset_index(drop=True)
    nation_df.to_csv(Constants.MAP_CSV, encoding='utf-8', index=False)
