from random import shuffle

from flask import Blueprint, render_template

from ug import app
from ug.util.cache import cached
from ug.util.ical import upcoming_events
from ug.util.twitter import get_tweets

mod = Blueprint('base', __name__)


@mod.route('/')
@cached(timeout=60 * 2)  # 2 mins
def index():

    tweets = get_tweets()
    events = upcoming_events()
    members = app.get_github_members()

    if members:
        shuffle(members)

    return render_template(
        'base/index.html',
        members=members,
        tweets=tweets,
        upcoming_events=events,
    )
