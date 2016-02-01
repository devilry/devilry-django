from django import forms
from django.utils.translation import pgettext_lazy
from django_cradmin.viewhelpers import multiselect2

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_account.models import User
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedstudent
from devilry.devilry_cradmin import devilry_listbuilder


class SelectedItem(devilry_listbuilder.user.UserTitleDescriptionMixin,
                   multiselect2.selected_item_renderer.SelectedItem):
    valuealias = 'user'


class ItemValue(devilry_listbuilder.user.UserTitleDescriptionMixin,
                multiselect2.listbuilder_itemvalues.ItemValue):
    valuealias = 'user'
    selected_item_renderer_class = SelectedItem


class Target(multiselect2.target_renderer.Target):
    def get_with_items_title(self):
        return pgettext_lazy('admin multiselect2_users',
                             'Selected users')

    def get_without_items_text(self):
        return pgettext_lazy('admin multiselect2_users',
                             'No users selected')


class SelectUsersForm(forms.Form):
    selected_items = forms.ModelMultipleChoiceField(
        widget=forms.MultipleHiddenInput,
        queryset=User.objects.none())

    def __init__(self, *args, **kwargs):
        users_queryset = kwargs.pop('users_queryset')
        super(SelectUsersForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = users_queryset
