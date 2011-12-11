def extjs(output_data):
    if isinstance(output_data, dict):
        output_data['successful'] = True
    return output_data