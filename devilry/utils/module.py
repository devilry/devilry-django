def dump_all_into_dict(module):
    """ Dump ``module.__all__ into a dict, and return the dict. """
    dct = {}
    for clsname in module.__all__:
        dct[clsname] = getattr(module, clsname)
    return dct
