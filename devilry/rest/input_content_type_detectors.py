def from_content_type_header(request, suffix, suffix_to_content_type_map, valid_content_types, output_content_type):
    return request.META.get('CONTENT_TYPE')

def use_output_content_type(request, suffix, ouput_content_type):
    return ouput_content_type
