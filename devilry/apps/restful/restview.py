from django.views.generic import View
from django.http import HttpResponseBadRequest
from django.utils import simplejson as json
from django.shortcuts import get_object_or_404

from ..ui.http import HttpJsonResponse
from errors import InvalidRequestDataError, InvalidRequestFormatError
from serialize import serialize_result





class SerializerRegistryItem(object):
    def __init__(self, serializer, deserializer, httpresponsecls):
        self.serializer = serializer
        self.deserializer = deserializer
        self.httpresponsecls = httpresponsecls

class SerializerRegistry(dict):
    def create_response(self, data, content_type):
        i = self[content_type]
        return i.httpresponsecls(i.serializer(data))

_serializers = SerializerRegistry()
_serializers['application/json'] = SerializerRegistryItem(json.dumps, json.loads, HttpJsonResponse)



class RestView(View):
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

    def restultqry_to_list(self, resultQry):
        return list(resultQry)

    def get(self, request, **kwargs):
        try:
            form = self.__class__._searchform_to_kwargs(request.GET)
        except InvalidRequestDataError, e:
            return HttpResponseBadRequest("Bad request: %s" % e,
                    content_type='text/plain; encoding=utf-8')

        content_type = form['content_type']
        del form['content_type'] # Remove content_type, since it is not an parameter for get
        form.update(**kwargs) # add variables from url PATH
        getqryresult = self._meta.simplified.search(request.user, **form)
        resultList = self.restultqry_to_list(getqryresult.valuesQryset())

        result = dict(total=len(resultList), success=True, items=resultList)
        #try:
            #resultList = serialize_result(getqryresult.resultfields, resultList, content_type)
        #except InvalidRequestFormatError, e:
            #return HttpResponseBadRequest(
                #"Bad request: %s" % content_type,
                #content_type='text/plain; encoding=utf-8')
        return _serializers.create_response(result, content_type)


    def _create_or_replace(self, instance=None):
        content_type = self.request.META['CONTENT_TYPE']
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
        return _serializers.create_response(result, content_type)

    def post(self, request, pk=0):
        """ Create """
        return self._create_or_replace()

    def put(self, request, pk):
        """ Replace/Update """
        instance = get_object_or_404(self._meta.simplified._meta.model, pk=pk)
        return self._create_or_replace(instance)

    #def put(self, request, pk):
        #""" Replace """
        #content_type = request.META['CONTENT_TYPE']
        #data = json.loads(request.raw_post_data)
        #instance = get_object_or_404(self._meta.simplified._meta.model, pk=pk)
        #form = self.__class__.EditForm(data, instance=instance)
        #result = None
        #if form.is_valid():
            #form.save()
            #result = dict(success=True)
        #else:
            #fielderrors = dict(form.errors)
            #non_field_errors = list(form.non_field_errors())
            #result = dict(success=False, fielderrors=fielderrors, non_field_errors=non_field_errors)
        #return _serializers.create_response(result, content_type)
