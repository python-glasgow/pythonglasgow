#!/usr/bin/env python

from flask import render_template
from flask.ext.script import Manager
from flask_mail import Message

from app import app, mail
from util.gcal import days_until_next_event, NoEvents
from util.twitter import update_status, send_dm

manager = Manager(app)


@manager.command
def mailer():
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
        to = app.config['ADMINS']
        subject = "[Python Glasgow] (Admin pre-warning) " + subject
        template = "admin-alert.txt"
    elif days == app.config['LIST_REMINDER_DAYS'] or days == app.config['LIST_FINAL_REMINDER_DAYS']:
        print "Sending list email - %s days before event." % days
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


@manager.command
def tweeter():

    try:
        days, event = days_until_next_event()
    except NoEvents:
        print "no events"
        return

    where = event.where.split(',')[0]
    time = event.when.time()
    time_string = "%02d:%02d" % (time.hour, time.minute)

    if days == app.config['ADMIN_REMINDER_DAYS']:
        print "DM to d0ugal"
        send_dm("d0ugal", "Hey - we have an event coming up, have you sorted it?")
    elif days == app.config['LIST_REMINDER_DAYS']:
        print "weekly tweet"
        update_status("The next Python Glasgow event is a {title} in {days} days at {where}. See http://pythonglasgow.org/ for more details.".format(
            title=event.title, where=where, days=days))
    elif days == 0:
        print "on the day tweet."
        update_status("There is a {title} tonight at {time} in {where}. Who's coming? See http://pythonglasgow.org/ for more details.".format(
            title=event.title, time=time_string, where=where))
    else:
        print "No Twitter updates today"

if __name__ == "__main__":
    manager.run()
