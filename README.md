# Projet-Open-Source-Fbref
Python Projet Data Visualization ESIEE 2022

 - Scraps football player's data from www.fbref.com using beautifullSoup
 - Presents the data in a dashboard using Plotly Dash

## How to Install and Run the Project :

Run main.py to start the app

The data is already scrapped and can be find in [data/player.csv](https://github.com/Gasmain/Projet-Open-Source-Fbref/blob/master/data/player.csv) but it can be rescraped by uncommenting `fb.scrap()` method : 
```Python
if __name__ == '__main__':
    # Config logging output file
    logging.basicConfig(filename='logs/main.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logging.debug('----------- Starting -----------')

    fb.scrap() # <- this line should not be commented if you want to rescrap the data
```






