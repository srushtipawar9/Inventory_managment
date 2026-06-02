import urllib.request
from bs4 import BeautifulSoup
html = urllib.request.urlopen("https://inventory-managment-1-7ylq.onrender.com/").read()
soup = BeautifulSoup(html, 'html.parser')
for link in soup.find_all('link', rel='stylesheet'):
    print(link.get('href'))
