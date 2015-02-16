from logging import ERROR
from logging.handlers import SMTPHandler
from os import environ
import warnings

from flask import Flask, render_template, request
from flask.helpers import locked_cached_property
from flask_mail import Mail
from raven.contrib.flask import Sentry
from werkzeug.contrib.cache import SimpleCache

from .util import github


class App(Flask):

    @locked_cached_property
    def sentry(self):
        dsn = environ.get('SENTRY_DSN', None)
        if dsn:
            return Sentry(self, dsn=dsn)
        warnings.warn('Missing Sentry DSN.', UserWarning)

    @locked_cached_property
    def cache(self):
        if self.config['DEBUG']:
            from werkzeug.contrib.cache import NullCache
            return NullCache()
        return SimpleCache()

    @locked_cached_property
    def mail(self):
        return Mail(self)

    def get_github_members(self):
        org = self.config.get('GITHUB_ORG', None)
        if org is None:
            warnings.warn("No Github organization defined.")
            return []
        return github.get_members(org)

    def setup_log_handler(self):
        # Try to setup email logging if details can be found.
        try:
            smtp_server = environ['SMTP_HOST']
            user = environ['SMTP_USER']
            credentials = (user, environ['SMTP_PASSWORD'])
        except KeyError:
            warnings.warn('Missing SMTP configuration.', UserWarning)
        else:
            admins = self.config['ADMINS']
            title = '[www.pythonglasgow.org] 500'
            mail_handler = SMTPHandler(smtp_server, user, admins, title,
                                       credentials=credentials, secure=())
            mail_handler.setLevel(ERROR)
            self.logger.addHandler(mail_handler)

    def setup_debug_toolbar(self):
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(self)


app = App("pythonglasgow", template_folder='ug/templates',
          static_folder='ug/static')
app.config.from_object('ug.config')
app.setup_debug_toolbar()
app.before_first_request_funcs.append(app.setup_log_handler)

# TODO: Fix this. Sentry must be initialised at setup time. There
# are a million better ways to do this, but for now we will just
# access the property to trigger it.
app.sentry


@app.errorhandler(404)
def not_found(error):
    if app.sentry is not None:
        app.sentry.captureMessage("404: %s" % request.url)
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 404


from ug import views  # NOQA
app.register_blueprint(views.mod)
