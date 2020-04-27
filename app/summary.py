from collections import defaultdict
from dataclasses import dataclass, field
import itertools


@dataclass
class OrgSummary:
    """
    OrgSummary represents the aggregation of all organization/team information from multiple sources.

    It acts as an accumulator and can output its accumulated values via the _asdict_ method.
    """
    original_repositories: int = 0
    forked_repositories: int = 0
    watchers: int = 0
    languages: dict = field(default_factory=lambda: defaultdict(int))
    topics: dict = field(default_factory=lambda: defaultdict(int))

    def accumulate(self, repo_summary):
        """
        Accumulate a repository summary into this organization summary, example:
        {
            "private": False,
            "language": "Python",
            "fork": True,
            "watchers_count": 10,
            "topics": [
                "programming",
                "scaling"
            ]
        }
        """
        if repo_summary.get("private", False):
            return

        if repo_summary.get("fork", False):
            self.forked_repositories += 1
        else:
            self.original_repositories += 1

        for topic in repo_summary.get("topics", []):
            self.topics[topic] += 1

        self.watchers += repo_summary.get("watchers_count", 0)
        self.languages[repo_summary["language"] or "No Language Specified"] += 1

    def asdict(self):
        return {
            "original_repositories": self.original_repositories,
            "forked_repositories": self.forked_repositories,
            "watchers_count": self.watchers,
            "languages": dict(self.languages),
            "topics": self.topics
        }


def combine(org_summary_1, org_summary_2):
    """
    Combine two org summaries together in additive fashion into a new org summary.

    It's a gross function
    """
    topics = defaultdict(int)
    for topic, count in itertools.chain(org_summary_1.topics.items(), org_summary_2.topics.items()):
        topics[topic] += count

    languages = defaultdict(int)
    for language, count in itertools.chain(org_summary_1.languages.items(), org_summary_2.languages.items()):
        languages[language] += count

    return OrgSummary(forked_repositories=org_summary_1.forked_repositories + org_summary_2.forked_repositories,
                      original_repositories=org_summary_1.original_repositories + org_summary_2.original_repositories,
                      watchers=org_summary_1.watchers + org_summary_2.watchers,
                      topics=topics,
                      languages=languages)
