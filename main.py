import os.path

import app
import scrapping.fbref as fbref
import logging
from utils import simple_functions as sf

if __name__ == '__main__':
    # Config logging output file
    logging.basicConfig(filename='logs/main.log', level=logging.CRITICAL, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logging.debug('----------- Starting -----------')
    #fbref.scrap()
    #sf.temp()

    sf.build_data_frame()
    if not os.path.exists("data/my_team.json"):
        sf.create_random_team()
    app.create()
