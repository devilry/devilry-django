from functools import wraps

from django.core.urlresolvers import reverse
from django.views.generic import View
from django.http import HttpResponseBadRequest, HttpResponse
from django.utils import simplejson as json
from django.shortcuts import get_object_or_404
from django.conf.urls.defaults import url
from django.contrib.auth.decorators import login_required
from django.db.models.query import ValuesQuerySet

from errors import InvalidRequestDataError



class RestResult(object):
    def __init__(self, result, httpresponsecls=HttpResponse, encoding='utf-8'):
        self.result = result
        self.httpresponsecls = httpresponsecls
        self.encoding = encoding

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
    print type(obj)
    if isinstance(obj, ValuesQuerySet):
        return list(obj)
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (
            type(obj), repr(obj)))

def json_serialize(s):
    return json.dumps(s, default=json_serialize_handler, indent=2)

_serializers = SerializerRegistry()
_serializers['application/json'] = SerializerRegistryItem(json_serialize, json.loads)



def serialize(f):
    @wraps(f)
    def wrapper(self, request, *args, **kwargs):
        comformat = request.META.get('Accept', 'application/json')
        if not comformat in _serializers:
            return HttpResponseBadRequest(
                "Bad request: %s" % comformat,
                format='text/plain; encoding=utf-8')
        self.comformat = comformat
        result = f(self, request, *args, **kwargs) # returns a RestResult object
        return _serializers.create_response(result, comformat)
    return wrapper



class RestView(View):
    @classmethod
    def create_rest_url(cls):
        return url(r'^%s/(?P<id>[a-zA-Z0-9]+)?$' % cls._meta.urlprefix,
            login_required(cls.as_view()),
            name=cls._meta.urlname)

    @classmethod
    def get_rest_url(cls, *args, **kwargs):
        return reverse(cls._meta.urlname, args=args, kwargs=kwargs)

    @serialize
    def get(self, request, **kwargs):
        if kwargs['id'] == None:
            del kwargs['id']
            if not hasattr(self, 'crud_search'):
                return RestResult(dict(
                    error='GET method with no identifier (search) is not supported.'),
                    httpresponsecls=HttpResponseBadRequest)
            return self.crud_search(request, **kwargs)
        else:
            if not hasattr(self, 'crud_read'):
                return RestResult(dict(
                    error='GET method with identifier (read) is not supported.'),
                    httpresponsecls=HttpResponseBadRequest)
            return self.crud_read(request, **kwargs)

    @serialize
    def post(self, request, id=None):
        return self.crud_create(request)

    @serialize
    def put(self, request, id):
        return self.crud_update(request, id)

    @serialize
    def delete(self, request, id):
        return self.crud_delete(request, id)


class ModelRestView(RestView):
    @classmethod
    def _searchform_to_kwargs(cls, getdata):
        """
        Converts the ``data`` to a validated :class:`SearchForm`.

        Throws :class:`errors.InvalidRequestDataError` if the form does not
        validate.
        """
        form = cls.SearchForm(getdata)
        if form.is_valid():
            return form.cleaned_data
        else:
            raise InvalidRequestDataError(form)

    @classmethod
    def filter_urlmap(cls, itemdct):
        if not hasattr(cls._meta, 'urlmap'):
            return itemdct
        for fieldname, mapping in cls._meta.urlmap.iteritems():
            url = mapping.restfulcls.get_rest_url(itemdct[mapping.idfield])
            itemdct[fieldname] = url
        return itemdct

    @classmethod
    def filter_resultitem(cls, itemdct):
        return cls.filter_urlmap(itemdct)

    def restultqry_to_list(self, resultQry):
        return [self.__class__.filter_resultitem(itemdct) \
                for itemdct in resultQry]

    def _create_or_replace(self, instance=None):
        data = _serializers.deserialize(self.comformat, self.request.raw_post_data)
        form = self.__class__.EditForm(data, instance=instance)
        result = None
        if form.is_valid():
            form.save()
            result = dict(success=True, id=form.instance.id)
        else:
            fielderrors = dict(form.errors)
            non_field_errors = list(form.non_field_errors())
            result = dict(success=False, fielderrors=fielderrors, non_field_errors=non_field_errors)
        return RestResult(result)



    def crud_search(self, request, **kwargs):
        """ Maps to the ``search`` method of the simplified class. """
        if 'use_getqry' in self.request.GET:
            data = self.request.GET
        else:
            try:
                data = _serializers.deserialize(self.comformat, self.request.raw_post_data)
            except ValueError, e:
                return RestResult(
                        result=dict(error="Bad request data: %s" % e),
                        httpresponsecls=HttpResponseBadRequest)
        try:
            form = self.__class__._searchform_to_kwargs(data)
        except InvalidRequestDataError, e:
            return RestResult(
                    result=dict(error="Bad request: %s" % e),
                    httpresponsecls=HttpResponseBadRequest)

        form.update(**kwargs) # add variables from url PATH
        getqryresult = self._meta.simplified.search(self.request.user, **form)
        resultList = self.restultqry_to_list(getqryresult.valuesQryset())
        result = dict(total=len(resultList), success=True, items=resultList)
        return RestResult(result)


    def crud_read(self, request, id):
        """ Maps to the ``read`` method of the simplified class. """
        data = self._meta.simplified.read(self.request.user, id)
        return RestResult(data)


    def crud_create(self, request):
        """ Maps to the ``create`` method of the simplified class. """
        return self._create_or_replace()

    def crud_update(self, request, id):
        """ Maps to the ``update`` method of the simplified class. """
        instance = get_object_or_404(self._meta.simplified._meta.model,
                pk=id)
        return self._create_or_replace(instance)

    def crud_delete(self, request, id):
        """ Maps to the ``delete`` method of the simplified class. """
        self._meta.simplified.delete(request.user, id)
        return RestResult(dict(pk=id))
