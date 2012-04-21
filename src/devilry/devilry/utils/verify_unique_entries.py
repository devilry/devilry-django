def verify_unique_entries(iterator):
    unique_dict = {}
    for f in iterator:
        if unique_dict.has_key(str(f)):
            return False
        else:
            unique_dict[str(f)] = ''
    return True
