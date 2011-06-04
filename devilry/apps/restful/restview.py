from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest

from ..ui.http import HttpJsonResponse, HttpXmlResponse
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

        format = form['format']
        del form['format'] # Remove format, since it is not an parameter for get
        form.update(**kwargs) # add variables from PATH
        getqryresult = self.SIMPCLASS.search(request.user, **form)
        resultList = self.restultqry_to_list(getqryresult.valuesQryset())

        try:
            resultList = serialize_result(getqryresult.fields, resultList, format)
        except InvalidRequestFormatError, e:
            return HttpResponseBadRequest(
                "Bad request: %s" % format,
                content_type='text/plain; encoding=utf-8')

        return _response(resultList, format)


    def put(self, request, **kwargs):
        instance = self.__class__.SIMPCLASS.CORE_MODEL(**kwargs)
        print request.raw_post_data
        #form = self.__class__.ModelForm(request.PUT, instance=instance)
        #print form.instance
        return _response("hei", "text")
