def verify_unique_entries(iterator):
    unique_dict = {}
    for f in iterator:
        if str(f) in unique_dict:
            return False
        else:
            unique_dict[str(f)] = ''
    return True
