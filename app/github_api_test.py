import unittest

import flask
from requests import HTTPError
import responses

from app.github_api import parse_repo, get_repos, get, parse_next_page_url
from app.test_data import *


app = flask.Flask(__name__)


class GithubApiTestCase(unittest.TestCase):

    def test_parse_repo(self):
        self.assertEqual(REPO_PUBLIC, parse_repo(REPO_PUBLIC))

    @responses.activate
    def test_get_repos(self):
        with app.app_context():
            responses.add(responses.GET, 'https://api.github.com/orgs/org-1/repos',
                          json=[{'unit-test': 'data'}], status=200)

            self.assertEqual([{"unit-test": "data"}], list(get_repos("org-1")))
            self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_get_repos_errors_raised(self):
        with app.app_context():
            responses.add(responses.GET, 'https://api.github.com/orgs/org-1/repos',
                          json={'error': 'barf'}, status=404)

            with self.assertRaises(HTTPError):
                list(get_repos("org-1"))

            self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_get(self):
        with app.app_context():
            responses.add(responses.GET, 'https://api.github.com/orgs/org-1/repos',
                          json=[REPO_PUBLIC, REPO_PRIVATE, REPO_PUBLIC_FORK], status=200)

            self.assertEqual({
              "forked_repositories": 1,
              "languages": {
                  "Python": 1,
                  "Javascript": 1
              },
              "original_repositories": 1,
              "topics": {
                  "programming": 2,
                  "front-end": 1,
                  "fun": 1,
              },
              "watchers_count": 3}, get("org-1").asdict())
            self.assertEqual(1, len(responses.calls))

    def test_parse_next_page_url(self):
        with app.app_context():
            first_url = "https://api.github.com/organizations/4314092/repos?per_page=20&page=1"
            next_url = "https://api.github.com/organizations/4314092/repos?per_page=20&page=2"
            last_url = "https://api.github.com/organizations/4314092/repos?per_page=20&page=3"
            self.assertEqual(next_url, parse_next_page_url(f'<{first_url}>; rel="prev", <{next_url}>; rel="next", <{last_url}>; rel="last"'))
            self.assertFalse(parse_next_page_url(None))
            self.assertFalse(parse_next_page_url(""))
            self.assertFalse(parse_next_page_url("malformed header value that cannot be parsed"))


if __name__ == '__main__':
    unittest.main()
