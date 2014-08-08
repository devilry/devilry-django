from django.http import HttpResponseBadRequest, HttpResponse

from ..simplified import PermissionDenied, SimplifiedException, InvalidUsername
from restview import RestfulView, extjswrap
from serializers import (serializers, SerializableResult,
                         ErrorMsgSerializableResult,
                         ForbiddenSerializableResult,
                         InvalidUsernameSerializableResult)
from readform import ReadForm



class HttpResponseCreated(HttpResponse):
    status_code = 201


class FormErrorSerializableResult(SerializableResult):
    def _create_error_msg_from_form(self, form):
        fielderrors = dict(form.errors)
        non_field_errors = list(form.non_field_errors())
        return dict(fielderrors=fielderrors, errormessages=non_field_errors)

    def __init__(self, form, use_extjshacks):
        error = self._create_error_msg_from_form(form)
        error = extjswrap(error, use_extjshacks, success=False)
        super(FormErrorSerializableResult, self).__init__(error, httpresponsecls=HttpResponseBadRequest)

class MultiFormErrorSerializableResult(FormErrorSerializableResult):
    def __init__(self, list_of_forms, use_extjshacks):
        list_of_errors = [self._create_error_msg_from_form(form) for form in list_of_forms]
        errors = extjswrap(list_of_errors, use_extjshacks, success=False)
        super(FormErrorSerializableResult, self).__init__(errors, httpresponsecls=HttpResponseBadRequest)


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

    def restultqry_to_list(self, qryresultwrapper):
        return [self.__class__.filter_resultitem(itemdct) \
                for itemdct in qryresultwrapper]


    def extra_create_or_replace_responsedata(self, obj_id):
        """ If this does not return ``None``, the return-value is added to the
        ``extra_responsedata`` attribute of the data returned on ``create()`` or
        ``update()``.

        :param obj_id: The id of the object changed by the create or update call.
        """
        return None


    def _deserialize_and_validate_many(self, list_of_field_values):
        list_of_deserialized_field_values = []
        errors = []
        for field_values in list_of_field_values:
            form = self.__class__.EditForm(field_values)
            if form.is_valid():
                cleaned = form.cleaned_data
                pk = field_values.get('pk')
                if pk:
                    cleaned['pk'] = pk
                list_of_deserialized_field_values.append(cleaned)
            else:
                errors.append(form)
        return errors, list_of_deserialized_field_values

    def _create_or_replace_many(self, list_of_field_values, update=False):
        errors, list_of_deserialized_field_values = self._deserialize_and_validate_many(list_of_field_values)
        if errors:
            return MultiFormErrorSerializableResult(errors, self.use_extjshacks)

        responsedata = []
        if update:
            responsedata = self._meta.simplified.updatemany(self.request.user, *list_of_deserialized_field_values)
        else:
            responsedata = self._meta.simplified.createmany(self.request.user, *list_of_deserialized_field_values)

        result = self.extjswrapshortcut(responsedata)
        if update:
            return SerializableResult(result)
        else:
            return SerializableResult(result, httpresponsecls=HttpResponseCreated)

    def _create_or_replace_single(self, data, instance=None):
        form = self.__class__.EditForm(data, instance=instance)
        if form.is_valid():
            try:
                if instance == None:
                    id = self._meta.simplified.create(self.request.user, **form.cleaned_data)
                else:
                    id = self._meta.simplified.update(self.request.user, instance.pk, **form.cleaned_data)
            except PermissionDenied, e:
                return ForbiddenSerializableResult(e)
            except InvalidUsername, e:
                return InvalidUsernameSerializableResult(e.username)

            data['id'] = id
            extra = self.extra_create_or_replace_responsedata(id)
            if extra != None:
                data['extra_responsedata'] = extra
            result = self.extjswrapshortcut(data)
            if instance == None:
                return SerializableResult(result, httpresponsecls=HttpResponseCreated)
            else:
                return SerializableResult(result)
        else:
            return FormErrorSerializableResult(form, self.use_extjshacks)


    def _load_getdata(self):
        if 'getdata_in_qrystring' in self.request.GET or self.use_extjshacks: # NOTE: For easier ExtJS integration
            return True, self.request.GET
        else:
            try:
                return False, serializers.deserialize(self.comformat, self.request.body)
            except ValueError, e:
                raise ValueError(('Bad request data: {0}. Perhaps you ment to'
                                  'send GET data as a querystring? In that case, add '
                                  'getdata_in_qrystring=1 to your querystring.'.format(e)))

    def _parse_extjs_sort(self, sortlist):
        orderby = []
        for sortitem in sortlist:
            fieldname = sortitem['property']
            if sortitem.get('direction', 'ASC') == 'DESC':
                fieldname = '-' + fieldname
            orderby.append(fieldname)
        return orderby

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
            if 'sort' in cleaned_data:
                sort = cleaned_data['sort']
                del cleaned_data['sort']
                if not cleaned_data.get('orderby'):
                    if sort and self.use_extjshacks:
                        orderby = self._parse_extjs_sort(sort)
                        cleaned_data['orderby'] = orderby

            if 'filter' in cleaned_data:
                f = cleaned_data['filter']
                if f:
                    cleaned_data['filters'] = f
                del cleaned_data['filter']
            try:
                qryresultwrapper = self._meta.simplified.search(self.request.user, **cleaned_data)
            except SimplifiedException, e:
                return ErrorMsgSerializableResult(str(e),
                                                  httpresponsecls=HttpResponseBadRequest)

            resultlist = self.restultqry_to_list(qryresultwrapper)
            result = self.extjswrapshortcut(resultlist, total=qryresultwrapper.total)
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
                return ForbiddenSerializableResult(e)
            data = self.extjswrapshortcut(data)
            return SerializableResult(data)
        else:
            return FormErrorSerializableResult(form, self.use_extjshacks)

    def _deserialize_create_or_replace_request(self):
        data = serializers.deserialize(self.comformat, self.request.body)
        if isinstance(data, list):
            return data, False
        else:
            return data, True

    def crud_create(self, request):
        """ Maps to the ``create`` method of the simplified class. """
        data, is_single = self._deserialize_create_or_replace_request()
        if is_single:
            return self._create_or_replace_single(data)
        else:
            return self._create_or_replace_many(data, update=False)

    def crud_update(self, request, id=None):
        """ Maps to the ``update`` method of the simplified class. """
        data, is_single = self._deserialize_create_or_replace_request()
        if is_single:
            try:
                instance = self._meta.simplified._meta.model.objects.get(pk=id)
            except self._meta.simplified._meta.model.DoesNotExist, e:
                return ForbiddenSerializableResult(e)
            return self._create_or_replace_single(data, instance)
        else:
            return self._create_or_replace_many(data, update=True)


    def _delete_many(self):
        if 'deletedata_in_qrystring' in self.request.GET:
            try:
                raw_data = self.request.GET['pks']
            except KeyError, e:
                return ErrorMsgSerializableResult('The querystring must contain a JSON encoded array of primary-keys in the "pks" attribute.',
                                                  httpresponsecls=HttpResponseBadRequest)
        else:
            raw_data = self.request.body
        list_of_pks = serializers.deserialize(self.comformat, raw_data)
        if not isinstance(list_of_pks, list):
            return ErrorMsgSerializableResult('Requires "pks" as a JSON encoded array.',
                                              httpresponsecls=HttpResponseBadRequest)
        pks = self._meta.simplified.deletemany(self.request.user, *list_of_pks)
        result = self.extjswrapshortcut(pks, total=len(pks))
        return SerializableResult(result)


    def crud_delete(self, request, id=None):
        """ Maps to the ``delete`` method of the simplified class. """
        is_single = id != None
        if is_single:
            try:
                self._meta.simplified.delete(request.user, id)
            except PermissionDenied, e:
                return ForbiddenSerializableResult(e)
            else:
                data = self.extjswrapshortcut(dict(id=id))
                return SerializableResult(data)
        else:
            return self._delete_many()
