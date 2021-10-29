import time
import uuid
import os

import requests

def createItem(issue):
    key = str(uuid.uuid4()).upper()
    now = int(time.time())
    item = {key: {'t': 0,
                  'e': 'Task2',
                  'p': {
                      'acrd': None,
                      'ar': [],
                      'cd': now,
                      'dd': None,
                      'dl': [],
                      'do': 0,
                      'icc': 0,
                      'icp': False,
                      'icsd': None,
                      'ix': 0,
                      'md': now,
                      'nt': '<note xml:space="preserve">' + issue['url'] + '</note>',
                      'pr': [],
                      'rr': None,
                      'rt': [],
                      'sp': None,
                      'sr': None,
                      'ss': 0,
                      'st': 0,
                      'tg': [],
                      'ti': 0,
                      'tp': 0,
                      'tr': False,
                      'tt': issue['title']
                  }
                }
            }
    return item

if __name__ == '__main__':
    THINGS_BASE = 'https://cloud.culturedcode.com/version/1'

    try:
        with open('seen.txt') as f:
            seen_issues = set(f.read().splitlines())
    except FileNotFoundError:
        seen_issues = set()

    with open('query.graphql') as f:
        query_string = f.read()

    query = {
        'query': query_string,
        'variables': {'gh_query': "org:labordata repo:datamade/cannabis-idfp"}}

    s = requests.Session()

    response = s.post('https://api.github.com/graphql',
                      json=query,
                      headers={"Authorization": 'bearer ' + os.environ['GH_TOKEN']})

    issues = [node['node'] for node in response.json()['data']['search']['edges']]
    query = {
        'query': query_string,
        'variables': {'gh_query': "assignee:fgregg state:open"}}
    
    response = s.post('https://api.github.com/graphql',
                      json=query,
                      headers={"Authorization": 'bearer ' + os.environ['GH_TOKEN']})

    issues += [node['node'] for node in response.json()['data']['search']['edges']]

    for issue in issues:
        database_id = str(issue['databaseId'])
        if database_id in seen_issues:
            continue

        item = createItem(issue)

        response = s.get(THINGS_BASE + '/history/' + os.environ['HISTORY_KEY'])
        payload = {
            'current-item-index': response.json()['latest-server-index'],
            'items': [item],
            'schema': 1
            }
        response = s.post(THINGS_BASE + '/history/' + os.environ['HISTORY_KEY'] + '/items',
                          json=payload)

        seen_issues.add(database_id)
        
        with open('seen.txt', 'a') as f:
            f.write(database_id + '\n')


    
    
