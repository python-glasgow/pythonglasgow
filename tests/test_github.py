from unittest2 import TestCase

from mock import patch
from requests import Response

from ug import app


class GithubTestCase(TestCase):

    @patch('ug.util.github.get')
    def test_get_members(self, mock_get):
        response = Response()
        response.status_code = 200
        response._content = "[]"
        mock_get.return_value = response
        self.assertEquals(app.get_github_members(), [])
