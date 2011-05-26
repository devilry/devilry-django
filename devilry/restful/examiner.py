from django import forms

from simplified.examiner import Assignments, Groups

import fields
from restview import RestView


class RestAssignments(Assignments, RestView):

    class GetForm(forms.Form):
        format = fields.FormatField()
        count = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=["short_name"])
        old = fields.BooleanWithFallbackField(fallbackvalue=True)
        active = fields.BooleanWithFallbackField(fallbackvalue=True)
        search = forms.CharField(required=False)
        longnamefields = fields.BooleanWithFallbackField()
        pointhandlingfields = fields.BooleanWithFallbackField()


class RestGroups(Groups, RestView):

    class GetForm(forms.Form):
        format = fields.FormatField()
        count = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=["short_name"])
        deadlines = fields.BooleanWithFallbackField(fallbackvalue=False)
        search = forms.CharField(required=False)
