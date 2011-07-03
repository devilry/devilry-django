from django import forms

from ...simplified import (SimplifiedSubject, SimplifiedPeriod, SimplifiedAssignment, SimplifiedAssignmentGroup)
from ...restful import fields, SearchFormBase


#class RestfulSimplifiedSubject(RestView):
    #SIMPCLASS = SimplifiedSubject

    #def restultqry_to_list(self, resultQry):
        #tpl = '/%(short_name)s'
        #def filter_func(assignmentDict):
            #assignmentDict.update(path=tpl % assignmentDict)
            ##assignmentDict.update(id=tpl % assignmentDict)
            #return assignmentDict
        #return filter(filter_func, resultQry)

    #class SearchForm(SearchFormBase):
        #orderby = fields.CharListWithFallbackField(
                #fallbackvalue=SimplifiedSubject._meta.ordering)


#class RestfulSimplifiedPeriod(RestView):
    #SIMPCLASS = SimplifiedPeriod

    #def restultqry_to_list(self, resultQry):
        #tpl = '/%(parentnode__short_name)s/%(short_name)s'
        #def filter_func(assignmentDict):
            #assignmentDict.update(path=tpl % assignmentDict)
            ##assignmentDict.update(id=tpl % assignmentDict)
            #return assignmentDict
        #return filter(filter_func, resultQry)

    #class SearchForm(SearchFormBase):
        #orderby = fields.CharListWithFallbackField(
                #fallbackvalue=SimplifiedSubject._meta.ordering)
        #subject_short_name = forms.CharField(required=False)


#class RestfulSimplifiedAssignment(RestView):
    #SIMPCLASS = SimplifiedAssignment

    #def restultqry_to_list(self, resultQry):
        #tpl = ('/%(parentnode__parentnode__short_name)s/'
            #'%(parentnode__short_name)s/%(short_name)s')
        #def filter_func(assignmentDict):
            #print assignmentDict
            #assignmentDict.update(path=tpl % assignmentDict)
            #return assignmentDict
        #return filter(filter_func, resultQry)

    #class SearchForm(SearchFormBase):
        #orderby = fields.CharListWithFallbackField(
                #fallbackvalue=SimplifiedAssignment._meta.ordering)
        #old = fields.BooleanWithFallbackField(fallbackvalue=True)
        #active = fields.BooleanWithFallbackField(fallbackvalue=True)
        #longnamefields = fields.BooleanWithFallbackField()
        #pointhandlingfields = fields.BooleanWithFallbackField()
        #subject_short_name = forms.CharField(required=False)
        #period_short_name = forms.CharField(required=False)


#class RestfulSimplifiedAssignmentGroup(RestView):
    #SIMPCLASS = SimplifiedAssignmentGroup
    #class SearchForm(SearchFormBase):
        #orderby = fields.CharListWithFallbackField(
                #fallbackvalue=SimplifiedAssignmentGroup._meta.ordering)
        #deadlines = fields.BooleanWithFallbackField(fallbackvalue=False)
