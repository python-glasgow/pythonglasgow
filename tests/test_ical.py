from datetime import datetime
from unittest2 import TestCase
from os import path

import pytz
from mock import patch

from ug import app
from ug.util import ical


def _load_calendar():
    ical_file = path.join(path.dirname(path.abspath(__file__)), 'ical.ics')
    ical_contents = open(ical_file).read()
    cal = ical.Calendar.from_ical(ical_contents)
    return cal


class IcalTestCase(TestCase):

    def setUp(self):

        self.now_patch = patch('ug.util.ical._now',
                               return_value=datetime(2014, 11, 18, 8, 24, 7,
                                                     tzinfo=pytz.utc))
        self.now_patch.start()
        self.load_calendar_patch = patch('ug.util.ical._load_calendar',
                                         new=_load_calendar)
        self.load_calendar_patch.start()

        self.cal = _load_calendar()
        self.event_pub, self.event_dojo = ical.upcoming_events(cal=self.cal)

    def tearDown(self):
        self.now_patch.stop()
        self.load_calendar_patch.stop()

    def test_upcoming_events(self):

        pub, dojo = ical.upcoming_events()
        url = 'http://attending.io/events/pythonglasgow-dojo-december-2014'

        self.assertEquals(dojo.title, "Coding Dojo")
        self.assertEquals(
            dojo.start, datetime(2014, 12, 9, 18, 30, 00, tzinfo=pytz.utc))
        self.assertEquals(dojo.where, "Twig World, 14 N Claremont St, G3 7Le")
        self.assertEquals(dojo.description, "")
        self.assertEquals(dojo.metadata, {
            'type': 'dojo',
            'link': url,
        })

        self.assertEquals(pub.title, "Pub Meetup")
        self.assertEquals(
            pub.start, datetime(2014, 11, 19, 18, 30, 00, tzinfo=pytz.utc))
        self.assertEquals(pub.where, ("The Raven Glasgow, 81-85 Renfield St, "
                                      "Glasgow G2 1Nq, United Kingdom"))
        self.assertEquals(pub.description, "")
        self.assertEquals(pub.metadata, {
            'type': 'pub',
        })

    def test_days_until_next_event(self):

        days, event = ical.days_until_next_event()

        self.assertEquals(1, days)
        self.assertEquals(event.title, self.event_pub.title)
        self.assertEquals(event.start, self.event_pub.start)

        self.assertEquals(21, self.event_dojo.days_until())

    def test_days_until_next_event_none(self):

        with patch('ug.util.ical._now',
                   return_value=datetime(2015, 11, 18, 8, 24, 7,
                                         tzinfo=pytz.utc)):
            with self.assertRaises(ical.NoEvents):
                ical.days_until_next_event()

    @patch('flask_mail._MailMixin.send')
    @patch('ug.util.ical.days_until_next_event')
    def test_mail_events_noop(self, mock_days_until, mock_send):

        mock_days_until.return_value = (20, self.event_pub)

        ical.mail_events('test@test.com')

        assert not mock_send.called

    @patch('flask_mail._MailMixin.send')
    @patch('ug.util.ical.days_until_next_event')
    def test_mail_events_admin(self, mock_days_until, mock_send):

        mock_days_until.return_value = (
            app.config['ADMIN_REMINDER_DAYS'], self.event_pub
        )

        with app.test_request_context('/send_email'):
            ical.mail_events('test@test.com')

        mock_send.assert_called_once()

    @patch('flask_mail._MailMixin.send')
    @patch('ug.util.ical.days_until_next_event')
    def test_mail_events_list(self, mock_days_until, mock_send):

        mock_days_until.return_value = (
            app.config['LIST_REMINDER_DAYS'], self.event_pub
        )

        with app.test_request_context('/send_email'):
            ical.mail_events('test@test.com')

        mock_send.assert_called_once()

    @patch('flask_mail.Mail.send')
    def test_mail_no_events(self, mock_send):

        with app.test_request_context('/send_email'):
            ical.mail_events('test@test.com')

        mock_send.assert_called_once()
