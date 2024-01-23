import os
import sys
import time
import uuid

import requests
from things_cloud import ThingsClient
from things_cloud.models.todo import Note, TodoItem

if __name__ == "__main__":
    THINGS_BASE = "https://cloud.culturedcode.com/version/1"

    try:
        with open("seen.txt") as f:
            seen_issues = set(f.read().splitlines())
    except FileNotFoundError:
        seen_issues = set()

    with open("query.graphql") as f:
        query_string = f.read()

    query = {
        "query": query_string,
        "variables": {
            "gh_query": "org:labordata repo:datamade/cannabis-idfp repo:vm-wylbur/adaptive-blocking-paper state:open"
        },
    }

    s = requests.Session()

    response = s.post(
        "https://api.github.com/graphql",
        json=query,
        headers={"Authorization": "bearer " + os.environ["GH_TOKEN"]},
    )

    issues = [node["node"] for node in response.json()["data"]["search"]["edges"]]
    query = {
        "query": query_string,
        "variables": {"gh_query": "assignee:fgregg state:open"},
    }

    response = s.post(
        "https://api.github.com/graphql",
        json=query,
        headers={"Authorization": "bearer " + os.environ["GH_TOKEN"]},
    )

    issues += [node["node"] for node in response.json()["data"]["search"]["edges"]]

    with open("pr.graphql") as f:
        pr_query_string = f.read()

    query = {
        "query": pr_query_string,
        "variables": {"gh_query": "review-requested:fgregg state:open"},
    }

    response = s.post(
        "https://api.github.com/graphql",
        json=query,
        headers={"Authorization": "bearer " + os.environ["GH_TOKEN"]},
    )

    issues += [node["node"] for node in response.json()["data"]["search"]["edges"]]

    for issue in issues:
        try:
            database_id = str(issue["databaseId"])
        except KeyError:
            print(issue, file=sys.stderr)
            continue

        if database_id in seen_issues:
            continue

        response = s.get(THINGS_BASE + "/history/" + os.environ["HISTORY_KEY"])

        things = ThingsClient(
            os.environ["HISTORY_KEY"],
            initial_offset=response.json()["latest-server-index"],
        )

        note = Note()
        note.ch = 1
        note.v = issue["url"]
        note.t = 1
        todo = TodoItem(issue["title"], note=note)
        things.create(todo)

        seen_issues.add(database_id)

        with open("seen.txt", "a") as f:
            f.write(database_id + "\n")
