import logging
import datetime

from google.appengine.api import memcache

import gdata.alt.appengine
import gdata.calendar.service

import settings


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
        try:
            self.when = datetime.datetime.strptime(whs, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            self.when = ""
        self.where = atom_ob.where[0].value_string

    def date_string(self):
        if self.when:
            date_s = self.when.strftime("%A %d%%s of %B")
            date_s = date_s % _nth(self.when.day)

            return date_s
        return ""

    def time_string(self):
        if self.when:
            time_s = "%d:%02d" % (self.when.hour % 12, self.when.minute)
            ampm = self.when.strftime("%p").lower()

            return time_s + ampm
        return ""


def upcoming_events():
    upcoming_events = memcache.get("upcoming-events")

    if not upcoming_events:
        # Create a Google Calendar client to talk to the Google Calendar service.
        calendar_client = gdata.calendar.service.CalendarService()
        gdata.alt.appengine.run_on_appengine(calendar_client)

        # Set up a query with the Python Edinburgh calendar ID:
        query = gdata.calendar.service.CalendarEventQuery(settings.GCAL_ID,
                                                          'public', 'full')
        query.orderby = 'starttime'
        query.sortorder = 'ascending'

        # we're interested in events in the next 30 days
        # if we wanted all the futuer events, we'd use
        # query.futureevents='true'
        # and ignore the start_min, start_max options
        month_offset = datetime.timedelta(days=30)

        start_min = datetime.datetime.now()
        start_max = start_min + month_offset

        query.start_min = start_min.isoformat()
        query.start_max = start_max.isoformat()

        # query gcal for the time interval
        events = [CalendarEvent(e)
                for e in calendar_client.CalendarQuery(query).entry]

        upcoming_events = events

        if not memcache.add("upcoming-events", upcoming_events, 60 * 60):  # 60 mins.
            logging.error("Memcache event store failed.")

    return upcoming_events
