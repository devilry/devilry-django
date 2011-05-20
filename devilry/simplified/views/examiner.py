from django.views.generic import View
from django import forms

from devilry.simplified.examiner import get_assignments
from devilry.simplified import fields
from serialize import qrycallback_to_httpresponse


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


    def get(self, request):
        """
        Calls :meth:`get` after converting the GET-data in the given http
        ``request`` to python objects.
        """
        return qrycallback_to_httpresponse(request.user, request.GET,
                self.GetForm, get_assignments)
