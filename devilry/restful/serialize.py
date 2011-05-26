from django.utils import simplejson as json

from errors import InvalidRequestFormatError


def _json_serialize(resultQry):
    result = list(resultQry)
    return json.dumps(result,
            ensure_ascii = True, # For utf-8 support http://docs.djangoproject.com/en/dev/topics/serialization/#notes-for-specific-serialization-formats
            indent = 2)


def serialize_result(fields, resultQry, format):
    """ Serialize a django.db.models.query.ValuesQuerySet """
    if format == 'json':
        return _json_serialize(resultQry.values(*fields))
    else:
        raise InvalidRequestFormatError('Unknown format: %s' % format)
