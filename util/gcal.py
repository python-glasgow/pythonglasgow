from datetime import datetime, timedelta

from gdata.calendar.service import CalendarService, CalendarEventQuery

from app import app


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

    def date_string(self):
        date_s = self.when.strftime("%A %d%%s of %B")
        date_s = date_s % _nth(self.when.day)

        return date_s

    def time_string(self):
        time_s = "%d:%02d" % (self.when.hour % 12, self.when.minute)
        ampm = self.when.strftime("%p").lower()

        return time_s + ampm


def upcoming_events(days=60):

    # Create a Google Calendar client to talk to the Google Calendar service.
    calendar_client = CalendarService()

    # Set up a query with the GCAL_ID.
    query = CalendarEventQuery(app.config['GCAL_ID'], 'public', 'full')
    query.orderby = 'starttime'
    query.sortorder = 'ascending'

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
        raise Exception("No events planned")

    event = events[0]
    until_event = event.when - datetime.now()

    return until_event.days, event
