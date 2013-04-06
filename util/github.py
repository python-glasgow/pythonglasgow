from requests import get, ConnectionError


def get_members():

    try:
        members = get("https://api.github.com/orgs/python-glasgow/members").json()
    except ConnectionError:
        raise StopIteration

    for member in members:
        yield get(member['url']).json()
