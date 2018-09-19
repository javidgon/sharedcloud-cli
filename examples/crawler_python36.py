# Credits: https://dev.to/pranay749254/build-a-simple-python-web-crawler

import requests
from bs4 import BeautifulSoup

def handler(event):
    page = int(event[0])
    web_url = event[1]
    if(page > 0):
        url = web_url
        code = requests.get(url)
        plain = code.text
        s = BeautifulSoup(plain, "html.parser")
        for link in s.findAll('a', {'class':'s-access-detail-page'}):
            tet = link.get('title')
            print(tet)
            tet_2 = link.get('href')
            print(tet_2)