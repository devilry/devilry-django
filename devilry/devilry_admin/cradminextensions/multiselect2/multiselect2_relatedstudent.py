from django import forms
from django.utils.translation import pgettext_lazy
from cradmin_legacy.viewhelpers import multiselect2

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedstudent


class SelectedItem(listbuilder_relatedstudent.RelatedStudentItemValueTitleDescriptionMixin,
                   multiselect2.selected_item_renderer.SelectedItem):
    template_name = 'devilry_admin/multiselect2/multiselect2_relatedstudent/selecteditem.django.html'


class ItemValue(listbuilder_relatedstudent.RelatedStudentItemValueTitleDescriptionMixin,
                multiselect2.listbuilder_itemvalues.ItemValue):
    selected_item_renderer_class = SelectedItem
    template_name = 'devilry_admin/multiselect2/multiselect2_relatedstudent/itemvalue.django.html'


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
