import json
import pandas as pd

PLAYER_FILE_JSON = "data/player.json"
PLAYER_FILE_CSV = "data/player.csv"
PLAYER_FILE_CSV2 = "data/player2.csv"


class Database:
    df_role = None
    df_best_pos = None;

    def __init__(self):
        self.df_role, self.df_best_pos = self.build_data_frame()

    def build_data_frame(self):
        print("Building data")
        f = open(PLAYER_FILE_JSON)
        data = json.load(f)
        df_role = pd.json_normalize(data)
        for player in data:
            best_pos_stats = player["stats"][list(player["stats"].keys())[0]]
            player.pop('stats', None)
            player["stats"] = best_pos_stats
        df_best_pos = pd.json_normalize(data)
        return df_role, df_best_pos

