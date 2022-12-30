PLAYER_ALL_ROLE_FILE_CSV = "data/player_all_role.csv"
PLAYER_BEST_ROLE_FILE_CSV = "data/player_best_role.csv"
PLAYER_FILE_JSON = "data/player.json"
TEAM_LOGO_URL = "https://cdn.ssref.net/req/202211181/tlogo/fb/"
FBREF_URL = "https://fbref.com"
TOP_5_LEAGUE_PLAYER_LIST = "/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Host": "fbref.com",
    "Referer": "https://fbref.com/en/players/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
}
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
                    "Touches": 4, "Offsides": 4, "Crosses": 6, "Successful Dribble %": 6, "Dribbles Completed": 6, }
MF_OVERALL_STATS = {"Goals": 3, "Assists": 6, "Pass Completion %": 8, "Key Passes": 8, "Goal-Creating Actions": 6,
                    "Touches": 5, "Successful Dribble %": 4, "Dribbles Completed": 4, "Passes into Final Third": 5,
                    "Progressive Passe": 5,
                    "Tackles Won": 5,
                    }
GK_OVERALL_STATS = {"PSxG-GA": 9, "Save% (Penalty Kicks)": 7, "Save Percentage": 5, "Crosses Stopped %": 5,
                    "Pass Completion Percentage (Launched)": 4,
                    }
error_countries = {"Congo DR": "COD", "Republic of Ireland": "IRL","Korea Republic":"South Korea"}
no_countries = ["Cape Verde"]
DEFAULT_PLAYER_IMG = "/assets/default.jpg"
FORMATIONS = {"442": ["GK", "CB", "CB", "FB", "FB", "MF", "MF", "AM", "AM", "FW", "FW"],
              "433": ["GK", "CB", "CB", "FB", "FB", "MF", "MF", "MF", "AM", "AM", "FW"]}
MY_TEAM_FILE = "data/my_team.json"
MAP_CSV = "data/map.csv"
MY_LOGO = "assets/football.png"
LOGS_FILE = 'logs/main.log'
DEFAULT_TEAM_IMG = "/assets/default_team.png"
FLAG_URL = "https://cdn.ssref.net/req/1637611918233-20211022/flags/"
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
NODE_STYLE = [
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
PLAYER_IMG_URL = "https://fbref.com/req/202208180/images/headshots/player_id_2022.jpg"
CLUB_IMG_URL = "https://cdn.ssref.net/req/202212191/tlogo/fb/club_id.png"