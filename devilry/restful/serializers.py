from functools import wraps
import json
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
from devilry.defaults.encoding import CHARSET


class SerializableResult(object):
    """ Stores Python objects for serialization with :class:`devilry.simplified.serializers.SerializerRegistry`. """
    def __init__(self, result, httpresponsecls=HttpResponse, encoding=CHARSET):
        self.result = result
        self.httpresponsecls = httpresponsecls
        self.encoding = encoding

class ErrorMsgSerializableResult(SerializableResult):
    def __init__(self, errormessage, httpresponsecls):
        super(ErrorMsgSerializableResult, self).__init__(dict(errormessages=[errormessage]),
                                                         httpresponsecls=httpresponsecls)

class ForbiddenSerializableResult(ErrorMsgSerializableResult):
    def __init__(self, exception=None):
        if exception and exception.message:
            errormessage = exception.message
        else:
            errormessage = 'Forbidden'
        super(ForbiddenSerializableResult, self).__init__(errormessage,
                                                          HttpResponseForbidden)

class InvalidUsernameSerializableResult(ErrorMsgSerializableResult):
    def __init__(self, username):
        super(InvalidUsernameSerializableResult, self).__init__('Invalid username: {0}'.format(username),
                                                                HttpResponseBadRequest)


class SerializerRegistryItem(object):
    def __init__(self, serializer, deserializer):
        self.serializer = serializer
        self.deserializer = deserializer

class SerializerRegistry(dict):
    def create_response(self, result, comformat, content_type=None):
        i = self[comformat]
        content_type = content_type or comformat
        return result.httpresponsecls(i.serializer(result.result),
                content_type='{0}; encoding={1}'.format(content_type, result.encoding))

    def deserialize(self, comformat, data):
        i = self[comformat]
        return i.deserializer(data)


def json_serialize_handler(obj):
    #print type(obj)
    if isinstance(obj, ValuesQuerySet):
        return list(obj)
    if hasattr(obj, 'isoformat'):
        #return obj.strftime('%Y-%m-%d')
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (
            type(obj), repr(obj)))

def json_serialize(s):
    return json.dumps(s, default=json_serialize_handler, indent=2)

serializers = SerializerRegistry()
serializers['application/json'] = SerializerRegistryItem(json_serialize, json.loads)



def _serialize(content_type_override=None):
    def decorator(f):
        @wraps(f)
        def wrapper(self, request, *args, **kwargs):
            comformat = request.META.get('Accept', 'application/json')
            if not comformat in serializers:
                return HttpResponseBadRequest(
                    "Bad request: %s" % comformat,
                    format='text/plain; encoding={0}'.format(CHARSET))
            self.comformat = comformat
            result = f(self, request, *args, **kwargs) # returns a SerializableResult object
            return serializers.create_response(result, comformat, content_type_override)
        return wrapper
    return decorator

def serialize(f=None, content_type_override=None):
    """ Decorator to serialize response.

    :param content_type_override: Override content type of response.
        Serialization is still done using the the communication format from the
        Accept header, however the content-type header will use this format instead
        of the communication format. Mainly useful when browsers need text/html
        response to behave, such as with file upload.
    """
    decorator = _serialize(content_type_override=content_type_override)
    if f:
        return decorator(f)
    else:
        return decorator
