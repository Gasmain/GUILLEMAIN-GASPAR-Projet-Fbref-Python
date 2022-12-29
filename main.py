import os.path
import app
import logging
from scrapping.fbref import Scrapper
from utils import shared_functions as sf, Constants

if __name__ == '__main__':
    # Config logging output file
    logging.basicConfig(filename=Constants.LOGS_FILE, level=logging.CRITICAL,
                        format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # TODO : treat the callback error
    # TODO : avoid duplicates when scrapping

    sf.build_data_frame()  # converts the .json file in dataframe, recalculate overall (useful if json changed)
    if not os.path.exists(Constants.MY_TEAM_FILE):  # Creates a random team if no team file was found
        sf.create_random_team()
    app.create()  # Runs the dash app
