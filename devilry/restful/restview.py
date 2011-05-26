from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest

from devilry.ui.http import HttpJsonResponse, HttpXmlResponse
from errors import InvalidRequestDataError, InvalidRequestFormatError
from serialize import serialize_result



def _response(resultQry, format):
    if format == 'xml':
        return HttpXmlResponse(resultQry)
    elif format == 'json':
        return HttpJsonResponse(resultQry)
    else:
        return HttpResponse(resultQry,
                content_type='text/plain; encoding=utf-8')


class RestView(View):
    @classmethod
    def _getdata_to_kwargs(cls, getdata):
        """
        Converts the ``data`` to a validated :class:`GetForm`.

        Throws :class:`errors.InvalidRequestDataError` if the form does not
        validate.
        """
        form = cls.GetForm(getdata)
        if form.is_valid():
            return form.cleaned_data
        else:
            raise InvalidRequestDataError(form)

    def get(self, request, **kwargs):
        try:
            form = self.__class__._getdata_to_kwargs(request.GET)
        except InvalidRequestDataError, e:
            return HttpResponseBadRequest("Bad request: %s" % e,
                    content_type='text/plain; encoding=utf-8')

        format = form['format']
        del form['format'] # Remove format, since it is not an parameter for getqry
        form.update(**kwargs) # add variables from PATH
        fields, resultQry = self.__class__.getqry(request.user, **form)

        try:
            resultQry = serialize_result(fields, resultQry, format)
        except InvalidRequestFormatError, e:
            return HttpResponseBadRequest(
                "Bad request: %s" % format,
                content_type='text/plain; encoding=utf-8')

        return _response(resultQry, format)
