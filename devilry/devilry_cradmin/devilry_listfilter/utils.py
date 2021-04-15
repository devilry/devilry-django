from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers.listbuilder.itemvalue import TitleDescription
from cradmin_legacy.viewhelpers.listbuilder.lists import RowList
from cradmin_legacy.viewhelpers.listbuilder.itemframe import DefaultSpacingItemFrame


class WithResultValueRenderable(TitleDescription):
    """
    For rendering results number in list filter views.
    """
    template_name = 'devilry_cradmin/devilry_listfilter/utils/devilry_with_result_value_renderable.django.html'

    def get_object_name_singular(self, num_matches):
        """
        String representation of the objects listed in singular form.
        """
        return 'object'

    def get_object_name_plural(self, num_matches):
        """
        String representation of the objects listed in plural form.
        """
        return 'objects'

    def get_title(self):
        num_matches = self.kwargs['num_matches']
        if num_matches == 1:
            object_name = self.get_object_name_singular(num_matches=num_matches)
        else:
            object_name = self.get_object_name_plural(num_matches=num_matches)
        return gettext_lazy('Found %(result_num)s of %(total_num)s %(object_name)s') % {
            'result_num': self.kwargs['num_matches'],
            'total_num': self.kwargs['num_total'],
            'object_name': object_name
        }

    def get_base_css_classes_list(self):
        """
        Adds the ``cradmin-legacy-listbuilder-itemvalue-titledescription`` css class
        in addition to the classes added by the superclasses.
        """
        return []


class RowListWithMatchResults(RowList):
    """
    Extends the default RowList with rendering of filter hit count and
    total object count.
    """
    match_result_value_renderable = WithResultValueRenderable
    match_result_frame_renderable = DefaultSpacingItemFrame

    def append_results_renderable(self):
        result_info_renderable = self.match_result_value_renderable(
            value=None,
            num_matches=self.num_matches,
            num_total=self.num_total
        )
        self.renderable_list.insert(0, self.match_result_frame_renderable(inneritem=result_info_renderable))

    def __init__(self, num_matches, num_total, page):
        self.num_matches = num_matches
        self.num_total = num_total
        self.page = page
        super(RowListWithMatchResults, self).__init__()

        if page == 1:
            self.append_results_renderable()
