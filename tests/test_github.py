from unittest2 import TestCase

from mock import patch

from ug.util.github import get_members


class GithubTestCase(TestCase):

    @patch('ug.util.github.get')
    def test_get_members(self, mock_get):

        self.assertEquals(list(get_members()), [])
