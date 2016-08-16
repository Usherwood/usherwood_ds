__author__ = "Peter J Usherwood"

import requests
from bs4 import BeautifulSoup

r = requests.get("https://www.premierleague.com/players/4525/Philippe-Coutinho/stats")
soup = BeautifulSoup(r.text, 'html.parser')
#print(soup.get_text())

for link in soup.find_all('a')['allStatClass']:
    print(link)