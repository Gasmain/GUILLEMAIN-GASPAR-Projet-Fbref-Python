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

PLAYER_ALL_ROLE_FILE_CSV = "data/player_all_role.csv"
PLAYER_BEST_ROLE_FILE_CSV = "data/player_best_role.csv"
PLAYER_FILE_JSON = "data/player.json"
PLAYER_IMG_FOLDER = "assets/playerimg"
TEAM_IMG_FOLDER = "assets/teamimg"
TEAM_LOGO_URL = "https://cdn.ssref.net/req/202211181/tlogo/fb/"
FBREF_URL = "https://fbref.com"
TOP_5_LEAGUE_PLAYER_LIST = "/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Host": "fbref.com",
    "Referer": "https://fbref.com/en/players/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
}
data = []

ATK_OVERALL_STATS = {"Goals": 5, "Shots on target %": 2, "Non-Penalty Goals - npxG": 4, "xG": 3}
DRB_OVERALL_STATS = {"Successful Dribble %": 5, "Dribbles Completed": 4, "Dispossessed": 2, "Miscontrols": 3,
                     "Touches": 2, "Goal-Creating Actions": 2}
DEF_OVERALL_STATS = {"Tackles Won": 3, "% of dribblers tackled": 5, "Dribbled Past": 3, "Blocks": 3, "Interceptions": 3}
PASS_OVERALL_STATS = {"Passes Completed": 3, "Pass Completion %": 4, "Assists": 5, "Key Passes": 4,
                      "Progressive Passes": 3}
MENTAL_OVERALL_STATS = {"Red Cards": 4, "Yellow Cards": 2, "Fouls Committed": 2, "Own Goals": 4, "Errors": 2}

FB_OVERALL_STATS = {"Goals": 2, "Assists": 8, "Red Cards": 3, "Pass Completion %": 6, "Expected Assists": 8,
                    "Key Passes": 7, "Crosses into Penalty Area": 5, "Progressive Passes": 5,
                    "Shot-Creating Actions": 5, "Goal-Creating Actions": 6, "% of dribblers tackled": 5,
                    "Tackles Won": 5, "Dribbled Past": 4, "Blocks": 4, "Interceptions": 5, "Successful Dribble %": 5,
                    "Dribbles Completed": 5, "Dispossessed": 5, "Progressive Passes Rec": 4, "Miscontrols": 4}
CB_OVERALL_STATS = {"Goals": 2, "Red Cards": 3, "Pass Completion %": 5, "Progressive Passes": 4,
                    "% of dribblers tackled": 5, "Dribbled Past": 5, "Pass Completion % (Long)": 4, "Tackles Won": 3,
                    "Interceptions": 3, "Blocks": 3, "% of Aerials Won": 4, "Penalty Kicks Conceded": 4, "Touches": 7,
                    "Miscontrols": 5}
FW_OVERALL_STATS = {"Goals": 10, "Assists": 6, "Red Cards": 2, "Goals - xG": 7, "xG": 6, "Shots on target %": 5,
                    "Pass Completion %": 5, "Key Passes": 5, "Goal-Creating Actions": 5, "Dispossessed": 4,
                    "Touches": 4, "Offsides": 4}
AM_OVERALL_STATS = {"Goals": 7, "Assists": 7, "Goals - xG": 7, "xG": 6, "Shots on target %": 5,
                    "Pass Completion %": 5, "Key Passes": 7, "Goal-Creating Actions": 7, "Dispossessed": 5,
                    "Touches": 4, "Offsides": 4, "Crosses": 6,"Successful Dribble %": 6,"Dribbles Completed": 6,}
MF_OVERALL_STATS = {"Goals": 3, "Assists": 6,"Pass Completion %": 8, "Key Passes": 8, "Goal-Creating Actions": 6,
                    "Touches": 5, "Successful Dribble %": 4,"Dribbles Completed": 4, "Passes into Final Third": 5,"Progressive Passe": 5,
                    "Tackles Won": 5,
                    }
GK_OVERALL_STATS = {"PSxG-GA":9, "Save% (Penalty Kicks)":7, "Save Percentage":5, "Crosses Stopped %":5, "Pass Completion Percentage (Launched)":4,
                    }


error_countries = {"Congo DR": "COD", "Republic of Ireland":"IRL"}
no_countries = ["Cape Verde"]

DEFAULT_PLAYER_IMG = "/assets/default.jpg"

FORMATIONS = {"442": ["GK", "CB", "CB", "FB", "FB", "MF", "MF", "AM", "AM", "FW", "FW"],
              "433": ["GK", "CB", "CB", "FB", "FB", "MF", "MF", "MF", "AM", "AM", "FW"]}


