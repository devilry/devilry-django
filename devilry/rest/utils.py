"""
Utility functions for ``rest``.
"""

def str_format_datetime(datetime):
    """
    Format datetime object as ``yyyy-mm-ddThh:mm:ss``.
    """
    return datetime.strftime('%Y-%m-%dT%H:%M:%S')

def request_is_extjs(request):
    """
    Return ``True`` if:

        - ``_devilry_extjs`` is in the querystring (request.GET).
        - The ``X_DEVILRY_USE_EXTJS`` HTTP header is in the request.
    """
    return '_devilry_extjs' in request.GET or 'HTTP_X_DEVILRY_USE_EXTJS' in request.META
