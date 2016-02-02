from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listbuilderview

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relateduser


class AddFilterListItemsMixin(object):
    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter_relateduser.Search())
        filterlist.append(listfilter_relateduser.OrderRelatedStudentsFilter())


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

    # def get_title(self):
    #     if self.relatedstudent.user.fullname:
    #         return self.relatedstudent.user.fullname
    #     else:
    #         return self.relatedstudent.user.shortname

    def get_description(self):

        if self.relatedstudent.user.fullname:
            return self.relatedstudent.user.shortname
        else:
            return ''


class ReadOnlyItemValue(RelatedStudentItemValueTitleDescriptionMixin,
                        listbuilder.itemvalue.TitleDescription):
    template_name = 'listbuilder/listbuilder_relatedstudent/readonly-itemvalue.django.html'

    def get_extra_css_classes_list(self):
        cssclasses = ['devilry-admin-listbuilder-relatedstudent-readonlyitemvalue']
        if self.relatedstudent.active:
            cssclasses.append('devilry-admin-relatedstudent-itemvalue-active')
        else:
            cssclasses.append('devilry-admin-relatedstudent-itemvalue-inactive')
        return cssclasses
