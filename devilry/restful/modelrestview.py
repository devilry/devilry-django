from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse

from ..simplified import PermissionDenied, SimplifiedException
from restview import RestfulView
from serializers import serializers, SerializableResult
from readform import ReadForm



class HttpResponseCreated(HttpResponse):
    status_code = 201


def _extjswrap(data, use_extjshacks, success=True, total=None):
    if use_extjshacks:
        result = dict(items = data)
        if total != None:
            result['total'] = total
        result['success'] = success
        return result
    else:
        if total == None:
            return data
        else:
            return dict(items=data, total=total)

class ErrorMsgSerializableResult(SerializableResult):
    def __init__(self, errormessage, httpresponsecls):
        super(ErrorMsgSerializableResult, self).__init__(dict(errormessages=[errormessage]),
                                                         httpresponsecls=httpresponsecls)

class ForbiddenSerializableResult(ErrorMsgSerializableResult):
    def __init__(self):
        super(ForbiddenSerializableResult, self).__init__('Forbidden',
                                                          HttpResponseForbidden)

class FormErrorSerializableResult(SerializableResult):
    def __init__(self, form, use_extjshacks):
        fielderrors = dict(form.errors)
        non_field_errors = list(form.non_field_errors())
        result = dict(fielderrors=fielderrors, errormessages=non_field_errors)
        result = _extjswrap(result, use_extjshacks, success=False)
        super(FormErrorSerializableResult, self).__init__(result, httpresponsecls=HttpResponseBadRequest)


class ModelRestfulView(RestfulView):
    """
    :class:`ModelRestfulView` is used in conjunction with the
    :class:`restful_modelapi`-decorator to autogenerate a RESTful
    interface for a simplified class (see :ref:`simplified`).
    """
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


    def _extjswrapshortcut(self, data, success=True, total=None):
        return _extjswrap(data, self.use_extjshacks, success, total)

    def restultqry_to_list(self, qryresultwrapper):
        return [self.__class__.filter_resultitem(itemdct) \
                for itemdct in qryresultwrapper]

    def _create_or_replace(self, instance=None):
        data = serializers.deserialize(self.comformat, self.request.raw_post_data)
        form = self.__class__.EditForm(data, instance=instance)
        result = None
        if form.is_valid():
            form.save()
            data['id'] = form.instance.id
            result = self._extjswrapshortcut(data)
            if instance == None:
                return SerializableResult(result, httpresponsecls=HttpResponseCreated)
            else:
                return SerializableResult(result)
        else:
            return FormErrorSerializableResult(form, self.use_extjshacks)


    def _load_getdata(self):
        if 'getdata_in_qrystring' in self.request.GET: # NOTE: For easier ExtJS integration
            return True, self.request.GET
        else:
            try:
                return False, serializers.deserialize(self.comformat, self.request.raw_post_data)
            except ValueError, e:
                raise ValueError(('Bad request data: {0}. Perhaps you ment to'
                                  'send GET data as a querystring? In that case, add '
                                  'getdata_in_qrystring=1 to your querystring.'.format(e)))

    def crud_search(self, request):
        """ Maps to the ``search`` method of the simplified class. """
        try:
            fromGET, getdata = self._load_getdata()
        except ValueError, e:
            return ErrorMsgSerializableResult(str(e),
                                              httpresponsecls=HttpResponseBadRequest)
        form = self.__class__.SearchForm(getdata)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            try:
                qryresultwrapper = self._meta.simplified.search(self.request.user, **cleaned_data)
            except SimplifiedException, e:
                return ErrorMsgSerializableResult(str(e),
                                                  httpresponsecls=HttpResponseBadRequest)

            resultlist = self.restultqry_to_list(qryresultwrapper)
            result = self._extjswrapshortcut(resultlist, total=qryresultwrapper.total)
            return SerializableResult(result)
        else:
            return FormErrorSerializableResult(form, self.use_extjshacks)



    def crud_read(self, request, id):
        """ Maps to the ``read`` method of the simplified class. """
        try:
            fromGET, getdata = self._load_getdata()
        except ValueError, e:
            return ErrorMsgSerializableResult(str(e),
                                              httpresponsecls=HttpResponseBadRequest)
        form = ReadForm(getdata)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            try:
                data = self._meta.simplified.read(self.request.user, id, **cleaned_data)
            except PermissionDenied, e:
                return ForbiddenSerializableResult()
            data = self._extjswrapshortcut(data)
            return SerializableResult(data)
        else:
            return FormErrorSerializableResult(form, self.use_extjshacks)


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
        try:
            self._meta.simplified.delete(request.user, id)
        except PermissionDenied, e:
            return ForbiddenSerializableResult()
        else:
            data = self._extjswrapshortcut(dict(id=id))
            return SerializableResult(data)
