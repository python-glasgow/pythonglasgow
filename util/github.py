from requests import get


def get_members():

    members = get("https://api.github.com/orgs/python-glasgow/members").json()

    for member in members:
        yield get(member['url']).json()
