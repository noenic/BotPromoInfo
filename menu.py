import requests
from bs4 import BeautifulSoup

url = 'https://www.crous-bordeaux.fr/restaurant/resto-u-pierre-bidart/'

r = requests.get(url)

soup = BeautifulSoup(r.text)
elementMenu = soup.find("inner")

print(elementMenu)
