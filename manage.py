#!/usr/bin/env python

from flask import render_template
from flask.ext.script import Manager
from flask_mail import Message

from app import app, mail
from util.gcal import days_until_next_event, NoEvents

manager = Manager(app)


@manager.command
def mailer():
    """Send notification emails."""

    """
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
        return

    where = event.where.split(',')[0]

    subject = " %s on %s in %s" % (event.title, event.date_string(), where)

    if days == app.config['ADMIN_REMINDER_DAYS']:
        print "Sending Admin e-mail" % days
        to = app.config['ADMINS']
        subject = "[Python Glasgow] (Admin pre-warning) " + subject
        template = "admin-alert.txt"
    elif days == app.config['LIST_REMINDER_DAYS']:
        print "Sending list email"
        to = app.config['NOTIFICATION_EMAILS']
        subject = "[Python Glasgow] " + subject
        template = "list-alert.txt"
    else:
        print "No emails today. Next event in %s days" % days
        return

    body = render_template(template, event=event, days=days, diff=app.config['ADMIN_REMINDER_DAYS'] - app.config['LIST_REMINDER_DAYS'])

    msg = Message(subject,
        sender="no-reply@dougalmathews.com",
        recipients=to,
        body=body,
        reply_to="glasgow@python.org")

    mail.send(msg)

if __name__ == "__main__":
    manager.run()
