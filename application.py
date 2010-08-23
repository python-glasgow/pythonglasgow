import logging
import re
import urllib

from django.utils import simplejson
from django.utils.html import urlize
from google.appengine.api import memcache
from google.appengine.ext import db

from flask import Flask
from flask import render_template, redirect, request
from jinja2 import Markup
import tweepy

CONSUMER_KEY = 'yoeDSxUQtz40PbpnCUQ'
CONSUMER_SECRET = 'hM3sja4piETCm1z7s77fapjynLerdHmfd14qY8Yvq0'
CALLBACK = 'http://localhost:8080/oauth/callback'

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html', );

class OAuthToken(db.Model):
    token_key = db.StringProperty(required=True)
    token_secret = db.StringProperty(required=True)


@app.route('/oauth')
def auth():
    # Build a new oauth handler and display authorization url to user.
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
    authurl = auth.get_authorization_url()
    
    try:
        request_token = auth.request_token
        if not request_token:
            return render_template('error.html', message='Failed to get a request token')
    except tweepy.TweepError, e:
        # Failed to get a request token
        return render_template('error.html', message=e)
    
    # We must store the request token for later use in the callback page.
    request_token = OAuthToken(
            token_key = auth.request_token.key,
            token_secret = auth.request_token.secret
    )
    request_token.put()
    
    return redirect(authurl)


@app.route('/oauth/callback')
def auth_callback():
    oauth_token = request.args.get("oauth_token", None)
    oauth_verifier = request.args.get("oauth_verifier", None)
    if oauth_token is None:
        # Invalid request!
        return render_template('error.html',
            message='Missing required parameters!'
        )
    
    # Lookup the request token
    request_token = OAuthToken.gql("WHERE token_key=:key", key=oauth_token).get()
    if request_token is None:
        # We do not seem to have this request token, show an error.
        return render_template('error.html',
            message='Invalid token!')
    
    # Rebuild the auth handler
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_request_token(request_token.token_key, request_token.token_secret)
    
    # Fetch the access token
    try:
        auth.get_access_token(oauth_verifier)
    except tweepy.TweepError, e:
        # Failed to get access token
        return render_template('error.html', message=e)
    
    # So now we could use this auth handler.
    # Here we will just display the access token key&secret
    return render_template('oauth_example/callback.html',
        access_token=auth.access_token)


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

@app.context_processor
def get_tweets():
    
    tweets = memcache.get("tweets")
    
    if tweets is None:
        
        url = "http://search.twitter.com/search.json?q=from:pythonedinburgh"
        f = urllib.urlopen(url)
        content = f.read()
        json = simplejson.loads(content)
        json_tweets = json['results']
        
        tweets = {'tweets': [twitterfy(tweet['text']) for tweet in json_tweets],}
        
        if not memcache.add("tweets", tweets, 60 * 10): # 10 mins.
            logging.error("Memcache set failed.")
    
    return tweets

app.secret_key = '7%@0g6y!hu^flbmkcfb$@zxs9ftmh=t0blgnog-ibh52za$6nu'

if __name__ == '__main__':
    app.run()
