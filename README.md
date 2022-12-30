# Projet-Open-Source-Fbref
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/) <br>
Python Projet Data Visualization ESIEE 2022 <br>
Ce projet à été importé de mon git perso : https://github.com/Gasmain/Projet-Open-Source-Fbref/
Seuls les commits sont donc visibles mais pas les pushs

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

Le but de ce projet était de créer un dashboard en utilisant Python qui permettrait d'analyser et de mettre en valeur des données publiques Open Data sur un sujet d'intérêt public. Le code devait être structuré en plusieurs fichiers et exécuté dans un navigateur. Au minimum, le dashboard devait inclure un histogramme et une représentation géolocalisée, ainsi qu'au moins un graphique dynamique. <br>

J'ai choisi de travailler avec des données footballistiques provenant de bref, qui répertorient les statistiques de joueurs de cinq des plus grands championnats sur les 365 derniers jours. J'ai utilisé la bibliothèque Plotly Dash pour créer un dashboard qui permettrait de manipuler ces données et de les rendre plus accessibles. <br>

Le dashboard final comprend quatre pages, chacune ayant sa propre fonctionnalité : <br>

  - La page d'accueil présente un histogramme et une carte choroplèthe permettant de visualiser la répartition géographique des joueurs. Elle inclut également un scatter plot
  dynamique qui affiche les statistiques de chaque joueur ainsi qu’un histogram dynamique. <br>
  
  - La page joueur permet aux utilisateurs de rechercher un joueur en particulier et d'afficher ses informations et ses statistiques. Elle inclut également un graphique en
  forme de radar qui présente une note de défense, d'attaque, de dribble, de passe et de mental pour chaque joueur et un graphique camembert revisité pour afficher la note
  totale du joueur. <br>
  
  - La page squad builder permet aux utilisateurs de créer une équipe en sélectionnant des joueurs scrappés. Un dash cytoscape est utilisé pour représenter chaque joueur sous
  forme de nœud, et les liens entre les nœuds représentent la compatibilité entre les joueurs. La page inclut également un radar et une note générale. <br>

  - La page scrapping permet de lancer le scrapping des données pour mettre à jour les informations du dashboard. <br>
  

**Graphiques utilisés:**

  - Scatter Plot ( Dynamique )
  - Historgram ( Dynamique )
  - Carte Choroplèthe
  - Graph Radar ( Dynamique )
  - Camembert / Pie ( Dynamique )
  - Dash Cytoscape ( Dynamique )




<a name="conclusion"/>

## III. Analyses et conclusions :

<a name="user-guide"/>

## IV. Guide utilisateur :

  > :warning: **Ce projet a été créé avec python 3.9 mais devrait fonctionner pour toutes versions de python 3, si cela n'est pas le cas, utilisez python 3.9**
  
- **Premièrement, clonez le repo :**

  `$ git clone https://github.com/Gasmain/Projet-Open-Source-Fbref.git`

- **Ensuite, installez les dependances :**

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
 







