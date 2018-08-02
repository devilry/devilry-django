from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin import crapp

from devilry.apps.core.models import Subject
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_admin.views.subject_for_period_admin import overview_for_periodadmin, subject_redirect
from devilry.devilry_cradmin import devilry_crmenu


class Menu(devilry_crmenu_admin.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        subject = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_subject_breadcrumb_item(subject=subject, active=True)

    def add_subject_breadcrumb_item(self, subject, active=False):
        return self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=subject.short_name,
            url=reverse_cradmin_url(
                instanceid='devilry_admin_subject_for_periodadmin',
                appname='overview',
                roleid=subject.id,
                viewname=crapp.INDEXVIEW_NAME
            ),
            active=active
        ))


class CrAdminInstance(devilry_crinstance.BaseCrInstanceAdmin):
    menuclass = Menu
    roleclass = Subject
    apps = [
        ('overview', overview_for_periodadmin.App),
        ('subject_redirect', subject_redirect.App)
    ]
    id = 'devilry_admin_subject_for_periodadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Subject.objects.filter_user_is_admin_for_any_periods_within_subject(user=self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a Subject.
        """
        subject = role
        return subject

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_admin/subject_for_periodadmin')

    def get_devilryrole_for_requestuser(self):
        """
        Only period admins will be redirected back to this crinstance
        """
        return 'periodadmin'
