def flatten_querydata(querydata):
    """
    GET/POST data are lists. This function maps the first item in the list to its key.
    """
    def flatten(value):
        if isinstance(value, tuple):
            return value[0]
        else:
            return value
    return dict((key, flatten(value)) for key, value in querydata.iteritems())

def getqrystring_inputdata_handler(request, input_content_type, dataconverters):
    """

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
    dataconverter = dataconverters.get(input_content_type)
    if dataconverter:
        return True, dataconverter.toPython(request.raw_post_data)
    else:
        return False, None