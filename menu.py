import requests
from bs4 import BeautifulSoup as bs

def majMenu():
    return {}
    url = 'https://www.crous-bordeaux.fr/restaurant/resto-u-pierre-bidart/'

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
    cle = list(dico.keys())
    return (cle[0], dico[cle[0]])

print(majMenu())