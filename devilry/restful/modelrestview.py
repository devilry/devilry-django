from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseForbidden

from ..simplified import PermissionDenied
from errors import InvalidRequestDataError
from restview import RestfulView
from serializers import serializers, SerializableResult


class ErrorMsgSerializableResult(SerializableResult):
    def __init__(self, errormessage, httpresponsecls):
        super(ErrorMsgSerializableResult, self).__init__(dict(errormessages=[errormessage]),
                                                         httpresponsecls=httpresponsecls)

class ForbiddenSerializableResult(ErrorMsgSerializableResult):
    def __init__(self):
        super(ForbiddenSerializableResult, self).__init__('Forbidden',
                                                          HttpResponseForbidden)


class ModelRestfulView(RestfulView):
    """
    :class:`ModelRestfulView` is used in conjunction with the
    :class:`restful_modelapi`-decorator to autogenerate a RESTful
    interface for a simplified class (see :ref:`simplified`).
    """

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


    def _extjswrap(self, data, success=True):
        if self.use_extjshacks:
            if isinstance(data, list):
                result = dict(total = len(data),
                              items = data)
            elif isinstance(data, dict):
                result = data
            result['success'] = success
            return result
        else:
            return data

    def _extjswrap_failure(self, data):
        return self._extjswrap(data, success=False)


    def restultqry_to_list(self, qryresultwrapper):
        return [self.__class__.filter_resultitem(itemdct) \
                for itemdct in qryresultwrapper]

    def _create_or_replace(self, instance=None):
        print self.request.raw_post_data
        data = serializers.deserialize(self.comformat, self.request.raw_post_data)
        #data['start_time'] = data['start_time'].replace('T', ' ')
        #data['end_time'] = data['end_time'].replace('T', ' ')
        #for x, y in data.iteritems():
            #print x, y, type(y)
        form = self.__class__.EditForm(data, instance=instance)
        result = None
        if form.is_valid():
            form.save()
            data['id'] = form.instance.id
            result = self._extjswrap(data)
            return SerializableResult(result)
        else:
            fielderrors = dict(form.errors)
            non_field_errors = list(form.non_field_errors())
            result = dict(fielderrors=fielderrors, errormessages=non_field_errors)
            self._extjswrap_failure(result)
            return SerializableResult(result, httpresponsecls=HttpResponseBadRequest)



    def crud_search(self, request, **kwargs):
        """ Maps to the ``search`` method of the simplified class. """
        if 'getdata_in_qrystring' in self.request.GET: # NOTE: For easier ExtJS integration
            data = self.request.GET
        else:
            try:
                data = serializers.deserialize(self.comformat, self.request.raw_post_data)
            except ValueError, e:
                return ErrorMsgSerializableResult(('Bad request data: {0}. Perhaps you ment to'
                                                   'send GET data as a querystring? In that case, add '
                                                   'getdata_in_qrystring=1 to your querystring.'.format(e)),
                                                  httpresponsecls=HttpResponseBadRequest)
        try:
            form = self.__class__._searchform_to_kwargs(data)
        except InvalidRequestDataError, e:
            return ErrorMsgSerializableResult("Bad request: %s" % e,
                                              httpresponsecls=HttpResponseBadRequest)

        form.update(**kwargs) # add variables from url PATH
        qryresultwrapper = self._meta.simplified.search(self.request.user, **form)
        resultlist = self.restultqry_to_list(qryresultwrapper)
        result = self._extjswrap(resultlist)
        return SerializableResult(result)


    def crud_read(self, request, id):
        """ Maps to the ``read`` method of the simplified class. """
        try:
            data = self._meta.simplified.read(self.request.user, id)
        except PermissionDenied, e:
            return ForbiddenSerializableResult()
        if self.use_extjshacks:
            data = dict(items=data, total=1, success=True)
        return SerializableResult(data)


    def crud_create(self, request):
        """ Maps to the ``create`` method of the simplified class. """
        return self._create_or_replace()

    def crud_update(self, request, id):
        """ Maps to the ``update`` method of the simplified class. """
        try:
            instance = self._meta.simplified._meta.model.objects.get(pk=id)
        except self._meta.simplified._meta.model.DoesNotExist, e:
            return ForbiddenSerializableResult()
        return self._create_or_replace(instance)

    def crud_delete(self, request, id):
        """ Maps to the ``delete`` method of the simplified class. """
        self._meta.simplified.delete(request.user, id)
        try:
            data = self._extjswrap(dict(pk=id))
            return SerializableResult(data)
        except PermissionDenied, e:
            return ForbiddenSerializableResult()
