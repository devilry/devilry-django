from django.views.generic import View
from django.core import serializers
from django.http import HttpResponse, HttpResponseBadRequest

from errors import InvalidRequestData


class RestView(View):
    @classmethod
    def _getdata_to_kwargs(cls, getdata):
        """
        Converts the ``data`` to a validated :class:`GetForm`.

        Throws :class:`errors.InvalidRequestData` if the form does not
        validate.
        """
        form = cls.GetForm(getdata)
        if form.is_valid():
            return form.cleaned_data
        else:
            raise InvalidRequestData(form)

    @classmethod
    def _serialize(self, resultQry, format):
        kwargs = dict(use_natural_keys=True)
        if format == 'json':
            return serializers.serialize(format, resultQry.all(),
                    ensure_ascii=False, # For utf-8 support http://docs.djangoproject.com/en/dev/topics/serialization/#notes-for-specific-serialization-formats
                    indent=2, **kwargs) 
        else:
            return serializers.serialize(format, resultQry.all(), **kwargs)

    def get(self, request, **kwargs):
        try:
            form = self.__class__._getdata_to_kwargs(request.GET)
            format = form['format']
            del form['format']
            form.update(**kwargs)
            resultQry = self.__class__.getqry(request.user, **form)

            try:
                result = self.__class__._serialize(resultQry, format)
            except KeyError, e:
                return HttpResponseBadRequest(
                    "Bad request: Unknown format: %s" % format)

            if format == 'xml':
                return HttpResponse(result, content_type='text/xml')
            else:
                return HttpResponse(result, content_type='text/plain')
        except InvalidRequestData, e:
            return HttpResponseBadRequest("Bad request: %s" % e)
