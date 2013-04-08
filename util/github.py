from requests import get, ConnectionError


def get_members():

    try:
        members = get("https://api.github.com/orgs/python-glasgow/members").json()
        if 'message' in members and members['message'].startswith("API Rate Limit Exceeded"):
            raise StopIteration
    except ConnectionError:
        raise StopIteration

    for member in members:
        yield get(member['url']).json()
