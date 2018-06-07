from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listbuilderview

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relateduser
from devilry.apps.core.models import period_tag


class ListViewBase(listbuilderview.FilterListMixin, listbuilderview.View):
    model = RelatedExaminer
    paginate_by = 20

    def get_period(self):
        raise NotImplementedError()

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter_relateduser.Search())
        filterlist.append(listfilter_relateduser.OrderRelatedStudentsFilter())
        period = self.get_period()
        if period_tag.PeriodTag.objects.filter(period=self.get_period()).exists():
            filterlist.append(listfilter_relateduser.TagSelectFilter(period=period))

    def get_no_items_message(self):
        return ugettext_lazy('No examiners found matching your filters/search.')


class VerticalFilterListView(ListViewBase):
    """
    List view for :class:`devilry.apps.core.models.relateduser.RelatedExaminer`
    with filters in a vertical layout.
    """
    def get_filterlist_position(self):
        return 'right'


class RelatedExaminerItemValueTitleDescriptionMixin(object):
    valuealias = 'relatedexaminer'

    def get_title(self):
        if self.relatedexaminer.user.fullname:
            return self.relatedexaminer.user.fullname
        else:
            return self.relatedexaminer.user.shortname

    def get_description(self):
        if self.relatedexaminer.user.fullname:
            return self.relatedexaminer.user.shortname
        else:
            return ''


class OnPeriodItemValue(RelatedExaminerItemValueTitleDescriptionMixin,
                        listbuilder.itemvalue.TitleDescription):

    def get_extra_css_classes_list(self):
        cssclasses = ['devilry-admin-relatedexaminer-onperioditemvalue']
        if self.relatedexaminer.active:
            cssclasses.append('devilry-admin-relatedexaminer-itemvalue-active')
        else:
            cssclasses.append('devilry-admin-relatedexaminer-itemvalue-inactive')
        return cssclasses


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
        # return self.relatedexaminer.number_of_candidates_on_assignment
        return self.relatedexaminer.number_of_candidates_on_assignment

    def has_projectgroups(self):
        return self.get_number_of_candidates() > self.get_number_of_groups()
