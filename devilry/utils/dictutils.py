def subdict(dct, *keys):
    return dict((key, dct[key]) for key in keys)


def todict(obj, *attrs):
    return dict((attr, getattr(obj, attr)) for attr in attrs)