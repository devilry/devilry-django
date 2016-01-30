from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relatedstudent


class AddFilterListItemsMixin(object):
    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label_is_screenreader_only=True,
            label=ugettext_lazy('Search'),
            modelfields=['user__fullname', 'user__shortname']))
        filterlist.append(listfilter_relatedstudent.OrderRelatedStudentsFilter(
            slug='orderby',
            label=ugettext_lazy('Order by')))


class ListViewBase(AddFilterListItemsMixin, listbuilderview.FilterListMixin, listbuilderview.View):
    model = RelatedStudent
    paginate_by = 200


class VerticalFilterListView(ListViewBase):
    """
    List view for :class:`devilry.apps.core.models.relateduser.RelatedStudent`
    with filters in a vertical layout.
    """
    def get_filterlist_position(self):
        return 'left'


class RelatedStudentItemValueTitleDescriptionMixin(object):
    valuealias = 'relatedstudent'

    def get_title(self):
        if self.relatedstudent.user.fullname:
            return self.relatedstudent.user.fullname
        else:
            return self.relatedstudent.user.shortname

    def get_description(self):
        if self.relatedstudent.user.fullname:
            return self.relatedstudent.user.shortname
        else:
            return ''


class ReadOnlyItemValue(RelatedStudentItemValueTitleDescriptionMixin,
                        listbuilder.itemvalue.TitleDescription):

    def get_extra_css_classes_list(self):
        return ['devilry-admin-listbuilder-relatedstudent-readonlyitemvalue']
