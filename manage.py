#!/usr/bin/env python

from flask.ext.script import Manager


from ug import app
from ug.util.twitter import tweet_events

manager = Manager(app)


@manager.command
def tweeter():
    tweet_events()

if __name__ == "__main__":
    manager.run()