def build_data_frame():
    f = open(PLAYER_FILE_JSON)
    data_json = json.load(f)

    for player in data_json:
        for role in player["roles"]:
            if role == "CB":
                stat_list = CB_OVERALL_STATS
            if role == "FB":
                stat_list = FB_OVERALL_STATS
            if role == "FW":
                stat_list = FW_OVERALL_STATS
            if role == "AM":
                stat_list = AM_OVERALL_STATS
            if role == "GK":
                stat_list = GK_OVERALL_STATS
            if role == "MF":
                stat_list = MF_OVERALL_STATS

            overall = 0

            overall = calc_overall(player, role, stat_list)

            player["stats"][role].update({"overall": overall})
            if role != "GK":
                player["stats"][role].update({"atk_overall": calc_overall(player, role, ATK_OVERALL_STATS)})
                player["stats"][role].update({"dribble_overall": calc_overall(player, role, DRB_OVERALL_STATS)})
                player["stats"][role].update({"pass_overall": calc_overall(player, role, PASS_OVERALL_STATS)})
                player["stats"][role].update({"mental_overall": calc_overall(player, role, MENTAL_OVERALL_STATS)})
                player["stats"][role].update({"def_overall": calc_overall(player, role, DEF_OVERALL_STATS)})
            else:
                player["stats"][role].update({"atk_overall": 0})
                player["stats"][role].update({"dribble_overall": 0})
                player["stats"][role].update({"pass_overall": 0})
                player["stats"][role].update({"mental_overall": 0})
                player["stats"][role].update({"def_overall": 0})

    df_role = pd.json_normalize(data_json)

    for player in data_json:
        best_pos_stats = player["stats"][list(player["stats"].keys())[0]]
        player.pop('stats', None)
        player["stats"] = best_pos_stats
        best_pos_rol = player["roles"][0]
        player.pop('roles', None)
        player["roles"] = best_pos_rol




    df_best_pos = pd.json_normalize(data_json)
    df_best_pos.to_csv(PLAYER_BEST_ROLE_FILE_CSV, encoding='utf-8', index=False)
    df_role.to_csv(PLAYER_ALL_ROLE_FILE_CSV, encoding='utf-8', index=False)


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
    my_team = {}
    key, value = random.choice(list(FORMATIONS.items()))
    my_team["formation"] = key
    players = []
    for role in value:
        f = open(PLAYER_FILE_JSON)
        data_json = json.load(f)
        player_role = ""
        while (role not in player_role):
            value = random.choice(data_json)
            player_role = value["roles"]
        players.append(value["id"])
    my_team["players"] = players
    with open("data/my_team.json", "w", encoding="utf-8") as file:
        json.dump(my_team, file)


def temp():
    f = open(PLAYER_FILE_JSON)
    data_json = json.load(f)
    for player in data_json:
        if os.path.exists(PLAYER_IMG_FOLDER + "/" + player["id"] + ".jpg"):
            player_img = PLAYER_IMG_FOLDER + "/" + player["id"] + ".jpg"

        else:
            player_img = DEFAULT_PLAYER_IMG
        player["img"] = player_img

    with open(PLAYER_FILE_JSON, "w", encoding="utf-8") as file:
        json.dump(data_json, file)


def calculate_age(born):
    birth = datetime.strptime(born, '%Y-%m-%d')
    today = date.today()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return str(age)


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
    if not math.isnan(player["height"].iloc[0]) and not math.isnan(player["weight"].iloc[0]):
        player_physique = str(int(player["height"].iloc[0])) + ' cm | ' + str(int(player["weight"].iloc[0])) + " kg"
    elif not math.isnan(player["height"].iloc[0]):
        player_physique = str(int(player["height"].iloc[0])) + ' cm'
    elif not math.isnan(player["weight"].iloc[0]):
        player_physique = str(int(player["weight"].iloc[0])) + " kg"
    else:
        player_physique = ""
    return player_physique


def build_overall_radar(overall_stats, size=200):
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
    overall_pie = go.Figure(data=[go.Pie(labels=["progress", "rest"], values=[overall, 100 - overall], hole=0.85,
                                         marker=dict(colors=['#6265F0', '#D7DEE5']), direction='clockwise',
                                         sort=False)])
    overall_pie.update(layout_showlegend=False)
    overall_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=75, width=75)
    overall_pie.update_traces(textinfo='none', hoverinfo='skip', hovertemplate=None)
    return overall_pie


def build_map_csv():
    nations = {}

    for index, player in app.df_best_role.iterrows():
        code = ""
        country = ""
        if player["nationality"] in error_countries :
            code = error_countries[player["nationality"]]
            country = player["nationality"]
        elif player["nationality"] in no_countries:
            print("skipped : " + player["nationality"])
            continue
        else :
            result = pycountry.countries.search_fuzzy(player["nationality"])
            code = result[0].alpha_3
            country = result[0].name

        if code not in nations:
            nations[code] = {"player_nb":1, "name":country}
        else :
            nations[code]["player_nb"] += 1

    nation_df = pd.DataFrame.from_dict(nations, orient='index')
    nation_df["code"] = nation_df.index
    nation_df.rename(columns={0: 'player_nb'}, inplace=True)
    nation_df = nation_df.reset_index(drop=True)
    nation_df.to_csv("data/map.csv", encoding='utf-8', index=False)