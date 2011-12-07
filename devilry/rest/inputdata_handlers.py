def rawbody_inputdata_handler(request, input_content_type, dataconverters):
    dataconverter = dataconverters.get(input_content_type)
    if dataconverter:
        return True, dataconverter.toPython(request.raw_post_data)
    else:
        return False, None