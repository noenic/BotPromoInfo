import requests
from bs4 import BeautifulSoup as bs

url = 'https://www.crous-bordeaux.fr/restaurant/resto-u-pierre-bidart/'
r = requests.get(url)
soup = bs(r.text, 'html.parser')
element = soup.select_one('div[id="menu-repas"]')
jours = element.select('h3')
sElement = element.select('div[class="content clearfix"]')
tab = []
for i in range(len(sElement)):
    tab.append(sElement[i].select_one('ul[class="liste-plats"]'))
print(tab)


