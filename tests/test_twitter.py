from datetime import datetime
from os import environ
from unittest2 import TestCase

from mock import patch, Mock
from tweepy import API

from ug import app
from ug.util.twitter import tweet_events, update_status, send_dm


class TwitterTestCase(TestCase):

    def setUp(self):

        environ['TWITTER_CONSUMER_KEY'] = 'fake'
        environ['TWITTER_ACCESS_TOKEN'] = 'fake'
        environ['TWITTER_CONSUMER_SECRET'] = 'fake'
        environ['TWITTER_ACCESS_SECRET'] = 'fake'

        self.mock_event = Mock(
            title="Pub meetup",
            where='Name, Location',
            when=datetime.now()
        )

    @patch('tweepy.auth.OAuthHandler')
    def test_update_status(self, mock_oauthhandler):

        with patch.object(API, 'update_status') as mock_api:

            update_status("Status")

            mock_api.assert_called_once_with(status="Status")

    @patch('tweepy.auth.OAuthHandler')
    def test_send_dm(self, mock_oauthhandler):

        with patch.object(API, 'send_direct_message') as mock_api:

            send_dm("d0ugal", "Hi!")

            mock_api.assert_called_once_with(screen_name="d0ugal", text="Hi!")

    @patch('ug.util.ical.days_until_next_event')
    @patch('ug.util.twitter.send_dm')
    @patch('ug.util.twitter.update_status')
    def test_tweet_far_future(self, mock_update, mock_dm, mock_ical):

        mock_ical.return_value = (100, self.mock_event)
        tweet_events()

        assert not mock_dm.called
        assert not mock_update.called

    @patch('ug.util.ical.days_until_next_event')
    @patch('ug.util.twitter.send_dm')
    @patch('ug.util.twitter.update_status')
    def test_tweet_admin_reminder(self, mock_update, mock_dm, mock_ical):

        num_days = app.config['ADMIN_REMINDER_DAYS']
        mock_ical.return_value = (num_days, self.mock_event)
        tweet_events()

        mock_dm.assert_called_once_with(
            'd0ugal', 'Hey - we have an event coming up, have you sorted it?')
        assert not mock_update.called

    @patch('ug.util.ical.days_until_next_event')
    @patch('ug.util.twitter.send_dm')
    @patch('ug.util.twitter.update_status')
    def test_tweet_list_reminder(self, mock_update, mock_dm, mock_ical):

        num_days = app.config['LIST_REMINDER_DAYS']
        mock_ical.return_value = (num_days, self.mock_event)
        tweet_events()

        mock_dm.assert_called_once_with(
            'd0ugal',
            ('The next Python Glasgow event is a Pub meetup in 7 '
             'days at Name. See http://pythonglasgow.org/ for more details.'))

        mock_update.assert_called_once_with(
            'The next Python Glasgow event is a Pub meetup in 7 '
            'days at Name. See http://pythonglasgow.org/ for more details.'
        )


class TwitterNoEnvTestCase(TestCase):

    def setUp(self):

        self.mock_event = Mock(
            title="Pub meetup",
            where='Name, Location',
            when=datetime.now()
        )

    @patch('tweepy.auth.OAuthHandler')
    def test_update_status(self, mock_oauthhandler):

        with patch.object(API, 'update_status') as mock_api:

            update_status("Status")
            assert not mock_api.called

    @patch('tweepy.auth.OAuthHandler')
    def test_send_dm(self, mock_oauthhandler):

        with patch.object(API, 'send_direct_message') as mock_api:

            send_dm("d0ugal", "Hi!")
            assert not mock_api.called
