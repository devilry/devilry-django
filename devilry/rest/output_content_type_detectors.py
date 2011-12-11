from devilry.rest.error import InvalidContentTypeError
from devilry.rest.httpacceptheaderparser import HttpAcceptHeaderParser

def suffix(request, suffix, suffix_to_content_type_map, valid_content_types):
    if not suffix:
        return None
    try:
        return suffix_to_content_type_map[suffix]
    except KeyError:
        raise InvalidContentTypeError('Invalid suffix: {0}'.format(suffix))

def _parse_acceptheader(acceptheader, valid_content_types):
    parser = HttpAcceptHeaderParser()
    print acceptheader, valid_content_types
    parser.parse(acceptheader)
    return parser.match(*valid_content_types)

def from_acceptheader(request, suffix, suffix_to_content_type_map, valid_content_types):
    acceptheader = request.META.get("HTTP_ACCEPT")
    if not acceptheader:
        return None
    print acceptheader
    return _parse_acceptheader(acceptheader, valid_content_types)

def devilry_accept_querystringparam(request, suffix, suffix_to_content_type_map, valid_content_types):
    acceptheader = request.GET.get('_devilry_accept')
    if not acceptheader:
        return None
    return _parse_acceptheader(acceptheader, valid_content_types)