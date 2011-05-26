from django import forms

from simplified.examiner import (Subjects, Assignments, Groups)

import fields
from restview import RestView


class GetFormBase(forms.Form):
    format = fields.FormatField()
    query = forms.CharField(required=False)
    limit = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
    start = fields.PositiveIntegerWithFallbackField()
    #page = fields.PositiveIntegerWithFallbackField()

class RestAssignments(Assignments, RestView):

    def restultqry_to_list(self, resultQry):
        tpl = ('%(parentnode__parentnode__short_name)s.'
            '%(parentnode__short_name)s.%(short_name)s')
        def filter_func(assignmentDict):
            assignmentDict.update(path=tpl % assignmentDict)
            return assignmentDict
        return filter(filter_func, resultQry)

    class GetForm(GetFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Assignments.default_orderby)
        old = fields.BooleanWithFallbackField(fallbackvalue=True)
        active = fields.BooleanWithFallbackField(fallbackvalue=True)
        longnamefields = fields.BooleanWithFallbackField()
        pointhandlingfields = fields.BooleanWithFallbackField()


class RestGroups(Groups, RestView):
    class GetForm(GetFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Groups.default_orderby)
        deadlines = fields.BooleanWithFallbackField(fallbackvalue=False)


class RestSubjects(Subjects, RestView):
    class GetForm(GetFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Subjects.default_orderby)
