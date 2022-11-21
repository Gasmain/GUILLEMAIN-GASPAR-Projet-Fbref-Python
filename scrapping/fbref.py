import re
import json
from bs4 import BeautifulSoup
import requests
import logging
import urllib.request
from random import randint
from time import sleep
from tkinter import *
from tkinter.ttk import *
import asyncio
from threading import Thread

PLAYER_FILE_CSV = "data/player.csv"
PLAYER_FILE_JSON = "data/player.json"
PLAYER_IMG_FOLDER = "data/playerimg"
FBREF_URL = "https://fbref.com"
TOP_5_LEAGUE_PLAYER_LIST = "/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats"
headers={
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Host":"fbref.com",
    "Referer":"https://fbref.com/en/players/",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
}
data = []
progress = 0
stop_threads = False;




def scrap():
    global data
    t = Thread(target=progress_bar)
    t.start()
    f = open(PLAYER_FILE_JSON)
    data = json.load(f)

    logging.debug('Starting fbref scrapping')
    player_url_list = get_player_url()

    if len(player_url_list) == 0:
        logging.error('player_url_list is empty')
        print("error : player_url_list is empty")
        return
    else:
        player_list = build_player_list(player_url_list)
    stop_threads = True
    t.join()
    return


def progress_bar():
    global progress, stop_threads
    window = Tk()
    window.wm_title("Scrapping progress")
    window.geometry("400x200")
    text = Label(window, text="0")
    text.place(x=180,y=90)
    bar = Progressbar(window, orient=HORIZONTAL, length=300)
    bar.pack(pady=50)

    while True:
        bar["value"] = progress
        text.config(text=str(round(progress, 2))+"%")
        window.update()
        if stop_threads:
            break


def get_player_url():
    """
    Iterate over an html table and extract for each line the link to the players page
    """

    player_url_list = []

    r = requests.get(FBREF_URL + TOP_5_LEAGUE_PLAYER_LIST, headers=headers)  # Requests the page with the players table
    if r.status_code == 200:  # Si code = success
        try:
            soup = BeautifulSoup(r.content, 'html.parser')
            player_table = soup.find(id="stats_standard")
            player_table_body = player_table.find("tbody")
            player_table_rows = player_table_body.select(
                "tr:not(.thead)")  # Get all the rows of the table that are not of class thead
        except:
            logging.error('Could not find the table of players correctly')
            print("error : Could not find the table of players correctly")
            exit()  # We stop the run because if the table can't be read we can't go any further

        for row in player_table_rows:
            try:
                player_url = row.find_all("td")[0].find("a")['href']  # Get link of the player
                # Rebuilding the url to get the player scouting report
                result = re.search(r"(.*)\/", player_url)  # Search in the url for the part without the player name
                player_url = result.group(1) + "/scout/365_m1/"
                player_url_list.append(player_url)
            except:
                pass

        player_url_list = list(dict.fromkeys(player_url_list))  # Drop duplicate urls

    else:  # Si code = error
        print("error : Got code " + str(r.status_code) + " for url : " + FBREF_URL + TOP_5_LEAGUE_PLAYER_LIST)
        logging.error('Got code ' + str(r.status_code) + " for url : " + FBREF_URL + TOP_5_LEAGUE_PLAYER_LIST)

    return player_url_list


def build_player_list(player_url_list):
    """
    Builds a list of players, each one being a json object
    """
    global data, progress
    player_list = []
    for player_url in player_url_list:
        player = get_player_data(player_url)
        if len(player)>0:
            if "stats" in player and "similar_players" in player: #Checks if the stats and sim player key exist in player dict before adding to list
                player_list.append(player)
                data.append(player)
                with open(PLAYER_FILE_JSON, "w") as file:
                    json.dump(data, file)
        progress += float(100.0/len(player_url_list))
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

    r = requests.get(FBREF_URL + player_url, headers=headers)  # Requests the player's web page'
    if r.status_code == 200:  # If code = success


        try:
            soup = BeautifulSoup(r.content, 'html.parser')

            # Check if player has a scouting report
            if soup.find(id="all_scout") is not None:

                # ---- Player id ----

                player_id = extractId(player_url)
                player["id"] = player_id

                # ---- Player name ----
                player_name = soup.find("h1").text
                player["name"] = player_name.replace("\n", "")

                # ---- Player img ----
                try:
                    player_img_src = soup.find(class_="media-item").find("img")["src"]
                    urllib.request.urlretrieve(player_img_src,
                                               PLAYER_IMG_FOLDER + "/" + player_id + ".jpg")  # Download and save the image in the playerimg folder
                except Exception as e:
                    print("no image found : " + str(e))
                    pass

                # ---- Player strong foot ----
                p_contain_foot = str(soup.select('p:-soup-contains("Footed:")'))  # Find <p> containing "Footed:"
                result = re.search(r".*strong> (.*)<", p_contain_foot)  # Search in the <p> the strong foot

                if result:  # If regex found matches it means player has strong foot
                    player["strong_foot"] = result.group(1)
                else :
                    player["strong_foot"] = None

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

                # ---- Player birthdate ----
                birth_date = soup.find(id="necro-birth")
                if birth_date == None :
                    player["birth_date"] = None
                else:
                    player["birth_date"] = birth_date["data-birth"]

                # Player nationality
                p_contain_nationality = soup.find(id="meta").select('p:-soup-contains("National Team")')  # Search for a <p> containing "National Team" in the div of the biography
                if len(p_contain_nationality) > 0:
                    player["nationality"] = p_contain_nationality[0].find("a").text
                else :
                    player["nationality"] = None

                # Player club
                p_contain_club = soup.find(id="meta").select('p:-soup-contains("Club:")')  # Search for a <p> containing "National Team" in the div of the biography
                if len(p_contain_club) > 0:
                    player["club"] = p_contain_club[0].find("a").text
                else :
                    player["club"] = None

                # Similar players
                similar_table = soup.find(id="all_similar")
                similar_table_row = similar_table.find_all("td", {"class": "left", "data-stat": "player"})
                similar_players = []
                for row in similar_table_row:
                    similar_players.append(extractId(row.find("a")["href"]))
                player["similar_players"] = similar_players
                # Player stats
                all_scout = soup.find_all(id="all_scout")[1]
                all_scout_table_body = all_scout.find("tbody")
                all_scout_rows = all_scout_table_body.find_all("tr")

                players_stats = []
                for row in all_scout_rows:
                    stat = {}
                    if row.has_attr("class"):
                        if("spacer" in row["class"] or "thead" in row["class"]):
                            continue
                    stat["name"] = row.find("th",{"data-stat": "statistic"}).text
                    stat["per90"] = row.find("td",{"data-stat": "per90"}).text
                    stat["percentile"] = row.find("td",{"data-stat": "percentile"})["csk"]
                    players_stats.append(stat)
                player["stats"] = players_stats


            else:  # If player has no scouting report
                logging.warning("Player has not scouting report : " + FBREF_URL + player_url)

        except Exception as e:
            logging.error("Error with player : " + FBREF_URL + player_url + "\n" + str(e))
            print("error : Error with player : " + FBREF_URL + player_url + "\n" + str(e))


    else:  # If code = error
        logging.error('Got code ' + str(r.status_code) + " for url : " + FBREF_URL + player_url)
        print("error : Got code " + str(r.status_code) + " for url : " + FBREF_URL + player_url)

    sleep(randint(4, 7))

    return player


def extractId(url):
    result = re.search(r"\/en\/players\/(.*?)\/", url)  # Search in the url for the player id
    return result.group(1)
