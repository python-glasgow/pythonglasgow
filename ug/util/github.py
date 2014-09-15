from requests import get, ConnectionError


MEMBERS_URL = "https://api.github.com/orgs/{org}/members"


def get_members(organization):
    url = MEMBERS_URL.format(org=organization)
    try:
        response = get(url)
    except ConnectionError:
        return []
    if response.ok:
        return response.json()
