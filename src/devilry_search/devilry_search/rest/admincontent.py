from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import ErrorResponse
from djangorestframework import status as statuscodes
from django import forms
from haystack.query import SearchQuerySet



class SearchForm(forms.Form):
    search = forms.CharField(required=False)
    maxresults = forms.IntegerField(required=False,
        min_value=1,
        max_value=100)


class SearchAdminContent(View):
    """
    Searches all content where the authenticated user is admin.

    # Parameters
    Takes the following parameters (in the QUERYSTRING):

    - ``search``: The search string. The result will be an empty list if this is empty.
    - ``maxresults``: The maximum number of results. Defaults to 10. Must be between 1 and 100.

    # Returns
    """
    permissions = (IsAuthenticated,)
    default_maxresults = 10

    def _serialize_basenode(self, obj, serialized):
        serialized['title'] = obj.long_name
        return serialized

    def _serialize_type_core_node(self, obj, serialized):
        return self._serialize_basenode(obj, serialized)

    def _serialize_type_core_subject(self, obj, serialized):
        return self._serialize_basenode(obj, serialized)

    def _serialize_type_core_period(self, obj, serialized):
        return self._serialize_basenode(obj, serialized)

    def _serialize_type_core_assignment(self, obj, serialized):
        return self._serialize_basenode(obj, serialized)

    def _serialize_searchresult(self, result):
        modeltype = '{0}_{1}'.format(result.app_label, result.model_name)
        serializer = getattr(self, '_serialize_type_{0}'.format(modeltype))
        serialized = {
            'id': result.object.id,
            'type': modeltype,
            'path': result.object.get_path()
        }
        return serializer(result.object, serialized)

    def get(self, request):
        form = SearchForm(self.request.GET)
        if form.is_valid():
            searchstring = form.cleaned_data['search']
            if not searchstring:
                return []
            maxresults = form.cleaned_data['maxresults'] or self.default_maxresults
            searchresults = SearchQuerySet().filter(admins=self.request.user.id).auto_query(searchstring)
            output = []
            for result in searchresults[:maxresults]:
                output.append(self._serialize_searchresult(result))
            return output
        else:
            errors = dict(form.errors.iteritems())
            raise ErrorResponse(statuscodes.HTTP_400_BAD_REQUEST, errors)