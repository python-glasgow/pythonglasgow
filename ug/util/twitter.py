from __future__ import print_function

from logging import error
from os import environ

from tweepy import OAuthHandler, API


def update_status(text):

    try:
        consumer_key = environ['TWITTER_CONSUMER_KEY']
        access_token = environ['TWITTER_ACCESS_TOKEN']
        consumer_secret = environ['TWITTER_CONSUMER_SECRET']
        access_secret = environ['TWITTER_ACCESS_SECRET']
    except KeyError:
        error("No Twitter credentials were found.")
        # We don't have login stuff, bail.
        return

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
        return

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = API(auth_handler=auth)
    api.send_direct_message(screen_name=username, text=text)
