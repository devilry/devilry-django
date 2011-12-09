import json
from devilry.dataconverter.dataconverter import DataConverter

from utils import str_format_datetime


def json_serialize_handler(obj):
    if hasattr(obj, 'isoformat'):
        return str_format_datetime(obj)
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (
            type(obj), repr(obj)))


class JsonDataConverter(DataConverter):
    @classmethod
    def fromPython(cls, obj, alternative_formats=[]):
        return json.dumps(obj, default=json_serialize_handler, indent=2)

    @classmethod
    def toPython(cls, bytestring):
        return json.loads(bytestring)