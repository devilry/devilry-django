from django.utils.translation import pgettext_lazy
from django_cradmin.viewhelpers import multiselect2


class SelectedItem(multiselect2.selected_item_renderer.SelectedItem):
    def get_title(self):
        if self.value.user.fullname:
            return self.value.user.fullname
        else:
            return self.value.user.shortname

    def get_description(self):
        if self.value.user.fullname:
            return self.value.user.shortname
        else:
            return ''


class ItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
    valuealias = 'relatedstudent'
    selected_item_renderer_class = SelectedItem

    def get_inputfield_name(self):
        return 'selected_related_students'

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


class Target(multiselect2.target_renderer.Target):
    def get_with_items_title(self):
        return pgettext_lazy('admin multiselect2_relatedstudent',
                             'Selected students')

    def get_without_items_text(self):
        return pgettext_lazy('admin multiselect2_relatedstudent',
                             'No students selected')
