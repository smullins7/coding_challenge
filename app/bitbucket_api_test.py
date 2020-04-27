import unittest

import flask
import responses
from requests import HTTPError

from app.bitbucket_api import PaginatedResponse, parse_repo, get_repos, get, get_watchers_count


app = flask.Flask(__name__)


class BitbucketApiTestCase(unittest.TestCase):

    def test_parse_repo(self):
        self.assertEqual({
            "private": False,
            "language": "Python",
            "fork": False,
            "watchers_ref": "some-link"
        }, parse_repo({
            "is_private": False,
            "language": "Python",
            "links": {
                "watchers": {
                    "href": "some-link"
                }
            }
        }))
        self.assertEqual({
            "private": False,
            "language": "Python",
            "fork": False,
            "watchers_ref": ""
        }, parse_repo({
            "is_private": False,
            "language": "Python"
        }))

    @responses.activate
    def test_get_repos(self):
        with app.app_context():
            responses.add(responses.GET, "https://api.bitbucket.org/2.0/repositories/org-1",
                          json={"values": [{"unit-test": "data"}]}, status=200)

            self.assertEqual([{"unit-test": "data"}], list(get_repos("org-1")))
            self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_get_repos_errors_raised(self):
        with app.app_context():
            responses.add(responses.GET, "https://api.bitbucket.org/2.0/repositories/org-1",
                          json={'error': 'barf'}, status=404)

            with self.assertRaises(HTTPError):
                list(get_repos("org-1"))

            self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_get(self):
        with app.app_context():
            responses.add(responses.GET, "https://api.bitbucket.org/2.0/repositories/org-1",
                          json={"values": [{"is_private": False, "parent": 1, "language": "Python"},
                                           {"is_private": True},
                                           {"is_private": False, "language": "Javascript"}]}, status=200)

            self.assertEqual({
                "forked_repositories": 1,
                "languages": {
                    "Python": 1,
                    "Javascript": 1
                },
                "original_repositories": 1,
                "topics": {},
                "watchers_count": 0}, get("org-1").asdict())
            self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_get_watchers_count(self):
        with app.app_context():
            responses.add(responses.GET, "http://dummy-url",
                          json={"values": ["watcher-1", "watcher-2"], "next": "http://dummy-url-2"}, status=200)
            responses.add(responses.GET, "http://dummy-url-2",
                          json={"values": ["watcher-3"]}, status=200)

            self.assertEqual(3, get_watchers_count("http://dummy-url"))
            self.assertEqual(2, len(responses.calls))

    @responses.activate
    def test_get_watchers_count_use_size(self):
        with app.app_context():
            responses.add(responses.GET, "http://dummy-url",
                          json={"size": 3, "values": ["watcher-1", "watcher-2"], "next": "http://dummy-url-2"}, status=200)

            self.assertEqual(3, get_watchers_count("http://dummy-url"))
            self.assertEqual(1, len(responses.calls))

    def test_paginated_response_single(self):
        response = PaginatedResponse({"size": 2, "values": ["foo", "bar"]})
        self.assertEqual(2, response.size())
        self.assertEqual(["foo", "bar"], next(response))
        with self.assertRaises(StopIteration):
            next(response)

    @responses.activate
    def test_paginated_response_multiple(self):
        with app.app_context():
            responses.add(responses.GET, "http://next-1",
                          json={"values": ["baz"]}, status=200)

            response = PaginatedResponse({"values": ["foo", "bar"], "next": "http://next-1"})
            self.assertEqual(-1, response.size())
            self.assertEqual(["foo", "bar"], next(response))
            self.assertEqual(["baz"], next(response))
            with self.assertRaises(StopIteration):
                next(response)


if __name__ == '__main__':
    unittest.main()
