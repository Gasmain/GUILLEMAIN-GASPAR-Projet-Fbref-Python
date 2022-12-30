import ast
import math
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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
    data_json = list(data_json.values())
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
    overall_role = calc_stats_overall(player, role, stat_list)
    overall = general_overall(overall_role, player["stats"][role])
    player["stats"][role].update({"overall": overall})

    if role != "GK":  # Goalkeepers don't have these stats so we don't build them for Goalkeepers
        player["stats"][role].update({"atk_overall": calc_stats_overall(player, role, Constants.ATK_OVERALL_STATS)})
        player["stats"][role].update({"dribble_overall": calc_stats_overall(player, role, Constants.DRB_OVERALL_STATS)})
        player["stats"][role].update({"pass_overall": calc_stats_overall(player, role, Constants.PASS_OVERALL_STATS)})
        player["stats"][role].update(
            {"mental_overall": calc_stats_overall(player, role, Constants.MENTAL_OVERALL_STATS)})
        player["stats"][role].update({"def_overall": calc_stats_overall(player, role, Constants.DEF_OVERALL_STATS)})
    else:
        player["stats"][role].update({"atk_overall": 0})
        player["stats"][role].update({"dribble_overall": 0})
        player["stats"][role].update({"pass_overall": 0})
        player["stats"][role].update({"mental_overall": 0})
        player["stats"][role].update({"def_overall": 0})

    return player


def calc_stats_overall(player, role, stat_list):
    """
    Calculate an overall rate from a list of stats. In the list of stats we have
    it's name and it's multiplication factor
    :param player: the player concerned by the calcul
    :param role: the role of the player
    :param stat_list: the list of stats and it's multiplication factor
    :return: the overall rate
    """
    count = 0
    overall = 0
    for stat in stat_list.keys():
        if stat + "_percentile" in player["stats"][role]:  # If player has this stat
            # We add it to the overall as many times as the factor says
            overall += int(player["stats"][role][stat + "_percentile"]) * stat_list[stat]
        else:
            overall += 50 * stat_list[stat]  # If player doesn't have this stat we consider it's average : so 50
        count += stat_list[stat]  # we increment the count variable by the factor of multiplication
    overall = overall / count
    overall = extrapolate_overall(overall)  # Extrapolate the rate (moves away from 50 and gets closer to 0 or 100)
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
        value = {"id":""}
        # While the randomly picked player doesn't match the role or is already in the ream we pick again
        while role not in player_role or value["id"] in players:
            value = random.choice(list(data_json.values()))
            player_role = value["roles"]

        players.append(value["id"])
    my_team["players"] = players
    # Now we have picked all the players we save the team json file
    with open(Constants.MY_TEAM_FILE, "w", encoding="utf-8") as file:
        json.dump(my_team, file)


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


def general_overall(overall_role, stats):
    """
    Calculates the mean of all the player stats for a role. stats above 97 counts triple
    (this favors player that excels in certain area)
    Then does a mean between the overall_role given in arguments and the mean determined above
    :param overall_role: the overall rate of a player for a role for a given list of stats that matter for the role
    :param stats: list of all the stats and it's value of the player for a given role
    :return: the general overall
    """
    overall = 0
    count = 0

    for s in stats:
        if "percentile" in s:  # If stat is percentile and not per90
            if int(stats[s]) > 97:
                overall += int(stats[s]) * 3  # Adds three times the value if it's above 97
                count += 3
            else:
                overall += int(stats[s])
                count += 1

    overall = round(((overall / count) + overall_role) / 2)
    overall = extrapolate_overall(overall)  # Extrapolate the rate (moves away from 50 and gets closer to 0 or 100)

    return overall


def extrapolate_overall(overall):
    """
    Extrapolate an overall rate. This makes rates above 50 even better and rates under 50 even worth

    :param overall:
    :return:
    """
    # if rate is above 50 we add to it 1/4 of the distance between the rate and 100
    if overall > 50:
        overall += (100 - overall) / 4

    # if rate is under 50 we subtract to it 1/4 of the distance between the rate and 0
    elif overall < 50:
        overall -= overall / 4

    overall = round(overall)
    # Clamps the value between 0 and 100, should normally never be under or above but it's done by precaution
    overall = max(0, min(overall, 100))

    return overall


