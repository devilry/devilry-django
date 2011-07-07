""" General purpose utilities used by the simplified API. If any functions here
proves useful outside this module, they should me moved to ``devilry.utils``. """
from django.db.models.fields import related


def _recurse_getmodelattr(instance, path):
    pathseg = path.pop(0)
    try:
        cur = getattr(instance, pathseg)
    except AttributeError, e:
        # NOTE: Dirty hack specifically for candidates
        if repr(type(instance)) == "<class 'django.db.models.fields.related.RelatedManager'>":
            return [getattr(obj, pathseg) for obj in instance.all()]
        return None  # If the foreign relationship we are following is null, we return None
    if not path:
        return cur
    else:
        return _recurse_getmodelattr(cur, path)


def modelinstance_to_dict(instance, fields):
    """ Convert the given django model instance into a dict where
    each field in ``fields`` is a key.

    :param instance: A django model instance.
    :param fields: List of field names. Can also be foreign keys, such as
        ``parentnode__parentnode__short_name``.
    """
    dct = {}
    for field in fields:
        if "__" in field:
            path = field.split('__')
            dct[field] = _recurse_getmodelattr(instance, path)
        else:
            dct[field] = getattr(instance, field)
    return dct
