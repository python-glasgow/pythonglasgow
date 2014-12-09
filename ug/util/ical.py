from __future__ import print_function

from datetime import date, datetime, timedelta

from flask_mail import Message
from flask import render_template
import yaml
import pytz
import requests
from icalendar import Calendar

from ug import app


class Event(object):

    def __init__(self, start, title, where, description):
        self.start = start
        self.title = title
        self.where = where
        self.description, self.metadata = self._event_metadata(description)

    def _event_metadata(self, description):

        split_on = "----------"

        if split_on in description:
            description, metadata = description.split(split_on)
            metadata = yaml.load(metadata)
        else:
            metadata = {}

        if 'type' not in metadata:
            metadata['type'] = self.title.split(' ', 1)[0].lower()

        return description, metadata

    def days_until(self):
        until_event = self.start - _now()
        return until_event.days

    def date_string(self):
        if self.start is None:
            return
        date_s = self.start.strftime("%A %d%%s of %B")
        date_s = date_s % _nth(self.start.day)
        return date_s

    def time_string(self):
        if self.start is None:
            return
        time_s = "%d:%02d" % (self.start.hour % 12, self.start.minute)
        ampm = self.start.strftime("%p").lower()
        return time_s + ampm

    @classmethod
    def from_vevent(cls, vevent):

        return Event(
            start=vevent.get('dtstart').dt,
            title=vevent.get('summary').title(),
            where=vevent.get('location').title(),
            description=str(vevent.get('description'))
        )


def _load_calendar():

    ical_request = requests.get(app.config['ICAL'])
    cal = Calendar.from_ical(ical_request.text)

    return cal


def _now():
    return datetime.now(tz=pytz.utc)


def _nth(num):
    """ Returns the 'th' suffix to the given num. What's that thing called?
    """
    sn = str(num)
    ld = sn[-1]
    if len(sn) == 1 or sn[-2] != '1':
        if ld == '1':
            return 'st'
        elif ld == '2':
            return 'nd'
        elif ld == '3':
            return 'rd'
    return 'th'


def upcoming_events(days=60, cal=None):

    if cal is None:
        cal = _load_calendar()

    now = _now() - timedelta(days=1)
    future = now + timedelta(days=days)
    events = []

    for vevent in cal.walk('vevent'):

        start = vevent.get('dtstart').dt

        if isinstance(start, date):
            start = datetime.combine(start, datetime.min.time())

        start = start.replace(tzinfo=pytz.utc)

        if start < now:
            continue

        if start > future:
            continue

        events.insert(0, Event.from_vevent(vevent))

    return events


class NoEvents(Exception):
    pass


def days_until_next_event():

    events = upcoming_events()

    if len(events) == 0:
        raise NoEvents("No events planned")

    event = events[0]
    return event.days_until(), event


def mail_events(recipients=None):
    """Send notification emails.

    Run nightly;
    - if its ADMIN_REMINDER_DAYS before the next event - send an
    email to ADMINS about the next event. This is to remind to book tables
    or remove the event if its there by mistake.

    - if its LIST_REMINDER_DAYS before the next event - send an email to the
    list to let everybody know.
    """

    try:
        days, event = days_until_next_event()
    except NoEvents:
        print("no events")
        return

    where = event.where.split(',')[0]

    subject = " %s on %s in %s" % (event.title, event.date_string(), where)

    if days == app.config['ADMIN_REMINDER_DAYS']:
        print("Sending Admin e-mail")
        to = recipients if recipients else app.config['ADMINS']
        subject = "[Python Glasgow] (Admin pre-warning) " + subject
        template = [
            "admin-alert-%s.txt" % event.metadata['type'], "admin-alert.txt"
        ]

    elif (days == app.config['LIST_REMINDER_DAYS']
          or days == app.config['LIST_FINAL_REMINDER_DAYS']):

        print("Sending list email - %s days before event." % days)
        to = recipients if recipients else app.config['NOTIFICATION_EMAILS']
        subject = "[Python Glasgow] " + subject
        template = [
            "list-alert-%s.txt" % event.metadata['type'], "list-alert.txt"
        ]

    else:
        print("No emails today. Next event in %s days" % days)
        return

    diff = app.config['ADMIN_REMINDER_DAYS'] - app.config['LIST_REMINDER_DAYS']
    body = render_template(template, event=event, days=days, diff=diff)

    to = list(to)
    msg = Message(subject, sender="no-reply@dougalmathews.com", recipients=to,
                  body=body, reply_to="glasgow@python.org")

    app.mail.send(msg)
