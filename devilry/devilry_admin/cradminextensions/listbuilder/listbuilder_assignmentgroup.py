from __future__ import unicode_literals
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listbuilderview

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_cradmin.devilry_listfilter import assignmentgroup as assignmentgroup_filters


class AddFilterListItemsMixin(object):
    def add_filterlist_items(self, filterlist):
        filterlist.append(assignmentgroup_filters.SearchNotAnonymous())


class ListViewBase(AddFilterListItemsMixin, listbuilderview.FilterListMixin, listbuilderview.View):
    model = AssignmentGroup
    paginate_by = 20


class VerticalFilterListView(ListViewBase):
    def get_filterlist_position(self):
        return 'right'


class AssignmentGroupItemValueTitleDescription(listbuilder.itemvalue.TitleDescription):
    valuealias = 'assignment_group'
