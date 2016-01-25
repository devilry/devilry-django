from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relatedstudent


class ListViewBase(listbuilderview.FilterListMixin, listbuilderview.View):
    model = RelatedStudent
    paginate_by = 200

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label_is_screenreader_only=True,
            label=ugettext_lazy('Search'),
            modelfields=['user__fullname', 'user__shortname']))
        filterlist.append(listfilter_relatedstudent.OrderRelatedStudentsFilter(
            slug='orderby',
            label=ugettext_lazy('Order by')))


class ItemValueMixin(object):
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


class ReadOnlyItemValue(ItemValueMixin, listbuilder.itemvalue.TitleDescription):
    def get_extra_css_classes_list(self):
        return ['devilry-admin-listbuilder-relatedexaminer-readonlyitemvalue']