def get_overall(player, role):
    """
    Returns for a given player and role, its overall rate and its overall by categories
    (Attack, Defense, Passing, Dribble, Mental)
    :param player: the player we want its overall
    :param role: the role for which we want the player's overall
    :return: the overall rate and a list of the 5 overall by categories
    """

    if player["stats." + role + ".overall"] is None or math.isnan(player["stats." + role + ".overall"]):
        overall = 0
        overall_stats = [0, 0, 0, 0, 0]
    else:
        overall = player["stats." + role + ".overall"]
        overall_stats = [player["stats." + role + ".atk_overall"],
                         player["stats." + role + ".dribble_overall"],
                         player["stats." + role + ".pass_overall"],
                         player["stats." + role + ".mental_overall"],
                         player["stats." + role + ".def_overall"]]

    return round(overall), overall_stats


def get_player_stats(player, role):
    """
    Returns all the stats for a given player and given role
    :param player: the player concerned
    :param role: the role concerned
    :return: the list of stats
    """
    stats_col = [col for col in player.keys() if
                 'stats.' + role in col and "percentile" in col and not math.isnan(player[col])]

    return stats_col


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


def calc_team_overall(my_team, my_team_df):
    """
    Calculate the team overall and its categorical stats by doing mean of all the players
    in the team
    :param my_team: the json of the team
    :param my_team_df: the data frame of the team containing the players
    :return: the overall value, and a list of the overall by categories
    """
    roles = Constants.FORMATIONS[my_team["formation"]]  # Get the list of all the roles in the formation

    team_overall = 0
    team_overall_stats = []

    for index, player in my_team_df.iterrows():
        role = roles[index]
        overall, overall_stats = get_overall(player, role)
        team_overall += overall

        if role != "GK":  # don't add goalie stats as he doesn't have atk, def, pas, or drb stats
            team_overall_stats.append(overall_stats)
    team_overall /= 11  # Divide by 11 to get the mean overall as their is 11 players in a team
    team_overall_stats = np.mean(np.array(team_overall_stats), axis=0)  # Get mean for each stats in array

    return round(team_overall), team_overall_stats


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

        WARNING : this function takes time to run due to pycountry lib search, run this only
        after scrapping but never on dash load otherwise it'll take 10 seconds to start
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


def build_3D_scatter(my_team_df):
    """
    Creates a 3D Scatter plot with x : Attack, y : Defense, z : passing, color : dribble
    :param my_team_df: the dataframe with the players of th team
    :return: the 3D scatter plot
    """
    fig = px.scatter_3d(my_team_df, x="current.atk_overall", y="current.def_overall", z="current.pass_overall",
                        color="current.dribble_overall", color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))  # Removes the default margins

    return fig


def make_my_team_df():
    """
    Creates a data frame containing the team players
    :return: the json file and the df
    """
    # Open json file containing team info and make a df containing the players of the team
    f = open(Constants.MY_TEAM_FILE)
    my_team = json.load(f)
    temp = app.df_all_role[app.df_all_role.id.isin(my_team["players"])]
    team_df = sort_df_by_id(temp, list(my_team["players"]))

    # If for some reason the team isn't complete ( less than 11 players ) we create a random team
    # and call make_my_team_df recursively
    if len(team_df) != 11:
        create_random_team()
        team_df, my_team = make_my_team_df()

    team_df = build_team_category_overall(team_df)

    return team_df, my_team


def sort_df_by_id(df, sorter):
    """
    Sort the data frame by id with a list of id
    :param df: the df to sort
    :param sorter: the list of id
    :return: the df sorted
    """
    sorted_df = df.sort_values(by="id", key=lambda column: column.map(lambda e: sorter.index(e)))
    sorted_df = sorted_df.reset_index(drop=True)
    return sorted_df


def build_team_category_overall(team_df):
    """
    Builds the overall col of the team by categories (Atk, Def, Drb, Pas, Mtl)
    :param team_df: the team_df to append new overall columns to
    :return team_df : the team_df modified
    """
    current_atk_overall = []
    current_def_overall = []
    current_pass_overall = []
    current_dribble_overall = []

    for index, player in team_df.iterrows():
        role = ast.literal_eval(player["roles"])[0]  # Get stats for the best player's role
        current_atk_overall.append(player["stats." + role + ".atk_overall"])
        current_def_overall.append(player["stats." + role + ".def_overall"])
        current_pass_overall.append(player["stats." + role + ".pass_overall"])
        current_dribble_overall.append(player["stats." + role + ".dribble_overall"])

    team_df["current.atk_overall"] = current_atk_overall
    team_df["current.def_overall"] = current_def_overall
    team_df["current.pass_overall"] = current_pass_overall
    team_df["current.dribble_overall"] = current_dribble_overall

    return team_df
