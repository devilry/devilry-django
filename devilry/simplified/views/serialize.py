from django.core import serializers
from django.http import HttpResponse, HttpResponseBadRequest

from devilry.simplified.errors import InvalidRequestData

def _getdata_to_kwargs(formcls, getdata):
    """
    Converts the ``data`` to a validated :class:`GetForm`.

    Throws :class:`errors.InvalidRequestData` if the form does not
    validate.
    """
    form = formcls(getdata)
    if form.is_valid():
        return form.cleaned_data
    else:
        raise InvalidRequestData(form)

def _serialize(resultQry, format):
    if format == 'json':
        return serializers.serialize(format, resultQry.all(),
                ensure_ascii=False) # For utf-8 support http://docs.djangoproject.com/en/dev/topics/serialization/#notes-for-specific-serialization-formats
    else:
        return serializers.serialize(format, resultQry.all())

def qrycallback_to_httpresponse(user, getdata, formcls, qrycallback):
    try:
        form = _getdata_to_kwargs(formcls, getdata)
        format = form['format']
        del form['format']
        resultQry = qrycallback(user, **form)

        try:
            result = _serialize(resultQry, format)
        except KeyError, e:
            return HttpResponseBadRequest(
                "Bad request: Unknown format: %s" % format)

        if format == 'xml':
            return HttpResponse(result, content_type='text/xml')
        else:
            return HttpResponse(result, content_type='text/plain')
    except InvalidRequestData, e:
        return HttpResponseBadRequest("Bad request: %s" % e)
