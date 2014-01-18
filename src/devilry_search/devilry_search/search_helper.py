from haystack.query import SearchQuerySet

from devilry.apps.core.models import AssignmentGroup


class SearchHelper(object):
    def __init__(self, user, searchstring):
        self.user = user
        self.searchstring = searchstring

    def _query(self, search_queryset):
        return search_queryset.auto_query(self.searchstring).load_all()

    def get_student_results(self):
        search_queryset = SearchQuerySet()\
            .filter(student_ids=self.user.id, is_published=True)\
            .models(AssignmentGroup)
        return self._query(search_queryset)
