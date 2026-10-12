from django.http import QueryDict
from urllib.parse import urlsplit, urlunsplit


def create_querydict(querystringargs, initial_query_string=None, ignore_none_values=True):
    """
    Parameters:
        querystringargs (dict): The querystring args to add/replace.
        initial_query_string (str): The initial querystring. Any ovelapping
            keys between this and ``querystringargs`` is overridden by
            the value in ``querystringargs``.
        ignore_none_values (bool): If this is ``True`` (default),
            we ignore ``None`` values in ``querystringargs``.

    Returns:
        The created :class:`django.http.request.QueryDict`.
    """
    querydict = QueryDict(query_string=initial_query_string, mutable=True)
    for key, value in querystringargs.items():
        if ignore_none_values and value is None:
            continue
        querydict[key] = value
    return querydict


def update_querystring(url, querystringargs, ignore_none_values=True):
    """
    Update the querystring portion of the given ``url``.

    Parameters:
        querystringargs (dict): The querystring args to add/replace.
        ignore_none_values (bool): If this is ``True`` (default),
            we ignore ``None`` values in ``querystringargs``.

    Returns:
        The updated url.

    Examples:

        Add querystring argument::

            from cradmin_legacy import urlutils
            urlutils.update_querystring('http://example.com', {'search': 'test'})

        Update querystring argument::

            urlutils.update_querystring('http://example.com?search=something&page=2',
                {'search': 'updated'})
    """
    parsed_url = urlsplit(url)
    querydict = create_querydict(
        querystringargs=querystringargs, initial_query_string=parsed_url.query, ignore_none_values=ignore_none_values
    )
    return urlunsplit(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, querydict.urlencode(), parsed_url.fragment)
    )
