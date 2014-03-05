from unittest import TestCase
from flask.ext.webtest import TestApp
from ug import app


class ViewsTestCase(TestCase):

    def setUp(self):
        self.app = app
        self.w = TestApp(self.app)

    def test(self):

        r = self.w.get('/')

        self.assertEquals(r.status_code, 200)
