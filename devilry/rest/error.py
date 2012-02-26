class RestError(Exception):
    """
    Base class for REST errors.
    """

class UnsupportedHttpMethodError(RestError):
    """
    Unsupported method.
    """
    pass


class NotFoundError(RestError):
    """
    404 not found
    """

class InvalidContentTypeError(RestError):
    """
    Invalid content type.
    """
