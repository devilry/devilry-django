from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
from django import forms

from devilry.simplified.examiner import Assignments
from devilry.simplified.errors import InvalidRequestData, InvalidRequestFormat
from devilry.simplified import fields



class FormatConverterProxy(object):
    def __init__(self, label, subsystems):
        self.label = label
        self.subsystems = set(subsystems)
        self.directory = {}

    def get(self, subsystem, format):
        if subsystem in self.directory and format in self.directory[subsystem]:
            return self.directory[subsystem][format]
        else:
            raise InvalidRequestFormat("subsystem:%s, format:%s" % (
                subsystem, format))

    def _set(self, subsystem, format, callback):
        if not subsystem in self.directory:
            self.directory[subsystem] = {}
        if format in self.directory[subsystem]:
            raise ValueError("Format %s is already registered in %s.%s" %
                    (format, self.label, subsystem))
        self.directory[subsystem][format] = callback

    def set(self, format, **all_convertors):
        if not self.subsystems == set(all_convertors.keys()):
            raise ValueError("all_convertors must contain callbacks for: %s"
                    % self.subsystems)
        for subsystem, callback in all_convertors.iteritems():
            self._set(subsystem, format, callback)

FORMAT_CONVERTERS = FormatConverterProxy("examiner", ["Assignments"])


def json_assignments(data):
    return str(data), dict(content_type="text/plain")


FORMAT_CONVERTERS.set("json",
        Assignments = json_assignments)


class HttpAssignments(View):

    class GetForm(forms.Form):
        count = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        format = forms.CharField(required=True)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=["short_name"])
        old = fields.BooleanWithFallbackField(fallbackvalue=True)
        active = fields.BooleanWithFallbackField(fallbackvalue=True)
        search = forms.CharField(required=False)
        longnamefields = fields.BooleanWithFallbackField()
        pointhandlingfields = fields.BooleanWithFallbackField()


    def _getdata_to_kwargs(cls, data):
        """
        Converts the ``data`` to a validated :class:`GetForm`.

        Throws :class:`errors.InvalidRequestData` if the form does not
        validate.
        """
        form = cls.GetForm(data)
        if form.is_valid():
            return form.cleaned_data
        else:
            raise InvalidRequestData(form)


    def get(self, request):
        """
        Calls :meth:`get` after converting the GET-data in the given http
        ``request`` to python objects.
        """
        try:
            getdata = self._getdata_to_kwargs(self.request.GET)
            format = getdata['format']
            del getdata['format']
            result = Assignments.get(request.user, **getdata)
            format_converter = FORMAT_CONVERTERS.get("Assignments", format)
            converted_data, properties = format_converter(result)
            return HttpResponse(converted_data, **properties)
        except InvalidRequestData, e:
            return HttpResponseBadRequest("Bad request: %s" % e)
