from datetime import datetime
from os import environ
from unittest2 import TestCase

from mock import patch, Mock
from tweepy import API

from ug.util.twitter import update_status, send_dm


class TwitterTestCase(TestCase):

    def setUp(self):

        environ['TWITTER_CONSUMER_KEY'] = 'fake'
        environ['TWITTER_ACCESS_TOKEN'] = 'fake'
        environ['TWITTER_CONSUMER_SECRET'] = 'fake'
        environ['TWITTER_ACCESS_SECRET'] = 'fake'

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
