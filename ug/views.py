from flask import Blueprint, render_template

from ug.util.cache import cached
from ug.util.ical import upcoming_events

mod = Blueprint('base', __name__)


@mod.route('/')
@cached(timeout=60 * 2)  # 2 mins
def index():

    events = upcoming_events()

    return render_template(
        'base/index.html',
        upcoming_events=events,
    )


@mod.route('/code-of-conduct/')
def code_of_conduct():
    return render_template('base/code_of_conduct.html')
