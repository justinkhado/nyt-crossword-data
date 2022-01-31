from bs4 import BeautifulSoup
from datetime import date
from dotenv import dotenv_values
import requests

def get_leaderboard(s):
    r = s.get('https://www.nytimes.com/puzzles/leaderboards')

    soup = BeautifulSoup(r.content, 'html.parser')

    results = soup.find_all(class_='lbd-score')

    today = date.today().strftime('%Y-%m-%d')
    leaderboard = {'date': today, 'scores': []}
    for result in results:
        person = {}
        person['rank'] = result.find(class_='lbd-score__rank').text
        person['name'] = result.find(class_='lbd-score__name').text
        person['time'] = result.find(class_='lbd-score__time').text
        leaderboard['scores'].append(person)

    return leaderboard

if __name__ == '__main__':
    config = dotenv_values('.env')

    assert 'AUTH_COOKIE' in config, 'No auth cookie'
    cookies = {
        'NYT-S': config['AUTH_COOKIE']
    }
    
    s = requests.Session()
    s.cookies.update(cookies)

    