from djangorestframework.permissions import IsAuthenticated
from haystack.query import SearchQuerySet

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Assignment
from .base import SearchRestViewBase




class SearchExaminerContent(SearchRestViewBase):
    """
    Searches all content where the authenticated user is examiner.

    # Parameters
    Takes the following parameters (in the QUERYSTRING):

    - ``search``: The search string. The result will be an empty list if this is empty.
    - ``maxresults``: The maximum number of results. Defaults to 10. Must be between 1 and 100.

    # Returns
    """
    permissions = (IsAuthenticated,)
    default_maxresults = 10


    def _serialize_candidateids(self, assignment):
        candidateids = [c.candidate_id
                        for c in assignment.candidates.all()]
        return candidateids

    def serialize_type_core_assignment(self, obj, serialized):
        serialized['title'] = obj.long_name
        serialized['path'] = obj.get_path()
        return serialized

    def serialize_type_core_assignmentgroup(self, obj, serialized):
        assignment = obj.parentnode
        serialized['title'] = assignment.long_name
        serialized['path'] = assignment.get_path()
        if assignment.anonymous:
            serialized['students'] = self._serialize_candidateids(obj)
        else:
            serialized['students'] = self.serialize_students(obj)
        serialized['name'] = obj.name
        return serialized

    def get_search_queryset(self):
        return SearchQuerySet().filter(examiner_ids=self.request.user.id, is_active=True).models(
            AssignmentGroup, Assignment)