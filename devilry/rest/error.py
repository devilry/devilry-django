class RestError(Exception):
    pass


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