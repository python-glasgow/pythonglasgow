#!/usr/bin/env python

from flask.ext.script import Manager

from app import app
manager = Manager(app)


@manager.command
def fetch():

    from pep.tasks import fetch_peps
    fetch_peps()

if __name__ == "__main__":
    manager.run()
