import re
from typing import List, Any
import json
from bs4 import BeautifulSoup
import requests
import logging
import urllib.request

PLAYER_FILE_CSV = "data/player.csv"
PLAYER_FILE_JSON = "data/player.json"
PLAYER_IMG_FOLDER = "data/playerimg"
FBREF_URL = "https://fbref.com"
TOP_5_LEAGUE_PLAYER_LIST = "/en/comps/Big5/stats/joueurs/Statistiques-Les-5-grands-championnats-europeens"


def scrap():
    logging.debug('Starting fbref scrapping')
    player_url_list = get_player_url()

    if len(player_url_list) == 0:
        logging.error('player_url_list is empty')
        print("error")
        return
    else:
        player_list = build_player_list(player_url_list)
        with open("PLAYER_FILE_JSON", "w") as file:
            json.dump(player_list, file)


    return


def get_player_url():
    """
    Iterate over an html table and extract for each line the link to the players page
    """

    player_url_list = []

    r = requests.get(FBREF_URL + TOP_5_LEAGUE_PLAYER_LIST)  # Requests the page with the players table
    if r.status_code == 200:  # Si code = success
        try:
            soup = BeautifulSoup(r.content, 'html.parser')
            player_table = soup.find(id="stats_standard")
            player_table_body = player_table.find("tbody")
            player_table_rows = player_table_body.select(
                "tr:not(.thead)")  # Get all the rows of the table that are not of class thead
        except:
            logging.error('Could not find the table of players correctly')
            print("error")
            exit()  # We stop the run because if the table can't be read we can't go any further

        for row in player_table_rows:
            try:
                player_url = row.find_all("td")[0].find("a")['href']  # Get link of the player
                # Rebuilding the url to get the player scouting report
                result = re.search(r"(.*)\/", player_url)  # Search in the url for the part without the player name
                player_url = result.group(1) + "/scout/365_euro/"
                player_url_list.append(player_url)
            except:
                pass

        player_url_list = list(dict.fromkeys(player_url_list))  # Drop duplicate urls

    else:  # Si code = error
        print("error")
        logging.error('Got code ' + r.status_code + " for url : " + FBREF_URL + TOP_5_LEAGUE_PLAYER_LIST)

    return player_url_list


def build_player_list(player_url_list):
    """
    Builds a list of players, each one being a json object
    """

    player_list = []

    for player_url in player_url_list:
        player = get_player_data(player_url)
        player_list.append(player)

    return player_list


def get_player_data(player_url):
    """
    Gather the player's data such as his name, nationality ...
    and parse all his stats from the extended scouting report

    {
    "name" : "Neymar",
    "age" : 28,
    ...
    "stats" : {}
    }

    """

    player = {}

    r = requests.get(FBREF_URL + player_url)  # Requests the player's web page'
    if r.status_code == 200:  # If code = success


        try:
            soup = BeautifulSoup(r.content, 'html.parser')

            # Check if player has a scouting report
            if soup.find(id="all_scout") is not None:

                # ---- Player id ----
                result = re.search(r"\/en\/players\/(.*?)\/", player_url)  # Search in the url for the player id
                player_id = result.group(1)
                player["id"] = player_id

                # ---- Player name ----
                player_name = soup.find("h1").text
                player["name"] = player_name

                # ---- Player img ----
                try:
                    player_img_src = soup.find(class_="media-item").find("img")["src"]
                    urllib.request.urlretrieve(player_img_src,
                                               PLAYER_IMG_FOLDER + "/" + player_id + ".jpg")  # Download and save the image in the playerimg folder
                except:
                    pass

                # ---- Player strong foot ----
                p_contain_foot = str(soup.select('p:-soup-contains("Footed:")'))  # Find <p> containing "Footed:"
                result = re.findall(r".*Footed:<\/strong>(.*?)%(.*?)<.*", p_contain_foot)  # Search in the <p> the strong foot, and it's percentage

                if len(result) > 0:  # If regex found matches it means player has strong foot and percentage
                    strong_foot_percentage = result[0][0]
                    strong_foot = result[0][1]
                else :
                    result = re.findall(r".*Footed:<\/strong>(.*?)<.*", p_contain_foot)  # Search in the <p> the strong foot only
                    if len(result) > 0:  # If regex found matches it means player has only strong foot
                        strong_foot_percentage = None
                        strong_foot = result[0][0]
                    else: # If regex didn't find anything it means player has no strong foot data
                        strong_foot_percentage = None
                        strong_foot = None

                player["strong_foot"] = {"foot": strong_foot, "percentage": strong_foot_percentage}

                # ---- Player height ----
                player["height"] = None
                p_contain_height = soup.find(id="meta").select('p:-soup-contains("cm")')  # Search for a <p> containing "cm" in the div of the biography
                if len(p_contain_height) > 0 :
                    for p in p_contain_height:
                        result = re.findall(r"(\d*)cm", p.text)  # Search for the height in <p>
                        if len(result) > 0 :
                            player["height"] = result[0]
                            break

                # ---- Player weight ----
                player["weight"] = None
                p_contain_weight = soup.find(id="meta").select('p:-soup-contains("kg")')  # Search for a <p> containing "kg" in the div of the biography
                if len(p_contain_weight) > 0:
                    for p in p_contain_weight:
                        result = re.findall(r"(\d*)kg", p.text)  # Search for the weight in <p>
                        if len(result) > 0:
                            player["weight"] = result[0]
                            break
                print(player["weight"])
                
                # ---- Player age ----
                p_contain_born = soup.select('p:-soup-contains("Born:")')  # Find <p> containing "Born:"
                #if len(p_contain_height) > 0 :


                # Player nationality
                # Player club
                # Similar players
                # Player stats

            else:  # If player has no scouting report
                logging.warning("Player has not scouting report : " + FBREF_URL + player_url)

        except Exception as e:
            logging.error("Error with player : " + FBREF_URL + player_url + "\n" + str(e))
            print("error")


    else:  # If code = error
        logging.error('Got code ' + r.status_code + " for url : " + FBREF_URL + player_url)
        print("error")

    return player
