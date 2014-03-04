from requests import get, ConnectionError

MEMBERS_URL = "https://api.github.com/orgs/python-glasgow/members"


def _check_rate_limit(members):
    msg = "API Rate Limit Exceeded"
    if 'message' in members and members['message'].startswith(msg):
        print "GITHUB RATE LIMIT."
        raise StopIteration


def get_members():

    try:
        members = get(MEMBERS_URL).json()
    except ConnectionError:
        raise StopIteration

    _check_rate_limit(members)

    for member in members:
        try:
            yield get(member['url']).json()
        except (ValueError, TypeError):
            continue
