from django import forms
from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import ErrorResponse
from djangorestframework import status as statuscodes



class SearchForm(forms.Form):
    # NOTE: Remember to update the docs for each of the subclasses of SearchRestViewBase if we change this
    search = forms.CharField(required=False)
    limit = forms.IntegerField(required=False,
        min_value=1,
        max_value=200)



class SearchRestViewBase(View):
    permissions = (IsAuthenticated,)
    default_limit = 10

    def _serialize_searchresult(self, result):
        modeltype = '{0}_{1}'.format(result.app_label, result.model_name)
        serializer = getattr(self, 'serialize_type_{0}'.format(modeltype))
        serialized = {
            'id': result.object.id,
            'type': modeltype
        }
        return serializer(result.object, serialized)

    def get_search_queryset(self):
        raise NotImplementedError()

    def serialize_students(self, assignment):
        studentnames = [c.student.get_profile().get_displayname()
                        for c in assignment.candidates.all()]
        return studentnames

    def get(self, request):
        form = SearchForm(self.request.GET)
        if form.is_valid():
            searchstring = form.cleaned_data['search']
            if not searchstring:
                return []
            limit = form.cleaned_data['limit'] or self.default_limit

            searchresults = self.get_search_queryset().auto_query(searchstring).load_all()
            total = searchresults.count()

            matches = []
            for result in searchresults[:limit]:
                if result: # We may get some None-values if content has been deleted since last indexing
                    matches.append(self._serialize_searchresult(result))
            return {
                'total': total,
                'matches': matches
            }
        else:
            errors = dict(form.errors.iteritems())
            raise ErrorResponse(statuscodes.HTTP_400_BAD_REQUEST, errors)