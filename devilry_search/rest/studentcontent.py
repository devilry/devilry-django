from djangorestframework.permissions import IsAuthenticated
from haystack.query import SearchQuerySet

from devilry.apps.core.models import AssignmentGroup
from .base import SearchRestViewBase




class SearchStudentContent(SearchRestViewBase):
    """
    Searches all content where the authenticated user is student.

    # Parameters
    Takes the following parameters (in the QUERYSTRING):

    - ``search``: The search string. The result will be an empty list if this is empty.
    - ``maxresults``: The maximum number of results. Defaults to 10. Must be between 1 and 100.

    # Returns
    """
    permissions = (IsAuthenticated,)
    default_maxresults = 10

    def serialize_type_core_assignmentgroup(self, obj, serialized):
        assignment = obj.parentnode
        serialized['title'] = assignment.long_name
        serialized['path'] = assignment.get_path()
        serialized['students'] = self.serialize_students(obj)
        serialized['name'] = obj.name
        return serialized

    def get_search_queryset(self):
        return SearchQuerySet().filter(student_ids=self.request.user.id, is_published=True).models(
            AssignmentGroup)