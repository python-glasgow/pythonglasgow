from datetime import datetime, timedelta

from flask_mail import Message
from flask import render_template
from gdata.calendar.service import CalendarService, CalendarEventQuery
import yaml

from ug import mail, app


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


class CalendarEvent(object):
    def __init__(self, atom_ob):
        self.title = atom_ob.title.text
        whs = atom_ob.when[0].start_time
        whs = whs.split('.')[0]
        self.when = datetime.strptime(whs, '%Y-%m-%dT%H:%M:%S')
        self.where = atom_ob.where[0].value_string

        self.description = atom_ob.content.text

        split_on = "----------"
        if self.description and split_on in self.description:
            self.description, metadata = self.description.split(split_on)

            self.metadata = yaml.load(metadata)

        else:
            self.metadata = {}

        if 'type' not in self.metadata:
            self.metadata['type'] = self.title.split(' ', 1)[0].lower()

    def date_string(self):
        date_s = self.when.strftime("%A %d%%s of %B")
        date_s = date_s % _nth(self.when.day)

        return date_s

    def time_string(self):
        time_s = "%d:%02d" % (self.when.hour % 12, self.when.minute)
        ampm = self.when.strftime("%p").lower()

        return time_s + ampm

    def days_until(self):
        until_event = self.when - datetime.now()

        return until_event.days


def upcoming_events(days=90):

    # Create a Google Calendar client to talk to the Google Calendar service.
    calendar_client = CalendarService()

    # Set up a query with the GCAL_ID.
    query = CalendarEventQuery(app.config['GCAL_ID'], 'public', 'full')
    query.orderby = 'starttime'
    query.sortorder = 'descending'

    # we're interested in events in the next 60 days if we wanted all the
    # futuer events, we'd use query.futureevents='true' and ignore the
    # start_min, start_max options
    month_offset = timedelta(days=days)

    start_min = datetime.now()
    start_max = start_min + month_offset

    query.start_min = start_min.isoformat()
    query.start_max = start_max.isoformat()

    # query gcal for the time interval
    return [CalendarEvent(e) for e in calendar_client.CalendarQuery(query).entry]


class NoEvents(Exception):
    pass


def days_until_next_event():

    events = upcoming_events(days=90)

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
        print "no events"
        return

    where = event.where.split(',')[0]

    subject = " %s on %s in %s" % (event.title, event.date_string(), where)

    if days == app.config['ADMIN_REMINDER_DAYS']:
        print "Sending Admin e-mail"
        to = recipients if recipients else app.config['ADMINS']
        subject = "[Python Glasgow] (Admin pre-warning) " + subject
        template = [
            "admin-alert-%s.txt" % event.metadata['type'], "admin-alert.txt"
        ]

    elif days == app.config['LIST_REMINDER_DAYS'] or days == app.config['LIST_FINAL_REMINDER_DAYS']:
        print "Sending list email - %s days before event." % days
        to = recipients if recipients else app.config['NOTIFICATION_EMAILS']
        subject = "[Python Glasgow] " + subject
        template = [
            "list-alert-%s.txt" % event.metadata['type'], "list-alert.txt"
        ]

    else:
        print "No emails today. Next event in %s days" % days
        return

    body = render_template(template, event=event, days=days, diff=app.config['ADMIN_REMINDER_DAYS'] - app.config['LIST_REMINDER_DAYS'])

    to = list(to)
    msg = Message(subject, sender="no-reply@dougalmathews.com", recipients=to,
                  body=body, reply_to="glasgow@python.org")

    mail.send(msg)
