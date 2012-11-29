from flask import Blueprint, render_template

from util.cache import cached
from util.gcal import upcoming_events
from util.twitter import get_tweets

mod = Blueprint('base', __name__)


@mod.route('/')
@cached(timeout=60 * 10)  # 10 mins
def index():

    tweets = get_tweets()
    events = cached(timeout=60 * 60)(upcoming_events)()

    return render_template('base/index.html',
        tweets=tweets,
        upcoming_events=events,
    )
