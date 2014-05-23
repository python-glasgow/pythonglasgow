from os import environ, path
_basedir = path.abspath(path.dirname(__file__))

ADMINS = frozenset(['dougal85@gmail.com'])
CSRF_ENABLED = True
CSRF_SESSION_KEY = environ.get('CSRF_SESSION_KEY')
DATABASE_CONNECT_OPTIONS = {}
DEBUG = False
SECRET_KEY = environ.get('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = environ.get('HEROKU_POSTGRESQL_OLIVE_URL')
THREADS_PER_PAGE = 8
GCAL_ID = '19d0eal34nt9boelm74n7p88vg@group.calendar.google.com'

try:
    MAIL_SERVER = environ['SMTP_HOST']
    MAIL_USE_TLS = True
    MAIL_USERNAME = environ['SMTP_USER']
    MAIL_PASSWORD = environ['SMTP_PASSWORD']
except KeyError as e:
    print "MISSING MAIL SETTINGS."

_TWITTER = ['TWITTER_CONSUMER_KEY', 'TWITTER_ACCESS_TOKEN'
            'TWITTER_CONSUMER_SECRET', 'TWITTER_ACCESS_SECRET']
if all(i not in environ for i in _TWITTER):
    print "MISSING TWITTER SETTINGS."

ADMIN_REMINDER_DAYS = 14
LIST_REMINDER_DAYS = 7
LIST_FINAL_REMINDER_DAYS = 1

# NOTIFICATION_EMAILS = frozenset(['glasgow@python.org'])
# Disabled until I fix my shit.
NOTIFICATION_EMAILS = frozenset(['dougal85@gmail.com'])