from app.routes import app
import argparse
import flask
import logging


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-token", help="A github authorization token")
    parser.add_argument("--bitbucket-token", help="A bitbucket authorization token")
    parser.add_argument("--log-level", help="The logging level for the application, defaults to INFO", default="INFO",
                        choices=["DEBUG", "INFO", "WARN", "ERROR"])
    args = parser.parse_args()

    app.config["github_token"] = args.github_token
    app.config["bitbucket_token"] = args.bitbucket_token
    logger = flask.logging.create_logger(app)
    logger.setLevel(logging.getLevelName(args.log_level))

    app.run(debug=True)
