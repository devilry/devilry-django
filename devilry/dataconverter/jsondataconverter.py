import json
from devilry.dataconverter.dataconverter import DataConverter

class JsonDataConverter(DataConverter):
    @classmethod
    def fromPython(cls, obj):
        return json.dumps(obj)

    @classmethod
    def toPython(cls, bytestring):
        return json.loads(bytestring)