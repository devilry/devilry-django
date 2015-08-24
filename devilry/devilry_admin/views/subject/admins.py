from django_cradmin import crapp
from devilry.apps.core.models import Subject
from devilry.devilry_admin.views.common import admins_common


class CommonMixin(object):
    model = Subject.admins.through
    basenodefield = 'subject'


class AdminsListView(CommonMixin, admins_common.AbstractAdminsListView):
    pass


class RemoveAdminView(CommonMixin, admins_common.AbstractRemoveAdminView):
    pass


class AdminUserSelectView(admins_common.AdminUserSelectView):
    pass


class AddAdminView(CommonMixin, admins_common.AbstractAddAdminView):
    pass


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', AdminsListView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^remove/(?P<pk>\d+)$',
            RemoveAdminView.as_view(),
            name="remove"),
        crapp.Url(
            r'^select-user-to-add-as-admin$',
            AdminUserSelectView.as_view(),
            name="select-user-to-add-as-admin"),
        crapp.Url(
            r'^add',
            AddAdminView.as_view(),
            name="add-user-as-admin"),
    ]
