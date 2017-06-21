from django import forms
from django.utils.translation import pgettext_lazy
from django_cradmin.viewhelpers import multiselect2
from django_cradmin.viewhelpers import multiselect2view

from devilry.devilry_account.models import User
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter


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


class BaseMultiselectUsersView(multiselect2view.ListbuilderFilterView):
    value_renderer_class = ItemValue
    model = User
    paginate_by = 70

    def add_filterlist_items(self, filterlist):
        filterlist.append(devilry_listfilter.user.Search())

    def get_target_renderer_class(self):
        return Target

    def get_unfiltered_queryset_for_role(self, role):
        return User.objects.order_by('shortname').distinct()

    def get_form_class(self):
        return SelectUsersForm

    def get_form_kwargs(self):
        kwargs = super(BaseMultiselectUsersView, self).get_form_kwargs()
        kwargs['users_queryset'] = self.get_unfiltered_queryset_for_role(
                role=self.request.cradmin_role)
        return kwargs

    def select_all_is_allowed(self):
        return False
