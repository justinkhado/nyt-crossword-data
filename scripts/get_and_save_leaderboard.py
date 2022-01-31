from bs4 import BeautifulSoup
from datetime import date
from dotenv import dotenv_values
import base64
import json
import requests

def _get_sha(session, url):
    r = session.get(url)
    if r.status_code == 404:
        return None
    return r.json()['sha']

def get_leaderboard(session):
    r = session.get('https://www.nytimes.com/puzzles/leaderboards')

    soup = BeautifulSoup(r.content, 'html.parser')

    results = soup.find_all(class_='lbd-score')

    today = date.today().strftime('%Y-%m-%d')
    leaderboard = {'date': today, 'scores': []}
    for result in results:
        person = {}
        person['rank'] = result.find(class_='lbd-score__rank').text
        person['name'] = result.find(class_='lbd-score__name').text.replace('(you)', '')
        person['time'] = result.find(class_='lbd-score__time').text
        if person['time'] != '--':
            leaderboard['scores'].append(person)

    return leaderboard

def save_leaderboard(session, leaderboard, token):   
    headers = {
        'Authorization': f'Token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    data = {
        'message': f"{leaderboard['date']}",
        'content': base64.b64encode(json.dumps(leaderboard).encode('utf-8')).decode(),
        'branch': 'data'
    }

    repo = 'justinkhado/nyt-crossword-data'
    path = f"data/{leaderboard['date'].split('-')[1]}/{leaderboard['date']}.json"
    url = f'https://api.github.com/repos/{repo}/contents/{path}'
    sha = _get_sha(session, url)

    if sha:
        data = {**data, 'sha': sha}
        
    r = session.put(url, data=json.dumps(data), headers=headers)


if __name__ == '__main__':
    config = dotenv_values('.env')
    cookies = {
        'NYT-S': config['AUTH_COOKIE']
    }
    
    s = requests.Session()
    s.cookies.update(cookies)

    leaderboard = get_leaderboard(s)
    save_leaderboard(s, leaderboard, config['GH_TOKEN'])
    