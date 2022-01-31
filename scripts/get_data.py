from bs4 import BeautifulSoup
from datetime import date
from dotenv import dotenv_values
import json
import requests

def get_leaderboard(session):
    r = session.get('https://www.nytimes.com/puzzles/leaderboards')

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

def save_leaderboard(leaderboard):
    pass

if __name__ == '__main__':
    config = dotenv_values('.env')
    cookies = {
        'NYT-S': config['AUTH_COOKIE']
    }
    
    s = requests.Session()
    s.cookies.update(cookies)

    leaderboard = get_leaderboard(s)
    print(leaderboard)