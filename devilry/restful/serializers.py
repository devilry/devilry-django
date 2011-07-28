from functools import wraps
import json
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden


class SerializableResult(object):
    """ Stores Python objects for serialization with :class:`devilry.simplified.serializers.SerializerRegistry`. """
    def __init__(self, result, httpresponsecls=HttpResponse, encoding='utf-8'):
        self.result = result
        self.httpresponsecls = httpresponsecls
        self.encoding = encoding

class ErrorMsgSerializableResult(SerializableResult):
    def __init__(self, errormessage, httpresponsecls):
        super(ErrorMsgSerializableResult, self).__init__(dict(errormessages=[errormessage]),
                                                         httpresponsecls=httpresponsecls)

class ForbiddenSerializableResult(ErrorMsgSerializableResult):
    def __init__(self):
        super(ForbiddenSerializableResult, self).__init__('Forbidden',
                                                          HttpResponseForbidden)


class SerializerRegistryItem(object):
    def __init__(self, serializer, deserializer):
        self.serializer = serializer
        self.deserializer = deserializer

class SerializerRegistry(dict):
    def create_response(self, result, comformat):
        i = self[comformat]
        return result.httpresponsecls(i.serializer(result.result),
                content_type='%s; encoding=%s' % (comformat, result.encoding))

    def deserialize(self, comformat, data):
        i = self[comformat]
        return i.deserializer(data)


def json_serialize_handler(obj):
    #print type(obj)
    if isinstance(obj, ValuesQuerySet):
        return list(obj)
    if hasattr(obj, 'isoformat'):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (
            type(obj), repr(obj)))

def json_serialize(s):
    return json.dumps(s, default=json_serialize_handler, indent=2)

serializers = SerializerRegistry()
serializers['application/json'] = SerializerRegistryItem(json_serialize, json.loads)



def serialize(f):
    @wraps(f)
    def wrapper(self, request, *args, **kwargs):
        comformat = request.META.get('Accept', 'application/json')
        if not comformat in serializers:
            return HttpResponseBadRequest(
                "Bad request: %s" % comformat,
                format='text/plain; encoding=utf-8')
        self.comformat = comformat
        result = f(self, request, *args, **kwargs) # returns a SerializableResult object
        return serializers.create_response(result, comformat)
    return wrapper
