from logging import DEBUG
from logging.handlers import SMTPHandler
from os import environ
import warnings

from flask import Flask, render_template
from flask.helpers import locked_cached_property
from flask_mail import Mail
from werkzeug.contrib.cache import SimpleCache


class App(Flask):

    @locked_cached_property
    def cache(self):
        if self.config['DEBUG']:
            from werkzeug.contrib.cache import NullCache
            return NullCache()
        return SimpleCache()

    @locked_cached_property
    def mail(self):
        return Mail(self)

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
            mail_handler.setLevel(DEBUG)
            self.logger.addHandler(mail_handler)

    def setup_debug_toolbar(self):
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(self)


app = App("pythonglasgow", template_folder='ug/templates',
          static_folder='ug/static')
app.config.from_object('ug.config')
app.setup_debug_toolbar()
app.before_first_request_funcs.append(app.setup_log_handler)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 404


from ug import views  # NOQA
app.register_blueprint(views.mod)
