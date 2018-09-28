import requests
from bs4 import BeautifulSoup

def handler(event):
    url = event[0]

    if(url):
        print('Fetching the number of answers and comments from {}'.format(url))
        code = requests.get(url)
        plain = code.text
        parser = BeautifulSoup(plain, "html.parser")

        num_answers = len(parser.find_all('div', {'class': 'answer'}))
        num_comments = len(parser.find_all('div', {'class': 'comment'}))

        return 'Num Answers: {}, Num Comments: {}'.format(num_answers, num_comments)
    else:
        print('Please type a valid StackOverflow URL')
