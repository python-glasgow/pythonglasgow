from datetime import datetime
import logging

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
        self.when = datetime.strptime(whs, '%Y-%m-%dT%H:%M:%S')

    def date_string(self):
        date_s = self.when.strftime("%A %d%%s of %B")
        date_s = date_s % _nth(self.when.day)
        
        return date_s

    def time_string(self):
        time_s = "%d:%02d" % (self.when.hour % 12, self.when.minute)
        ampm = self.when.strftime("%p").lower()
        
        return time_s + ampm

def next_event():
    next_event = memcache.get("next-event")
    
    if not next_event:
        # Create a Google Calendar client to talk to the Google Calendar service.
        calendar_client = gdata.calendar.service.CalendarService()
        gdata.alt.appengine.run_on_appengine(calendar_client)
                                             
        # Set up a query with the Python Edinburgh calendar ID: 
        query = gdata.calendar.service.CalendarEventQuery(settings.GCAL_ID,
                                                          'public', 'full')
        query.orderby='starttime'
        query.sortorder='ascending'
        query.futureevents='true'
        query.max_results='1'
        
        events = [CalendarEvent(e)
                  for e in calendar_client.CalendarQuery(query).entry]
        next_event = events[0]
        
        if not memcache.add("next-event", next_event, 60 * 60): # 60 mins.
            logging.error("Memcache event store failed.")
            
    return next_event