from functools import wraps

from django.core.urlresolvers import reverse
from django.views.generic import View
from django.http import HttpResponseBadRequest, HttpResponse
from django.utils import simplejson as json
from django.shortcuts import get_object_or_404
from django.conf.urls.defaults import url
from django.contrib.auth.decorators import login_required

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
    def create_response(self, result, format):
        i = self[format]
        return result.httpresponsecls(i.serializer(result.result),
                content_type='%s; encoding=%s' % (format, result.encoding))




def json_serialize_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (
            type(obj), repr(obj)))

def json_serialize(s):
    return json.dumps(s, default=json_serialize_handler)

_serializers = SerializerRegistry()
_serializers['application/json'] = SerializerRegistryItem(json_serialize, json.loads)



def serialize(f):
    @wraps(f)
    def wrapper(self, request, *args, **kwargs):
        result = f(self, request, *args, **kwargs) # returns a RestResult object
        format = request.META.get('Accept', 'application/json')
        if not format in _serializers:
            return HttpResponseBadRequest(
                "Bad request: %s" % format,
                format='text/plain; encoding=utf-8')
        return _serializers.create_response(result, format)
    return wrapper



class ModelRestView(View):
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
    def create_rest_url(cls):
        return url(r'^%s/(?P<pk>[a-zA-Z0-9]+)?$' % cls._meta.urlprefix,
            login_required(cls.as_view()),
            name=cls._meta.urlname)

    @classmethod
    def get_rest_url(cls, *args, **kwargs):
        return reverse(cls._meta.urlname, args=args, kwargs=kwargs)

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

    def _getlist(self, request, kwargs):
        try:
            form = self.__class__._searchform_to_kwargs(request.GET)
        except InvalidRequestDataError, e:
            return RestResult(HttpResponseBadRequest, dict(error="Bad request: %s" % e))

        #format = form['format']
        #del form['format'] # Remove format, since it is not an parameter for get
        form.update(**kwargs) # add variables from url PATH
        getqryresult = self._meta.simplified.search(request.user, **form)
        resultList = self.restultqry_to_list(getqryresult.valuesQryset())
        result = dict(total=len(resultList), success=True, items=resultList)
        return RestResult(result)

    def _getitem(self, request, kwargs):
        pk = kwargs['pk']
        data = self._meta.simplified.read(request.user, pk)
        return RestResult(data)

    def _create_or_replace(self, instance=None):
        data = json.loads(self.request.raw_post_data)
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


    @serialize
    def get(self, request, **kwargs):
        """ Maps to the read method of the simplified class. """
        if kwargs['pk'] != None:
            return self._getitem(request, kwargs)
        else:
            return self._getlist(request, kwargs)

    @serialize
    def post(self, request, pk=0):
        """ Maps to the ``create`` method of the simplified class. """
        return self._create_or_replace()

    @serialize
    def put(self, request, pk):
        """ Maps to the ``update`` method of the simplified class. """
        instance = get_object_or_404(self._meta.simplified._meta.model, pk=pk)
        return self._create_or_replace(instance)
