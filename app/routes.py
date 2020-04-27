import flask
from flask import Response
from flask import jsonify, request
from requests import HTTPError

from app import bitbucket_api, github_api
from app.errors import ClientRequestError
from app.summary import combine

app = flask.Flask("user_profiles_api")


@app.route("/health-check", methods=["GET"])
def health_check():
    """
    Endpoint to health check API
    """
    app.logger.info("Health Check!")
    return Response("All Good!", status=200)


@app.route("/v1/profile", methods=["GET"])
def profile():
    """
    Returns the combined organization/team profile from Github and Bitbucket.

    If any error occurs in either service, a 400 is returned to the client.
    """
    try:
        entity_name = request.args.get('name')
        return jsonify(combine(github_api.get(entity_name), bitbucket_api.get(entity_name)).asdict())
    except HTTPError as e:
        app.logger.error("Unable to construct profile: %s", e)

        raise ClientRequestError(str(e))


@app.route("/v1/debug/github", methods=["GET"])
def debug_github():
    """
    Returns the Github organization summary
    """
    return jsonify(github_api.get(request.args.get('name')).asdict())


@app.route("/v1/debug/github/repos", methods=["GET"])
def debug_github_repos():
    """
    Returns the raw Github repos response
    """
    return jsonify(list(github_api.get_repos(request.args.get('name'))))


@app.route("/v1/debug/bitbucket", methods=["GET"])
def debug_bitbucket():
    """
    Returns the Bitbucket team summary
    """
    return jsonify(bitbucket_api.get(request.args.get('name')).asdict())


@app.route("/v1/debug/bitbucket/repos", methods=["GET"])
def debug_bitbucket_repos():
    """
    Returns the raw Bitbucket repos response
    """
    return jsonify(list(bitbucket_api.get_repos(request.args.get('name'))))


@app.errorhandler(ClientRequestError)
def handle_not_found(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
