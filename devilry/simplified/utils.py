""" General purpose utilities used by the simplified API. If any functions here
proves useful outside this module, they should me moved to ``devilry.utils``. """


def _recurse_getmodelattr(instance, path):
    cur = getattr(instance, path.pop(0))
    if not path:
        return cur
    else:
        return _recurse_getmodelattr(cur, path)

def model_to_dict(instance, fields):
    dct = {}
    for field in fields:
        if "__" in field:
            path = field.split('__')
            dct[field] = _recurse_getmodelattr(instance, path)
        else:
            dct[field] = getattr(instance, field)
    return dct
