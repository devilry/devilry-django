from django.utils import simplejson as json

from errors import InvalidRequestFormatError


def _json_serialize(resultList):
    return json.dumps(dict(total=len(resultList), success=True, items=resultList),
            ensure_ascii = True, # For utf-8 support http://docs.djangoproject.com/en/dev/topics/serialization/#notes-for-specific-serialization-formats
            indent = 2)


def serialize_result(fields, resultList, format):
    """ Serialize a django.db.models.query.ValuesQuerySet """
    if format == 'json':
        return _json_serialize(resultList)
    else:
        raise InvalidRequestFormatError('Unknown format: %s' % format)
