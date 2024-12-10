
from cradmin_legacy.viewhelpers import listbuilder
from cradmin_legacy.viewhelpers import listbuilderview

from devilry.apps.core.models import RelatedStudent
# from devilry.apps.core.models.relateduser import RelatedStudentTag
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relateduser
import devilry.apps.core.models.period_tag as period_tag


class AddFilterListItemsMixin(object):
    def get_period(self):
        raise NotImplementedError()

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter_relateduser.Search())
        filterlist.append(listfilter_relateduser.OrderRelatedStudentsFilter())
        period = self.get_period()
        if period_tag.PeriodTag.objects.filter(period=self.get_period()).exists():
            filterlist.append(listfilter_relateduser.TagSelectFilter(period=period))


class ListViewBase(AddFilterListItemsMixin, listbuilderview.FilterListMixin, listbuilderview.View):
    model = RelatedStudent
    paginate_by = 200


class VerticalFilterListView(ListViewBase):
    """
    List view for :class:`devilry.apps.core.models.relateduser.RelatedStudent`
    with filters in a vertical layout.
    """
    def get_filterlist_position(self):
        return 'right'


class RelatedStudentItemValueTitleDescriptionMixin(object):
    valuealias = 'relatedstudent'

    def get_description(self):
        return ', '.join(self.relatedstudent.syncsystemtag_stringlist)


class ReadOnlyItemValue(RelatedStudentItemValueTitleDescriptionMixin,
                        listbuilder.itemvalue.TitleDescription):
    template_name = 'devilry_admin/listbuilder/listbuilder_relatedstudent/readonly-itemvalue.django.html'

    def get_extra_css_classes_list(self):
        cssclasses = ['devilry-admin-listbuilder-relatedstudent-readonlyitemvalue']
        if self.relatedstudent.active:
            cssclasses.append('devilry-admin-relatedstudent-itemvalue-active')
        else:
            cssclasses.append('devilry-admin-relatedstudent-itemvalue-inactive')
        return cssclasses
