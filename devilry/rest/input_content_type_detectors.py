import re

content_type_patt = re.compile('^([a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+)(?:.*?charset=([a-zA-Z0-9_-]+))?$')

def parse_content_type(content_type):
    return content_type_patt.match(content_type).groups()

def from_content_type_header(request, suffix, suffix_to_content_type_map, valid_content_types, output_content_type):
    content_type = request.META.get('CONTENT_TYPE')
    if content_type:
        return parse_content_type(content_type)
    else:
        return None

def use_output_content_type(request, suffix, output_content_type):
    return (output_content_type, None)
