from logging import error
from os import environ
from re import compile

from jinja2 import Markup
from jinja2.utils import urlize
from tweepy import OAuthHandler, API, TweepError


def twitterfy(tweet):

    tweet = urlize(tweet)

    # find hashtags
    pattern = compile(r"(?P<start>.?)#(?P<hashtag>[A-Za-z0-9\-_]+)(?P<end>.?)")

    # replace with link to search
    link = r'\g<start>#<a href="http://search.twitter.com/search?q=\g<hashtag>"  title="#\g<hashtag> search Twitter">\g<hashtag></a>\g<end>'
    text = pattern.sub(link, tweet)

    # find usernames
    pattern = compile(r"(?P<start>.?)@(?P<user>[A-Za-z0-9_]+)(?P<end>.?)")

    # replace with link to profile
    link = r'\g<start>@<a href="http://twitter.com/\g<user>"  title="#\g<user> on Twitter">\g<user></a>\g<end>'
    text = pattern.sub(link, text)

    return Markup(text)


def get_tweets():

    try:
        consumer_key = environ['TWITTER_CONSUMER_KEY']
        access_token = environ['TWITTER_ACCESS_TOKEN']
        consumer_secret = environ['TWITTER_CONSUMER_SECRET']
        access_secret = environ['TWITTER_ACCESS_SECRET']
    except KeyError:
        error("No Twitter credentials were found.")
        # We don't have login stuff, bail.
        return []

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = API(auth_handler=auth)

    try:
        statuses = api.user_timeline('pythonglasgow', count=5)
    except TweepError:
        error("Failed to read timelime.")
        return []

    tweets = [(status, twitterfy(status.text)) for status in statuses]

    return tweets


def update_status(text):

    try:
        consumer_key = environ['TWITTER_CONSUMER_KEY']
        access_token = environ['TWITTER_ACCESS_TOKEN']
        consumer_secret = environ['TWITTER_CONSUMER_SECRET']
        access_secret = environ['TWITTER_ACCESS_SECRET']
    except KeyError:
        error("No Twitter credentials were found.")
        # We don't have login stuff, bail.
        return []

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = API(auth_handler=auth)
    api.update_status(status=text)


def send_dm(username, text):

    try:
        consumer_key = environ['TWITTER_CONSUMER_KEY']
        access_token = environ['TWITTER_ACCESS_TOKEN']
        consumer_secret = environ['TWITTER_CONSUMER_SECRET']
        access_secret = environ['TWITTER_ACCESS_SECRET']
    except KeyError:
        error("No Twitter credentials were found.")
        # We don't have login stuff, bail.
        return []

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = API(auth_handler=auth)
    api.update_status(screen_name=username, text=text)
