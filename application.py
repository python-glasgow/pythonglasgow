import logging
import re
import urllib

from django.utils.html import urlize
from google.appengine.api import memcache
from google.appengine.ext import db

from flask import Flask
from flask import render_template, redirect, request
from jinja2 import Markup
import tweepy
import gcal

app = Flask(__name__)


class TwitterCredentials(db.Model):
    consumer_key = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    consumer_secret = db.StringProperty(required=True)
    access_secret = db.StringProperty(required=True)


@app.route('/')
def home():
    return render_template('home.html',
            tweets=get_tweets(),
            next_event=gcal.next_event());


def twitterfy(tweet):
    # find hashtags
    pattern = re.compile(r"(?P<start>.?)#(?P<hashtag>[A-Za-z0-9_]+)(?P<end>.?)")
    
    # replace with link to search
    link = r'\g<start>#<a href="http://search.twitter.com/search?q=\g<hashtag>"  title="#\g<hashtag> search Twitter">\g<hashtag></a>\g<end>'
    text = pattern.sub(link,tweet)
    
    # find usernames
    pattern = re.compile(r"(?P<start>.?)@(?P<user>[A-Za-z0-9_]+)(?P<end>.?)")
    
    # replace with link to profile
    link = r'\g<start>@<a href="http://twitter.com/\g<user>"  title="#\g<user> on Twitter">\g<user></a>\g<end>'
    text = pattern.sub(link,text)
    
    return Markup(urlize(text))


def get_tweets():
    tweets = memcache.get("tweets")
    
    if tweets is None:
        credentials = TwitterCredentials.all().get()
        if credentials:
            auth = tweepy.OAuthHandler(credentials.consumer_key, credentials.consumer_secret)
            auth.set_access_token(credentials.access_token, credentials.access_secret)
            api = tweepy.API(auth_handler=auth)
            statuses = api.user_timeline('pythonedinburgh', count=5)
        
            tweets = [twitterfy(status.text) for status in statuses]
        
            if not memcache.add("tweets", tweets, 60 * 10): # 10 mins.
                logging.error("Memcache tweet store failed.")
        else:
            logging.warn("No Twitter credentials were found in the database. Creating them")
            credentials = TwitterCredentials(consumer_key='a', access_token='a',
                    consumer_secret='a', access_secret='a')
            db.put(credentials)
    
    return tweets

app.secret_key = '7%@0g6y!hu^flbmkcfb$@zxs9ftmh=t0blgnog-ibh52za$6nu'

if __name__ == '__main__':
    app.run()
