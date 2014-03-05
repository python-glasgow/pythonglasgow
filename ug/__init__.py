from os import environ

from logging import ERROR
from logging.handlers import SMTPHandler
from flask import Flask, render_template, request
from flask_mail import Mail
from raven.contrib.flask import Sentry
from werkzeug.contrib.cache import SimpleCache

__version__ = '1.0'


def create_app():
    return Flask("pythonglasgow", template_folder='ug/templates',
                 static_folder='ug/static')

app = create_app()
app.config.from_object('ug.config')

try:
    sentry = Sentry(app, dsn=environ['SENTRY_DSN'])
except KeyError:
    sentry = None
    print "MISSING SENTRY_DSN"

cache = SimpleCache()
mail = Mail(app)

# For DEBUG, enable the debug toolbar and set the cach to be the NullCache.
if app.config['DEBUG']:
    from flask_debugtoolbar import DebugToolbarExtension
    from werkzeug.contrib.cache import NullCache
    toolbar = DebugToolbarExtension(app)
    cache = NullCache()

# Try to setup email logging if details can be found.
try:
    smtp_server = environ['SMTP_HOST']
    credentials = (environ['SMTP_USER'], environ['SMTP_PASSWORD'])

    mail_handler = SMTPHandler(smtp_server, environ['SMTP_USER'],
                               app.config['ADMINS'],
                               '[www.pythonglasgow.org] 500',
                               credentials=credentials, secure=())
    mail_handler.setLevel(ERROR)
    app.logger.addHandler(mail_handler)

except KeyError:
    pass


@app.errorhandler(404)
def not_found(error):
    if sentry:
        sentry.captureMessage("404: %s" % request.url)
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 404

from ug import views
app.register_blueprint(views.mod)
