import time
import uuid

import requests

import secrets

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

try:
    with open('last_updated.txt') as f:
        last_updated = f.read()
except FileNotFoundError:
    last_updated = '2021-01-01'

with open('query.graphql') as f:
    query = {
        'query': f.read(),
        'variables': {'gh_query': "org:labordata repo:datamade/cannabis-idfp state:open created:>=" + last_updated}}

s = requests.Session()
s.headers.update({"Authorization": 'bearer ' + secrets.GH_TOKEN})

response = s.post('https://api.github.com/graphql', json=query)

issues = [node['node'] for node in response.json()['data']['search']['edges']]
issues.sort(key = lambda x: x['createdAt'])

THINGS_BASE = 'https://cloud.culturedcode.com/version/1'

for issue in issues:
    last_updated = issue['createdAt']
    item = createItem(issue)
    response = s.get(THINGS_BASE + '/history/' + secrets.HISTORY_KEY)


    
    #print(item)
    payload = {
        'current-item-index': response.json()['latest-server-index'],
        'items': [item],
        'schema': 1
        }
    #response = s.post('https://cloud.culturedcode.com/version/1/history/' + secrets.HISTORY_KEY + '/items',
    #                  json=payload)
    #print(response.json())
    import json
    print(json.dumps(payload))

    with open('last_updated.txt', 'w') as f:
        f.write(last_updated)


    
    
