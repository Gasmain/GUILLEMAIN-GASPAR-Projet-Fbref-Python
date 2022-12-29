from bs4 import BeautifulSoup
import requests
import logging
import urllib.request
from random import randint
from time import sleep
from tkinter import *
import json
from utils import Constants

data = []


class Scrapper:
    running = False
    progress = 0

    @staticmethod
    def scrap():
        """
        Start the scrapping
        WARNING : Complete scrapping takes a very long time, roughly 5 hours due to the 7 seconds of wait between each
        of the 2000+ players, but it can be stop in it's process without any problem.
        """
        global data
        if not Scrapper.running:
            Scrapper.running = True
            f = open(Constants.PLAYER_FILE_JSON, encoding="utf-8")
            data = json.load(f)

            logging.debug('Starting fbref scrapping')
            player_url_list = Scrapper.get_player_url()

            if len(player_url_list) == 0:
                logging.error('player_url_list is empty')
                return
            else:
                player_list = Scrapper.build_player_list(player_url_list)
        return

    @staticmethod
    def get_player_url():
        """
        Iterate over an html table and extract for each line the link to the players pages
        """
        player_url_list = []
        # Requests the pages with the players table
        r = requests.get(Constants.FBREF_URL + Constants.TOP_5_LEAGUE_PLAYER_LIST, headers=Constants.headers)
        if r.status_code == 200:  # If code = success
            try:
                soup = BeautifulSoup(r.content, 'html.parser')
                player_table = soup.find(id="stats_standard")
                player_table_body = player_table.find("tbody")
                player_table_rows = player_table_body.select(
                    "tr:not(.thead)")  # Get all the rows of the table that are not of class thead
            except:
                logging.error('Could not find the table of players correctly')
                return []  # We stop the run because if the table can't be read we can't go any further

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
            logging.error('Got code ' + str(r.status_code) + " for url : " + Constants.FBREF_URL +
                          Constants.TOP_5_LEAGUE_PLAYER_LIST)

        return player_url_list

    @staticmethod
    def build_player_list(player_url_list):
        """
        Builds a list of players, each one being a json object

        :param player_url_list: list of the urls of the players to create
        :return: list of players (list of json objects)
        """
        global data

        player_list = []

        for player_url in player_url_list:
            player = Scrapper.get_player_data(player_url)  # Build a player
            # Verify if the json is not empty and that the stats and similar player attributes are in the json obj
            if len(player) > 0 and "stats" in player and "similar_players" in player:
                if len(player["stats"]) > 0:
                    player_list.append(player)
                    data.append(player)
                    # save after every new player was scraped, avoid losing scrapped player when script stop before
                    # finishing to scrap all players
                    with open(Constants.PLAYER_FILE_JSON, "w", encoding="utf-8") as file:
                        json.dump(data, file)
                        file.close()
            Scrapper.progress += float(100.0 / len(player_url_list))  # increase the progress after each player was
            # scrapped (for the dash progress bar)
        return player_list

    @staticmethod
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

        :param player_url: url of the player to scrap
        :return: returns the json obj representing the player
        """
        player = {}

        # Requests the player's web pages
        r = requests.get(Constants.FBREF_URL + player_url, headers=Constants.headers)
        if r.status_code == 200:  # If code is success
            try:
                soup = BeautifulSoup(r.content, 'html.parser')

                # Check if player has a scouting report
                if soup.find(id="all_scout") is not None:

                    player, player_id = Scrapper.get_name_id(player, soup, player_url)  # Get player name and id
                    player = Scrapper.get_player_img(soup, player, player_id)  # Download player img
                    player = Scrapper.get_player_foot(soup, player)  # Get player strong foot
                    player = Scrapper.get_height_weight(soup, player)  # Get player height and weight
                    player = Scrapper.get_birthdate(soup, player)  # Get player birthdate
                    player = Scrapper.get_nationality(soup, player)  # Get player nationality
                    player = Scrapper.get_club(soup, player)  # Get player's club
                    player = Scrapper.get_similar_players(soup, player)
                    player = Scrapper.get_stats_roles(soup, player)

                else:  # If player has no scouting report
                    logging.warning("Player has not scouting report : " + Constants.FBREF_URL + player_url)

            except Exception as e:
                logging.error("Error with player : " + Constants.FBREF_URL + player_url + "\n" + str(e))

        else:  # If code = error
            logging.error('Got code ' + str(r.status_code) + " for url : " + Constants.FBREF_URL + player_url)

        sleep(randint(4, 7))  # Sleep a random time between 4 and 7 sec to avoid getting ban by the site

        return player

    @staticmethod
    def extract_id(url):
        """
        Extract from an url the player's id
        :param url: the player's url in string
        :return: player's id in string
        """
        result = re.search(r"\/en\/players\/(.*?)\/", url)  # Search in the url for the player id
        return result.group(1)

    @staticmethod
    def get_name_id(player, soup, player_url):
        """
        add to the player json it's fbref id and its name
        :param player: the json object
        :param soup: soup instance
        :param player_url: the string of the player url
        :return: the json object & the player_id
        """
        player_id = Scrapper.extract_id(player_url)
        player["id"] = player_id

        # ---- Player name ----
        player_name = soup.find("h1").text
        player["name"] = player_name.replace("\n", "")

        return player, player_id

    @staticmethod
    def get_player_img(soup, player, player_id):
        """
        Download and save the player img if one was found
        :param soup: soup instance
        :param player_id: the id of the player, used as a name to save the image
        """
        try:
            player_img_src = soup.find(class_="media-item").find("img")["src"]
            urllib.request.urlretrieve(player_img_src,
                                       Constants.PLAYER_IMG_FOLDER + "/" + player_id + ".jpg")  # Download and save the image in the playerimg folder
            player["img"] = Constants.PLAYER_IMG_FOLDER + "/" + player["id"] + ".jpg"
        except Exception as e:
            player["img"] = Constants.DEFAULT_PLAYER_IMG
            logging.warning("no image found : " + str(e))
            pass

        return player
    @staticmethod
    def get_player_foot(soup, player):
        """
        Adds the the player json it's preferred foot
        :param soup: instance of the soup
        :param player: the player json object
        :return: the player json object
        """
        p_contain_foot = str(soup.select('p:-soup-contains("Footed:")'))  # Find <p> containing "Footed:"
        result = re.search(r".*strong> (.*)<", p_contain_foot)  # Search in the <p> the strong foot

        if result:  # If regex found matches it means player has strong foot
            player["strong_foot"] = result.group(1)
        else:
            player["strong_foot"] = None

        return player

    @staticmethod
    def get_height_weight(soup, player):
        """
        Adds to the player json object it's height and it's weight
        :param soup: instance of soup
        :param player: player json
        :return: player json
        """
        labels = [["height", "cm"], ["weight", "kg"]]

        for l in labels:
            player[l[0]] = None
            p_contain = soup.find(id="meta").select(
                'p:-soup-contains("' + l[
                    1] + '")')  # Search for a <p> containing "cm" or "kg" in the div of the biography
            if len(p_contain) > 0:
                for p in p_contain:
                    result = re.findall(r"(\d*)" + l[1], p.text)  # Search for the height or weight in <p>
                    if len(result) > 0:
                        player[l[0]] = result[0]
                        break
        return player

    @staticmethod
    def get_birthdate(soup, player):
        """
        Adds to the player json it's birthdate
        :param soup: instance of soup
        :param player: player json
        :return: player json
        """
        birth_date = soup.find(id="necro-birth")
        if birth_date == None:
            player["birth_date"] = None
        else:
            player["birth_date"] = birth_date["data-birth"]

        return player

    @staticmethod
    def get_nationality(soup, player):
        """
        Adds to the player json it's nationality and the player flag code
        :param soup: instance of soup
        :param player: player json
        :return: player json
        """
        p_contain_nationality = soup.find(id="meta").select(
            'p:-soup-contains("National Team")')  # Search for a <p> containing "National Team" in the div of the biography
        if len(p_contain_nationality) > 0:
            player["nationality"] = p_contain_nationality[0].find("a").text
        else:
            p_contain_nationality = soup.find(id="meta").select(
                'p:-soup-contains("Citizenship")')  # Search for a <p> containing "Citizenship" in the div of the biography
            if len(p_contain_nationality) > 0:
                player["nationality"] = p_contain_nationality[0].find("a").text
            else:
                player["nationality"] = None

        if p_contain_nationality is not None:
            flag_name = p_contain_nationality[0].find("span")[
                "class"]  # Get the code of the flag (used to get the flag img url
            player["flag_name"] = (''.join(flag_name)).replace("f-if-", "")

        return player

    @staticmethod
    def get_club(soup, player):
        """
        Adds the club and the club id to the json player and download club's logo
        :param soup: instance of soup
        :param player: json player
        :return: json player
        """
        p_contain_club = soup.find(id="meta").select(
            'p:-soup-contains("Club:")')  # Search for a <p> containing "National Team" in the div of the biography
        if len(p_contain_club) > 0:
            player["club"] = p_contain_club[0].find("a").text
            club_url = p_contain_club[0].find("a")["href"]
            result = re.search(r".*\/squads\/(.*)\/", club_url)
            player["club_id"] = result.group(1)
            try:
                urllib.request.urlretrieve(Constants.TEAM_LOGO_URL + result.group(1) + ".png",
                                           Constants.TEAM_IMG_FOLDER + "/" + player[
                                               "club_id"] + ".png")  # Download and save the image in playerimg
            except Exception as e:
                logging.warning("no image club found : " + str(e))
                pass

        else:
            player["club"] = None

        return player

    @staticmethod
    def get_similar_players(soup, player):
        """
        Adds a list of id of similar players in th player json
        :param soup: instance of soup
        :param player: player json
        :return: player json
        """
        similar_table = soup.find(id="all_similar")  # Get the table containing the similar player
        # only get rows with players
        similar_table_row = similar_table.find_all("td", {"class": "left", "data-stat": "player"})
        similar_players = []
        for row in similar_table_row:
            similar_players.append(Scrapper.extract_id(row.find("a")["href"]))  # Get the id from the player's url
        player["similar_players"] = similar_players

        return player

    @staticmethod
    def get_stats_roles(soup, player):
        """
        Adds to the json player it's stats and roles.
        For each roles its corresponding stats.
        Ex : roles = ["AM", "MF"] and stats = {"AM" : {...}, "MF" : {...}}
        :param soup: instance of soup
        :param player: player json
        :return: player json
        """
        # Get the tables containing the stats (one per role)
        all_scout = soup.find_all(id="all_scout")[1]
        all_table = all_scout.find_all("table")

        players_stats = {}
        player_roles = []

        for table in all_table:
            stats = {}

            result = re.search(r".*full_(.*)", table["id"])
            role = result.group(1)  # Get the role concerning the table

            player_roles.append(role)

            # Get all the rows of the stat table
            all_scout_table_body = table.find("tbody")
            all_scout_rows = all_scout_table_body.find_all("tr")

            for row in all_scout_rows:
                # determine if row is a stat row or a spacer row
                if row.has_attr("class"):
                    if "spacer" in row["class"] or "thead" in row["class"]:
                        continue

                # Extract name of the stats from th where attribute data-stat = statistic
                stat_name = row.find("th", {"data-stat": "statistic"}).text
                # Extract name of the stats from th where attribute data-stat = per90
                stats[stat_name + "_per90"] = row.find("td", {"data-stat": "per90"}).text
                # Extract name of the stats from th where attribute data-stat = percentile
                stats[stat_name + "_percentile"] = row.find("td", {"data-stat": "percentile"})["csk"]

            players_stats[role] = stats

        player["stats"] = players_stats
        player["roles"] = player_roles

        return player
