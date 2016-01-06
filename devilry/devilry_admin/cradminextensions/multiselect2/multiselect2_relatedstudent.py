from django.utils.translation import pgettext_lazy
from django import forms
from django_cradmin.viewhelpers import multiselect2

from devilry.apps.core.models import RelatedStudent


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


class SelectRelatedStudentsForm(forms.Form):
    selected_items = forms.ModelMultipleChoiceField(
        queryset=RelatedStudent.objects.none()
    )

    def __init__(self, *args, **kwargs):
        relatedstudents_queryset = kwargs.pop('relatedstudents_queryset')
        super(SelectRelatedStudentsForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = relatedstudents_queryset
