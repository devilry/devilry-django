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
    If the ``_devilry_qrystringindata`` key is available in the querystring (``request.GET``), this
    input handler will fetch input data from the querystring. This is mainly useful for debugging.
    """
    key = "_devilry_qrystringindata"
    use_qrystring = request.GET.get(key)
    if use_qrystring:
        querydata = flatten_querydata(request.GET)
        del querydata[key]
        return True, querydata
    else:
        return False, None


def rawbody_inputdata_handler(request, input_content_type, dataconverters):
    """
    Get inputdata from the request body. This should work with all modern browsers, however
    research indicates that there exists browsers/clients that may not support data in
    the request body of GET requests.
    """
    dataconverter = dataconverters.get(input_content_type)
    if dataconverter:
        return True, dataconverter.toPython(request.raw_post_data)
    else:
        return False, None