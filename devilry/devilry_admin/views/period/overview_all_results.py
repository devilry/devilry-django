from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers.listbuilderview import FilterListMixin


class AllResultsOverview(FilterListMixin, listbuilderview.View):

    def get_unfiltered_queryset_for_role(self, role):
        pass

    def get_filterlist_url(self, filters_string):
        pass