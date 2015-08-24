from django.contrib.auth import get_user_model
from django_cradmin.viewhelpers import objecttable


class UserInfoColumn(objecttable.MultiActionColumn):
    modelfield = 'shortname'
    select_label = None

    def render_value(self, obj):
        user = obj
        return user.get_displayname()

    def get_buttons(self, obj):
        user = obj
        return [
            objecttable.SubmitButton(
                label=self.select_label,
                name='user',
                value=str(user.id),
                buttonclass="btn btn-default btn-sm devilry-admin-userselect-select-button"),
        ]


class AbstractUserSelectView(objecttable.ObjectTableView):
    searchfields = ['shortname', 'fullname']
    hide_column_headers = True
    model = get_user_model()

    def get_excluded_user_ids(self):
        raise NotImplementedError()

    def get_queryset_for_role(self, role):
        excluded_user_ids = self.get_excluded_user_ids()
        queryset = get_user_model().objects.all().order_by('shortname')
        if excluded_user_ids:
            queryset = queryset.exclude(id__in=excluded_user_ids)
        return queryset

    def get_form_action(self):
        raise NotImplementedError()
