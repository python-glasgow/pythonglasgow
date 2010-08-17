import urllib

from django.utils import simplejson
from google.appengine.api import memcache

from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', );

@app.context_processor
def get_tweets():
    
    tweets = memcache.get("tweets")
    
    if tweets is None:
        
        url = "https://twitter.com/statuses/user_timeline.json?screen_name=pythonedinburgh"
        f = urllib.urlopen(url)
        content = f.read()
        json = simplejson.loads(content)
        
        tweets = {'tweets':json,}
        
        if not memcache.add("tweets", tweets, 60 * 10): # 10 mins.
            logging.error("Memcache set failed.")
        
    return tweets

app.secret_key = '7%@0g6y!hu^flbmkcfb$@zxs9ftmh=t0blgnog-ibh52za$6nu'

if __name__ == '__main__':
    app.run()
