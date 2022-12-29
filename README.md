# Projet-Open-Source-Fbref
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/) <br>
Python Projet Data Visualization ESIEE 2022

[I. Présentation](#presentation)<br>
[II. Le projet](#project)<br>
[III. Analyses et conclusions](#conclusion)<br>
[IV. Guide utilisateur (Install & Run)](#user-guide)<br>
[V. Guide developpeur](#dev-guide)<br>

<a name="presentation"/>

## I. Présentation :

Le football est un sport passionnant et très populaire à travers le monde, avec des millions de fans et de nombreux joueurs. Les performances de ces joueurs peuvent être cruciales pour le succès d'une équipe, et il est donc important de pouvoir les évaluer de manière objective.
J'ai créé un dashboard avec des données publiques de joueurs de football provenant de [fbref.com](https://fbref.com/en/) en utilisant Python et dash. Le dashboard offre une vue d'ensemble détaillée des performances des joueurs de football et permet aux utilisateurs de comprendre les qualités et défauts de chaque joueur et leur impact sur l'équipe.

<a name="project"/>

## II. Le projet :

<a name="conclusion"/>

## III. Analyses et conclusions :

<a name="user-guide"/>

## IV. Guide utilisateur :

  > :warning: **Ce projet a été créé avec python 3.9 mais devrait fonctionner pour toutes versions de python 3, si cela n'est pas le cas, utilisez python 3.9**

- **Premièrement, installez les dependances :**

  `$ pip install -r requirements.txt`

- **Puis lancez main.py pour demarrer l'app :**

  `$ python main.py`

- **Enfin, ouvrez le dashboard**

  visitez http://127.0.0.1:8050/ dans votre navigateur pour visualiser le dashboard


<a name="dev-guide"/>

## V. Guide developpeur :


  Les data ont déja été scrappé pour un gain de temps et peuvent être trouvées ici : [data/player.json](https://github.com/Gasmain/Projet-Open-Source-Fbref/blob/master/data/player.json) mais peuvent être rescrappé via l'interface ou en rajoutant `Scrapper.scrap()` dans le main : 
  > :warning: **Le scrapping de données est très long** : il peut prendre plus de 5h
  
  ```Python
  if __name__ == '__main__':
      # Config logging output file
      logging.basicConfig(filename='logs/main.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

      Scrapper.scrap() # <- cette ligne doit être présente si vous voulez scrapper avant de lancer le dashboard
  ```
 







