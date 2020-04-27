import unittest

from app.summary import OrgSummary, combine
from app.test_data import *


class MyTestCase(unittest.TestCase):

    def test_accumulate(self):
        org_summary = OrgSummary()
        org_summary.accumulate(REPO_PUBLIC)
        org_summary.accumulate(REPO_PRIVATE)
        org_summary.accumulate(REPO_PUBLIC_FORK)
        org_summary.accumulate({"language": None})
        self.assertEqual({
            "original_repositories": 2,
            "forked_repositories": 1,
            "watchers_count": 3,
            "languages": {
                "Python": 1,
                "Javascript": 1,
                "No Language Specified": 1
            },
            "topics": {
                "programming": 2,
                "fun": 1,
                "front-end": 1
            }
        }, org_summary.asdict())

    def test_combine(self):
        # not inlining for readability
        expected = OrgSummary(original_repositories=1,
                              forked_repositories=2,
                              watchers=3,
                              languages={
                                  "Python": 2
                              },
                              topics={
                                  "programming": 1,
                                  "fun": 1
                              })
        actual = combine(OrgSummary(original_repositories=1,
                                    forked_repositories=1,
                                    watchers=1,
                                    languages={
                                        "Python": 1
                                    },
                                    topics={
                                        "programming": 1
                                    }),
                         OrgSummary(original_repositories=0,
                                    forked_repositories=1,
                                    watchers=2,
                                    languages={
                                        "Python": 1
                                    },
                                    topics={
                                        "fun": 1
                                    })
                         )
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
