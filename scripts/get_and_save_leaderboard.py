from bs4 import BeautifulSoup
from datetime import date, datetime
from zoneinfo import ZoneInfo
import base64
import json
import requests
import os

REPO = 'justinkhado/nyt-crossword-data'

def _get_sha(session, url):
    r = session.get(url)
    if r.status_code == 404:
        return None
    return r.json()['sha']

def save_leaderboard_raw(session, token):
    r = session.get('https://www.nytimes.com/puzzles/leaderboards')
    # get today's date in New York time
    today = datetime.strftime(datetime.now(ZoneInfo('America/New_York')), '%Y-%m-%d')

    headers = {
        'Authorization': f'Token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    data = {
        'message': f"{today}",
        'content': base64.b64encode(r.content).decode(),
        'branch': 'master'
    }

    repo = 'justinkhado/nyt-crossword-data'
    path = f"raw_data/{today}.txt"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"

    sha = _get_sha(session, url)
    if sha:
        data = {**data, 'sha': sha}

    r = session.put(url, data=json.dumps(data), headers=headers)
    print(r.status_code)

    return today

def get_leaderboard(session, day):
    branch = 'master'
    r = session.get(f'https://raw.githubusercontent.com/{REPO}/{branch}/raw_data/{day}.txt')
    soup = BeautifulSoup(r.content, 'html.parser')

    today = soup.find(class_='lbd-type__date').text
    leaderboard = {'date': today, 'scores': []}
    results = soup.find_all(class_='lbd-score')
    for result in results:
        if result.find(class_='lbd-score__link'):
            continue

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
        'content': base64.b64encode(json.dumps(leaderboard, indent=4).encode('utf-8')).decode(),
        'branch': 'master'
    }

    today = datetime.strptime(leaderboard['date'], '%A, %B %d, %Y')
    path = f"data/{today.year}/{datetime.strftime(today, '%m. %B')}/{datetime.strftime(today, '%Y-%m-%d')}.json"
    url = f'https://api.github.com/repos/{REPO}/contents/{path}'

    sha = _get_sha(session, url)
    if sha:
        data = {**data, 'sha': sha}
        
    r = session.put(url, data=json.dumps(data), headers=headers)
    print(r.status_code)

if __name__ == '__main__':
    cookies = {
        'NYT-S': os.environ['AUTH_COOKIE']
    }
    
    s = requests.Session()
    s.cookies.update(cookies)

    today = save_leaderboard_raw(s, os.environ['GH_TOKEN'])
    leaderboard = get_leaderboard(s, today)
    save_leaderboard(s, leaderboard, os.environ['GH_TOKEN'])
    