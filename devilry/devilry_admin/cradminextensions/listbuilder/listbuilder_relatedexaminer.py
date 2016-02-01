from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relateduser


class ListViewBase(listbuilderview.FilterListMixin, listbuilderview.View):
    model = RelatedStudent
    paginate_by = 200

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter_relateduser.Search())
        filterlist.append(listfilter_relateduser.OrderRelatedStudentsFilter())


class OnassignmentItemValue(listbuilder.itemvalue.TitleDescription):
    """
    RelatedExaminer itemvalue renderer for an examiner on an assignment.

    Requires the RelatedExaminer queryset to be annotated with:

    - ``annotate_with_number_of_groups_on_assignment()``
    - ``extra_annotate_with_number_of_candidates_on_assignment()``
    """
    template_name = 'devilry_admin/listbuilder/listbuilder_relatedexaminer/onassignment-itemvalue.django.html'
    valuealias = 'relatedexaminer'

    def get_extra_css_classes_list(self):
        return ['devilry-admin-listbuilder-relatedexaminer-onassignment']

    def get_number_of_groups(self):
        return self.relatedexaminer.number_of_groups_on_assignment

    def get_number_of_candidates(self):
        return self.relatedexaminer.number_of_candidates_on_assignment

    def has_projectgroups(self):
        return self.get_number_of_candidates() > self.get_number_of_groups()
