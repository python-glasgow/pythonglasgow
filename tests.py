from unittest import TestCase, skipIf
from os import environ

from ug import app


class TwitterTestCase(TestCase):

    _TWITTER = ['TWITTER_CONSUMER_KEY', 'TWITTER_ACCESS_TOKEN',
                'TWITTER_CONSUMER_SECRET', 'TWITTER_ACCESS_SECRET']
    _CONDITION = all(i not in environ for i in _TWITTER)
    _MESSAGE = "Can't test without Twitter env vars: %s" % ', '.join(_TWITTER)

    @skipIf(_CONDITION, _MESSAGE)
    def test_twitter_basic(self):

        from util.twitter import get_tweets
        r = get_tweets()
        assert len(r) > 0, "Expecting to get some tweets."


class EventsTestCase(TestCase):

    def test_events_basic(self):

        from util.gcal import upcoming_events
        events = upcoming_events()

        for event in events:
            self.assertIn("type", event.metadata)


class GithubTestCase(TestCase):

    def test_github_basic(self):

        from util.github import get_members
        get_members()


class FlaskrTestCase(TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        self.assertEquals(self.app.get("/").status_code, 200)
