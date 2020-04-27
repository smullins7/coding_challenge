import re

from flask import current_app

from app.net import get_session
from app.summary import OrgSummary


BASE_URL = "https://api.github.com"
BASE_HEADERS = {
    "Accept": "application/vnd.github.mercy-preview+json",
}
LINK_PATTERN = re.compile('^(?:<[^>]*>; rel="prev", )?<([^>]*)>; rel="next",')
MAX_RESULTS = 100


def get(organization_name):
    org_summary = OrgSummary()
    for repo in get_repos(organization_name):
        org_summary.accumulate(parse_repo(repo))

    return org_summary


def get_repos(organization_name):
    repos_url = f"{BASE_URL}/orgs/{organization_name}/repos"

    for page in call_github(repos_url):
        for repo in page:
            yield repo


def parse_repo(repo_data):
    """
    Takes a full response from Github's repository API and returns the subset of information needed to provide a summary.
    """
    return {k: repo_data[k] for k in ("private", "language", "fork", "watchers_count", "topics")}


def get_headers():
    github_token = current_app.config.get("github_token")
    if github_token:
        return {**BASE_HEADERS, "Authorization": f"token {github_token}"}

    return BASE_HEADERS


def call_github(url):
    """
    Generator that makes an external network call to Github's API, yielding the json response.

    If the response contains a link header, that is used to provide pagination.
    """
    current_app.logger.info("Calling %s with %s", url, get_headers())
    r = get_session().get(url, headers=get_headers(), params={"per_page": MAX_RESULTS})
    r.raise_for_status()

    json_response = r.json()
    current_app.logger.debug("Got response %s", json_response)

    yield json_response

    next_page_url = parse_next_page_url(r.headers.get("Link"))
    current_app.logger.info("next: %s", next_page_url)
    if next_page_url:
        yield from call_github(next_page_url)


def parse_next_page_url(link_header):
    """
    Parse the next URL from the Link header if available, returns false otherwise.

    See https://developer.github.com/v3/guides/traversing-with-pagination/ for details on the pagination API.
    """
    current_app.logger.info("parsing link header: %s", link_header)
    if not link_header:
        return False

    matcher = LINK_PATTERN.match(link_header)
    return matcher and len(matcher.groups()) == 1 and matcher.group(1)
