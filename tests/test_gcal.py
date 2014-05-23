from datetime import datetime
from unittest2 import TestCase

from mock import patch, Mock

from ug import app
from ug.util.gcal import (CalendarEvent, upcoming_events, NoEvents,
                          days_until_next_event, mail_events)


class GCalTestCase(TestCase):

    def setUp(self):

        app.config['TESTING'] = True
        self.app = app.test_client()

        # Create two object that mimic that atom objects using within gdata.
        self.atom_pub = Mock()
        self.atom_pub.title.text = "Pub Meetup"
        self.atom_pub.when = [Mock(start_time="2014-03-11T18:30:00"), ]
        self.atom_pub.where = [Mock(value_string="Pub, Glasgow"), ]
        self.atom_pub.content.text = "Content"

        self.atom_dojo = Mock()
        self.atom_dojo.title.text = "Dojo"
        self.atom_dojo.when = [Mock(start_time="2014-02-11T18:00:00"), ]
        self.atom_dojo.where = [Mock(value_string="Host, Glasgow"), ]
        self.atom_dojo.content.text = (
            "Content\n"
            "----------\n"
            "link: http://pythonglasgow.org/"
        )
        self.event_pub = CalendarEvent(self.atom_pub)
        self.event_dojo = CalendarEvent(self.atom_dojo)

    @patch('gdata.calendar.service.CalendarService.CalendarQuery')
    def test_upcoming_events(self, mock_calendar):

        mock_calendar.return_value.entry = [self.atom_pub, self.atom_dojo]

        dojo, pub = upcoming_events()

        # TODO: Verify the query.
        mock_calendar.assert_called_once()

        self.assertEquals(pub.title, "Pub Meetup")
        self.assertEquals(pub.when, datetime(2014, 03, 11, 18, 30, 00))
        self.assertEquals(pub.where, "Pub, Glasgow")
        self.assertEquals(pub.description, "Content")
        self.assertEquals(pub.metadata, {'type': 'pub'})

        self.assertEquals(dojo.title, "Dojo")
        self.assertEquals(dojo.when, datetime(2014, 02, 11, 18, 00, 00))
        self.assertEquals(dojo.where, "Host, Glasgow")
        self.assertEquals(dojo.description, "Content\n")
        self.assertEquals(dojo.metadata, {
            'type': 'dojo',
            'link': 'http://pythonglasgow.org/'
        })

    @patch('ug.util.gcal.upcoming_events')
    @patch('ug.util.gcal._now', return_value=datetime(2014, 03, 04, 20, 0, 0))
    def test_days_until_next_event(self, mock_now, mock_upcoming_events):

        mock_upcoming_events.return_value = [self.event_pub, self.event_dojo]

        days, event = days_until_next_event()

        self.assertEquals(days, 6)
        self.assertEquals(event, self.event_pub)

    @patch('ug.util.gcal.upcoming_events')
    def test_days_until_next_event_none(self, mock_upcoming_events):

        mock_upcoming_events.return_value = []

        with self.assertRaises(NoEvents):
            days_until_next_event()

    @patch('flask_mail._MailMixin.send')
    @patch('ug.util.gcal.days_until_next_event')
    def test_mail_events_noop(self, mock_days_until_next_event, mock_send):

        mock_days_until_next_event.return_value = (20, self.event_pub)

        mail_events('test@test.com')

        assert not mock_send.called

    @patch('flask_mail._MailMixin.send')
    @patch('ug.util.gcal.days_until_next_event')
    def test_mail_events_admin(self, mock_days_until_next_event, mock_send):

        mock_days_until_next_event.return_value = (
            app.config['ADMIN_REMINDER_DAYS'], self.event_pub
        )

        with app.test_request_context('/send_email'):
            mail_events('test@test.com')

        mock_send.assert_called_once()

    @patch('flask_mail.Mail.send')
    @patch('ug.util.gcal.days_until_next_event')
    def test_mail_events_list(self, mock_days_until_next_event, mock_send):

        mock_days_until_next_event.return_value = (
            app.config['LIST_REMINDER_DAYS'], self.event_pub
        )

        with app.test_request_context('/send_email'):
            mail_events('test@test.com')

        mock_send.assert_called_once()

    @patch('flask_mail.Mail.send')
    @patch('ug.util.gcal.days_until_next_event')
    def test_mail_no_events(self, mock_days_until_next_event, mock_send):

        mock_days_until_next_event.side_effect = NoEvents("")

        with app.test_request_context('/send_email'):
            mail_events('test@test.com')

        mock_send.assert_called_once()
