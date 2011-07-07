class RestfulError(Exception):
    """ Raised when the restful call returns a JSON data containing an
    errormsg. """

class HttpResponseBadRequest(RestfulError):
    """ Raised on HTTP ``400 Bad Request`` response. """

class HttpResponseUnauthorized(RestfulError):
    """ """

class HttpResponseForbidden(RestfulError):
    """ Raised on HTTP ``403 Forbidden`` response. """

class HttpResponseNotFound(RestfulError):
    """ Raised on HTTP ``404 Not Found`` response. """



