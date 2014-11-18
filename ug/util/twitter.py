from logging import error
from os import environ
from re import compile

from jinja2 import Markup
from jinja2.utils import urlize
from tweepy import OAuthHandler, API, TweepError

from ug import app


def twitterfy(tweet):

    tweet = urlize(tweet)

    # find hashtags
    pattern = compile(r"(?P<start>.?)#(?P<hashtag>[A-Za-z0-9\-_]+)(?P<end>.?)")

    # replace with link to search
    link = (r'\g<start>#<a href="http://search.twitter.com/search?q=\g<hashtag'
            '>"  title="#\g<hashtag> search Twitter">\g<hashtag></a>\g<end>')
    text = pattern.sub(link, tweet)

    # find usernames
    pattern = compile(r"(?P<start>.?)@(?P<user>[A-Za-z0-9_]+)(?P<end>.?)")

    # replace with link to profile
    link = (r'\g<start>@<a href="http://twitter.com/\g<user>"  title="#\g<user'
            '> on Twitter">\g<user></a>\g<end>')
    text = pattern.sub(link, text)

    return Markup(text)


def get_tweets(count=5):

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
        statuses = api.user_timeline('pythonglasgow', count=count)
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


def tweet_events():

    from ug.util.ical import NoEvents, days_until_next_event

    try:
        days, event = days_until_next_event()
    except NoEvents:
        print "no events"
        return

    where = event.where.split(',')[0]
    time = event.when.time()
    time_string = "%02d:%02d" % (time.hour, time.minute)

    print days

    if days == app.config['ADMIN_REMINDER_DAYS']:

        print "DM to d0ugal"

        send_dm("d0ugal",
                "Hey - we have an event coming up, have you sorted it?")

    elif days == app.config['LIST_REMINDER_DAYS']:

        print "weekly tweet"

        tweet = ('The next Python Glasgow event is a {title} in {days} '
                 'days at {where}. See http://pythonglasgow.org/ for more '
                 'details.').format(title=event.title, where=where, days=days)

        update_status(tweet)
        send_dm("d0ugal", tweet)

    elif days == 0:

        print "on the day tweet."

        tweet = ("There is a {title} tonight at {time} in {where}. See "
                 "http://pythonglasgow.org/ for more details."
                 ).format(title=event.title, time=time_string, where=where)

        update_status(tweet)
        send_dm("d0ugal", tweet)

    else:
        print "No Twitter updates today"
