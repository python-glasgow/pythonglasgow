from os import environ

from logging import ERROR
from logging.handlers import SMTPHandler
from flask import Flask, render_template
from werkzeug.contrib.cache import SimpleCache


def create_app():
    return Flask("pythonglasgow", template_folder='app/templates',
        static_folder='app/static')

app = create_app()
app.config.from_object('config')

cache = SimpleCache()

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
        app.config['ADMINS'], '[www.pythonglasgow.org] 500', credentials=credentials)
    mail_handler.setLevel(ERROR)
    app.logger.addHandler(mail_handler)

except KeyError as e:
    pass


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 404

from app import views
app.register_blueprint(views.mod)
