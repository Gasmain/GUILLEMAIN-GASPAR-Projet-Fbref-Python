import app
import scrapping.fbref as fbref
import logging


if __name__ == '__main__':
    # Config logging output file
    logging.basicConfig(filename='logs/main.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logging.debug('----------- Starting -----------')
    #fbref.scrap()
    fbref.build_data_frame()
    app.create()
