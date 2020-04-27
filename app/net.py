import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


DEFAULT_TIMEOUT_S = 5
RETRIES = 3
BACKOFF = 0.2
RETRY_STATUSES = [500, 502, 504]


class TimeoutAdapter(HTTPAdapter):
    """
    An adapter that supplies a default timeout if one is not provided
    """

    def send(self, request, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = DEFAULT_TIMEOUT_S
        return super().send(request, **kwargs)


def get_session():
    """
    Returns a requests session with retry and timeout logic configured for all requests
    """
    http = requests.Session()

    retry = Retry(
        total=RETRIES,
        read=RETRIES,
        connect=RETRIES,
        backoff_factor=BACKOFF,
        status_forcelist=RETRY_STATUSES,
    )
    adapter = TimeoutAdapter(max_retries=retry)
    http.mount("http://", adapter)
    http.mount("https://", adapter)

    return http

