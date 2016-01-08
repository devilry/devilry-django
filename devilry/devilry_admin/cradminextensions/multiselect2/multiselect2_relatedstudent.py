from django import forms
from django.utils.translation import pgettext_lazy
from django_cradmin.viewhelpers import multiselect2

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedstudent


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


class ItemValue(listbuilder_relatedstudent.RelatedStudentItemValueTitleDescriptionMixin,
                multiselect2.listbuilder_itemvalues.ItemValue):
    selected_item_renderer_class = SelectedItem


class Target(multiselect2.target_renderer.Target):
    def get_with_items_title(self):
        return pgettext_lazy('admin multiselect2_relatedstudent',
                             'Selected students')

    def get_without_items_text(self):
        return pgettext_lazy('admin multiselect2_relatedstudent',
                             'No students selected')


class SelectRelatedStudentsForm(forms.Form):
    selected_items = forms.ModelMultipleChoiceField(
        widget=forms.MultipleHiddenInput,
        queryset=RelatedStudent.objects.none())

    def __init__(self, *args, **kwargs):
        relatedstudents_queryset = kwargs.pop('relatedstudents_queryset')
        super(SelectRelatedStudentsForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = relatedstudents_queryset
