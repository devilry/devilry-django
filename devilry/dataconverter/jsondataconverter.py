import json
from devilry.dataconverter.dataconverter import DataConverter

def json_serialize_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (
            type(obj), repr(obj)))


class JsonDataConverter(DataConverter):
    @classmethod
    def fromPython(cls, obj):
        return json.dumps(obj, default=json_serialize_handler, indent=2)

    @classmethod
    def toPython(cls, bytestring):
        return json.loads(bytestring)