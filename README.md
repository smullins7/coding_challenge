# Coding Challenge App

The DivvyDose coding challenge application is an HTTP service that exposes an endpoint to return a JSON representation of information from Github and Bitbucket.

## Install:

I used `venv` to manage the dependencies, which are in the requirements file: `./requirements.txt`

## Running the code

### Spin up the service

Once the dependencies are installed, start up the service via:
```
python run.py
```

You can also specify auth tokens to Github/Bitbucket:
```
python run.py --github-token MY_GITHUB_TOKEN --bitbucket-token MY_BITBUCKET_TOKEN
```

The service will work without them, but you may get rate limited sooner by Github and/or Bitbucket (unlikely unless you made a large number of requests).

### Making Requests

#### Health check

I left this as is, future work could be to have it ping Github and Bitbucket and return unhealthy if either API does not respond successfully.
```
curl -i "http://127.0.0.1:5000/health-check"
```

#### Profile summary

This is the endpoint for the actual coding challenge. Just specify the organization/team name with the query string parameter _name_ to get the summary, such as:
```
curl -i "http://127.0.0.1:5000/v1/profile?name=mailchimp"
```

should return a result like:
```json
{
  "forked_repositories": 2,
  "languages": {
    "C": 1,
    "No Language Specified": 1,
    "Python": 5,
    "Ruby": 1,
    "c++": 1,
    "python": 5
  },
  "original_repositories": 12,
  "topics": {
    "flask": 1,
    "game-dev": 1,
    "game-development": 1,
    "gamedev": 1,
    "pygame": 2,
    "python": 2,
    "sdl": 1,
    "sdl2": 1,
    "sqlalchemy": 1
  },
  "watchers_count": 2357
}
```

#### Debug endpoints

Get the summary from github
```
curl -i "http://127.0.0.1:5000/v1/debug/github?name=mailchimp"
```

Get the raw data response from github repos endpoint
```
curl -i "http://127.0.0.1:5000/v1/debug/github/repos?name=mailchimp"
```

Get the summary from bitbucket
```
curl -i "http://127.0.0.1:5000/v1/debug/bitbucket?name=mailchimp"
```

Get the raw data response from bitbucket repos endpoint
```
curl -i "http://127.0.0.1:5000/v1/debug/bitbucket/repos?name=mailchimp"
```

## Design Decisions

The following outlines various technical and style design decisions. In general, my approach to software development is to start with small, minimal code and work up from there.
As such, much of this code follows that thinking and does not attempt to future-proof or solve for requirements that were not stated in the problem description. YAGNI can be a powerful
deterrent for over-engineering solutions and stemming accidental complexity.

All that being said, if my solution comes across as _too_ minimal I'd be happy to implement more functionality if that's desired.

### Coding Style

I used [PEP-8](https://www.python.org/dev/peps/pep-0008/) as the style guide for this project.

### API Versions

This service specifies the API version in the URL path (e.g. "/v1/..."). This is a cheap and obvious way to allow for revisions to this service's APIs while not adding any complexity to
the code with just a single version supported. If we never develop a V2 of this application all we did was add three characters to the beginning of the request path. If a new version was
to be supported, it depends on the changes we want to make to these APIs for what code would be re-used or not.

For the dependent service APIs (Github and Bitbucket), there is nothing explicitly in the code to separate by version. If we wanted to support multiple versions of those, it would depend
on the version differences for where this code would adapt. For instance, if the versions are relatively similar but the JSON keys were renamed then that can easily inserted to the existing
parsing code. If, however, the endpoint, data format, and data types changed entirely then we'd be better off separating into distinct classes/modules to handle all the communication and parsing.
All this is to say it depends on the API differences for how to best account for API versioning (in my opinion anyway).

### Performance Concerns

Without scale or performance requirements, I opted for a simpler solution that is synchronous in its request processing. Each request to this service only requires a single request to Github's API
but does require N+1 calls to Bitbucket's API (where N is the number of repositories for the team requested) which makes it slow, taking several seconds to return instead of under a second. If we
wanted to improve on the performance of this service some future work could be:
- cache responses so that repeated queries do not need to make HTTP calls (could be utilized with cache headers like E-Tag/Last-Modified)
- replace requests with [grequests library](https://github.com/spyoungtech/grequests) to parallelize the HTTP calls

### Network/Error handling

I put small place holders for configuring retry policies on errors and timeouts. You could extend this to map different error codes to exceptions or have more fine grained retry policies. That seemed
overkill to start with but I wanted to put something in place to be able to demonstrate timeouts, retries and error handling.

There are other scenarios that we could account for, such as if Github returns an error but Bitbucket returns a successful response. Do we return an error to the client or a partial summary response?
I can see the case for either side so I went with returning an error if either Github or Bitbucket fails, but you could modify the code to return partial responses. At that point, we may want some type
of status indicator in the response to say it was successful (200) but with problems/warnings so that clients can be aware that data is potentially missing and act accordingly.

### Unit Testing

I tried to get decent coverage, using a test library to help test the HTTP request calls. This could have been replaced with a mocking library but I found the responses library more readable/obvious
for testing. I put shared test fixtures in *test_data.py* as I find this helpful to DRY them up. Normally I find myself always using mocks in unit tests with source code that uses more dependency injection,
this project being so small it didn't seem necessary.

### Logging

I kept the logging pretty minimal and didn't include any kind of metrics/monitoring though you'd want that in a production setting.

### Debug endpoints

I find debug endpoints invaluable in the development process, as they can be more accessible than sifting through logs to determine what data was returned for example. 