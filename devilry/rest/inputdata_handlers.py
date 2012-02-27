def flatten_querydata(querydata):
    """
    GET/POST data are often received as tuples. This function replaces each tuple-value with its first item.
    """

    def flatten(value):
        if isinstance(value, tuple):
            return value[0]
        else:
            return value

    return dict((key, flatten(value)) for key, value in querydata.iteritems())


def getqrystring_inputdata_handler(request, input_content_type, dataconverters):
    """
    Use ``request.GET`` if method is GET and the request body is empty.
    """
    if request.method == "GET":
        use_qrystring = request.raw_post_data.strip() == ""
        if use_qrystring:
            querydata = flatten_querydata(request.GET)
            return True, querydata
    return False, None


def rawbody_inputdata_handler(request, input_content_type, dataconverters):
    """
    Get inputdata from the request body. This should work with all modern browsers, however
    research indicates that there exists browsers/clients that may not support data in
    the request body of GET requests.
    """
    dataconverter = dataconverters.get(input_content_type)
    if dataconverter and request.raw_post_data:
        return True, dataconverter.toPython(request.raw_post_data)
    else:
        return False, None

def noinput_inputdata_handler(*args):
    """
    Returns ``(True, {})``. Suitable for fallback when no other inputdata
    handler can find any input data (which may be the case for requests that
    only require an ID, such as DELETE).
    """
    return True, {}
