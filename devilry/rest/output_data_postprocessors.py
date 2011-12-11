def extjs(request, output_data, successful):
    if '_devilry_extjs' in request.GET:
        if isinstance(output_data, dict):
            output_data['successful'] = successful
        return True, output_data
    return False, None