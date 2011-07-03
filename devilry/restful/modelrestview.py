from django.shortcuts import get_object_or_404

from errors import InvalidRequestDataError
from restview import RestfulView
from serializers import serializers, SerializableResult
from django.http import HttpResponseBadRequest


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
            result = dict(items=data, success=True)
        else:
            fielderrors = dict(form.errors)
            non_field_errors = list(form.non_field_errors())
            result = dict(success=False, fielderrors=fielderrors, non_field_errors=non_field_errors)
        return SerializableResult(result)



    def crud_search(self, request, **kwargs):
        """ Maps to the ``search`` method of the simplified class. """
        if 'getdata_in_qrystring' in self.request.GET: # NOTE: For easier ExtJS integration
            data = self.request.GET
        else:
            try:
                data = serializers.deserialize(self.comformat, self.request.raw_post_data)
            except ValueError, e:
                return SerializableResult(
                        result=dict(error='Bad request data: {0}. Perhaps you ment to'\
                                'send GET data as a querystring? In that case, add ' \
                                'getdata_in_qrystring=1 to your querystring.'.format(e)),
                        httpresponsecls=HttpResponseBadRequest)
        try:
            form = self.__class__._searchform_to_kwargs(data)
        except InvalidRequestDataError, e:
            return SerializableResult(
                    result=dict(error="Bad request: %s" % e),
                    httpresponsecls=HttpResponseBadRequest)

        form.update(**kwargs) # add variables from url PATH
        qryresultwrapper = self._meta.simplified.search(self.request.user, **form)
        resultList = self.restultqry_to_list(qryresultwrapper)
        result = dict(total=len(resultList), success=True, items=resultList)
        return SerializableResult(result)


    def crud_read(self, request, id):
        """ Maps to the ``read`` method of the simplified class. """
        data = self._meta.simplified.read(self.request.user, id)
        if self.use_extjshacks:
            data = dict(items=data, total=1, success=True)
        return SerializableResult(data)


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
        return SerializableResult(dict(pk=id))
