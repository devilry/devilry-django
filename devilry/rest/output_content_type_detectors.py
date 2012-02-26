"""
Output content type detectors detect the desired content type of the response data.
"""
from devilry.rest.error import InvalidContentTypeError
from devilry.rest.httpacceptheaderparser import HttpAcceptHeaderParser

def suffix(request, suffix, suffix_to_content_type_map, valid_content_types):
    """
    Detect content type from suffix.
    """
    if not suffix:
        return None
    try:
        return suffix_to_content_type_map[suffix]
    except KeyError:
        raise InvalidContentTypeError('Invalid suffix: {0}'.format(suffix))

def _parse_acceptheader(acceptheader, valid_content_types):
    parser = HttpAcceptHeaderParser()
    parser.parse(acceptheader)
    return parser.match(*valid_content_types)

def from_acceptheader(request, suffix, suffix_to_content_type_map, valid_content_types):
    """
    Parse HTTP ACCEPT header to detect the content type.
    """
    acceptheader = request.META.get("HTTP_ACCEPT")
    if not acceptheader:
        return None
    return _parse_acceptheader(acceptheader, valid_content_types)

def devilry_accept_querystringparam(request, suffix, suffix_to_content_type_map, valid_content_types):
    """
    Use the ``_devilry_accept`` querystring parameter to specity content type.
    The value of the querystring parameter is parsed just like a HTTP ACCEPT
    header value. This is mostly for debugging through a browser where
    specifying the ACCEPT header is non-trivial.
    """
    acceptheader = request.GET.get('_devilry_accept')
    if not acceptheader:
        return None
    return _parse_acceptheader(acceptheader, valid_content_types)

#def extjsjson(request, suffix, suffix_to_content_type_map, valid_content_types):
#    print
