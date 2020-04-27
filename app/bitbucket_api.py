from flask import current_app

from app.net import get_session
from app.summary import OrgSummary


BASE_URL = "https://api.bitbucket.org/2.0"


class PaginatedResponse(object):
    """
    An iterator that represents a paginated response from Bitbucket.

    See https://developer.atlassian.com/bitbucket/api/2/reference/meta/pagination
    """

    def __init__(self, json_response):
        self.json_response = json_response
        self.result_size = self.json_response.get("size", -1)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.json_response:
            raise StopIteration

        values = self.json_response["values"]
        next_page_url = self.json_response.get("next")
        self.json_response = call_bitbucket(next_page_url) if next_page_url else None
        return values

    def size(self):
        """
        Returns the size of the result set if available, -1 otherwise
        """
        return self.result_size


def get(organization_name):
    org_summary = OrgSummary()
    for repo in get_repos(organization_name):
        repo_summary = parse_repo(repo)
        repo_summary["watchers_count"] = get_watchers_count(repo_summary.pop("watchers_ref"))
        org_summary.accumulate(repo_summary)

    return org_summary


def parse_repo(repo_data):
    return {
        "private": repo_data.get("is_private", False),
        "language": repo_data.get("language", None),
        "fork": "parent" in repo_data,
        "watchers_ref": repo_data.get("links", {}).get("watchers", {}).get("href", "")
    }


def get_repos(organization_name):
    url = f"{BASE_URL}/repositories/{organization_name}"

    for values in PaginatedResponse(call_bitbucket(url)):
        for repo in values:
            yield repo


def get_watchers_count(watcher_url):
    """
    Given a watcher URL, calculate the total number of watchers.

    The response may contain a size field in which case we use that, but if not available fall back to "paging" through
    the result set to sum up the number of results.
    See https://developer.atlassian.com/bitbucket/api/2/reference/meta/pagination
    """
    if not watcher_url:
        return 0

    response = PaginatedResponse(call_bitbucket(watcher_url))
    if response.size() >= 0:
        return response.size()

    return sum([len(values) for values in response if values])


def get_headers():
    bitbucket_token = current_app.config.get("bitbucket_token")
    if bitbucket_token:
        return {"Authorization": f"Bearer  {bitbucket_token}"}

    return {}


def call_bitbucket(url):
    current_app.logger.info("Calling %s", url)
    r = get_session().get(url, headers=get_headers())
    r.raise_for_status()

    json_response = r.json()
    current_app.logger.debug("Got response %s", json_response)

    return json_response
