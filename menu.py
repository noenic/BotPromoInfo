import requests
from bs4 import BeautifulSoup as bs

def majMenu():
    '''
    Retourne un dictionnaire avec les différents menu des jours à venir exemple : 
    {'Menu du mardi 25 octobre 2022': ['Cordon bleu', 'Poisson à la bordelaise', 'Boulette soja tomate', 'Blé pilaf sauce tomate', 'Haricots verts'], 
    'Menu du mercredi 26 octobre 2022': ["Dos de colin d'Alaska sauce basquaise", 'Emincé de porc', 'Purée de potiron', 'Haricots plats'], 
    'Menu du jeudi 27 octobre 2022': ['Poisson meunière', 'Steak haché', 'Frites', 'Brocolis ail/persil']}
    '''
    #Définition de l'URL
    url = 'https://www.crous-bordeaux.fr/restaurant/resto-u-pierre-bidart/'

    #Request get de la page 
    r = requests.get(url)

    soup = bs(r.text, 'html.parser')
    element = soup.select_one('div[id="menu-repas"]')
    jours = element.find_all('h3')
    sElement = element.select('div[class="content clearfix"]')

    tab = []
    for i in range(len(sElement)):
        if(sElement[i].select_one('ul[class="liste-plats"]') != None):
            tab.append(sElement[i].select_one('ul[class="liste-plats"]'))

    dico = {}
    for i in range(len(tab)):
        dico[jours[i].text] = tab[i].select('li')

    for jours in list(dico.keys()):
        tab = []
        for j in range(len(dico[jours])):
            if dico[jours][j].text != "" and dico[jours][j].text != "DESSERT" and dico[jours][j].text != "ENTREE":
                tab.append(dico[jours][j].text)
        dico[jours] = tab

    return(dico)

def menuDuJours(dico):
    '''
    Retourne un tuple (Date, Tableau des différents plats) du jours
    '''
    cle = list(dico.keys())
    return (cle[0], dico[cle[0]])

print(majMenu())