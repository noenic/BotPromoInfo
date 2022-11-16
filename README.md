# Bot CROUS

## Descriptif
Bot Discord qui informe du menu du jour au Restaurant Universitaire Pierre Bidart à Anglet.

## Installation

## Commandes
La liste des commandes est la suivante :

Commande | Description
------------ |  ------------- 
***!menu*** | Donne le menu du jour
***!menuAll*** | Donne les menus de la semaine en cours


## Documentation utile

### Fonction majMenu
Retourne un dictionnaire avec les différents menu des jours à venir exemple : 
```python
{'Menu du mardi 25 octobre 2022': 
['Cordon bleu', 'Poisson à la bordelaise', 'Boulette soja tomate', 'Blé pilaf sauce tomate', 'Haricots verts'], 
'Menu du mercredi 26 octobre 2022': ["Dos de colin d'Alaska sauce basquaise", 'Emincé de porc', 'Purée de potiron', 'Haricots plats'], 
'Menu du jeudi 27 octobre 2022': ['Poisson meunière', 'Steak haché', 'Frites', 'Brocolis ail/persil']}
```

### Fonction menuDuJours
Retourne un tuple (Date, Tableau des différents plats) du jours