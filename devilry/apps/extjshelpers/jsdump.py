import json


class UnString(object):
    def __init__(self, string):
        self.string = string

    def serialize(self):
        return json.dumps(self.string)[1:-1]

    def __str__(self):
        return self.serialize()


def _json_serialize_handler(obj):
    #print type(obj)
    if isinstance(obj, UnString):
        return obj.serialize()
    else:
        raise TypeError('Object of type {0} with value of {1} is not JSON serializable' % (type(obj), repr(obj)))



def dumps(s):
    return json.dumps(s, default=_json_serialize_handler, indent=2)
