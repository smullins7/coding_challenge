class ClientRequestError(Exception):
    """
    A simple application error to register with Flask, maps to a 400 error and returns the error and status code
    """
    status_code = 400

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def to_dict(self):
        return {
            "message": self.message,
            "status_code": self.status_code
        }
