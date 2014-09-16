import warnings
from os import environ, path


_basedir = path.abspath(path.dirname(__file__))


THREADS_PER_PAGE = 8
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_DATABASE_URI = environ.get('HEROKU_POSTGRESQL_OLIVE_URL')

SECRET_KEY = environ.get('SECRET_KEY')
CSRF_ENABLED = True
CSRF_SESSION_KEY = environ.get('CSRF_SESSION_KEY')

ADMINS = frozenset(['dougal85@gmail.com'])
DEBUG = False
MAIL_USE_TLS = True
try:
    MAIL_SERVER = environ['SMTP_HOST']
    MAIL_USERNAME = environ['SMTP_USER']
    MAIL_PASSWORD = environ['SMTP_PASSWORD']
except KeyError as e:
    warnings.warn("Missing mail settings.", UserWarning)

GITHUB_ORG = "python-glasgow"
GCAL_ID = '19d0eal34nt9boelm74n7p88vg@group.calendar.google.com'
_TWITTER = ['TWITTER_CONSUMER_KEY', 'TWITTER_ACCESS_TOKEN'
            'TWITTER_CONSUMER_SECRET', 'TWITTER_ACCESS_SECRET']
if not all(i in environ for i in _TWITTER):
    warnings.warn("Missing twitter settings.", UserWarning)

ADMIN_REMINDER_DAYS = 14
LIST_REMINDER_DAYS = 7
LIST_FINAL_REMINDER_DAYS = 1
# NOTIFICATION_EMAILS = frozenset(['glasgow@python.org'])
# Disabled until I fix my shit.
NOTIFICATION_EMAILS = frozenset(['dougal85@gmail.com'])
