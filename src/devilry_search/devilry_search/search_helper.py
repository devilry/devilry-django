from haystack.query import SearchQuerySet

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import Period
from devilry.apps.core.models import Subject
from devilry.apps.core.models import Node


class SearchHelper(object):
    def __init__(self, user, searchstring):
        self.user = user
        self.searchstring = searchstring

    def _query(self, search_queryset):
        return search_queryset.auto_query(self.searchstring)

    def get_student_results(self):
        search_queryset = SearchQuerySet()\
            .filter(student_ids=self.user.id, is_published=True)\
            .models(AssignmentGroup)
        return self._query(search_queryset)

    def get_examiner_results(self):
        search_queryset = SearchQuerySet()\
            .filter(examiner_ids=self.user.id, is_active=True)\
            .models(AssignmentGroup, Assignment)
        return self._query(search_queryset)

    def get_admin_results(self):
        search_queryset = SearchQuerySet()
        if not self.user.is_superuser:
            search_queryset = search_queryset.filter(admin_ids=self.user.id)
        search_queryset = search_queryset.models(Node, Subject, Period, Assignment, AssignmentGroup)
        return self._query(search_queryset)