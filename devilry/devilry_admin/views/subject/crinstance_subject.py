from django_cradmin import crinstance

from devilry.apps.core.models import Subject
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_admin.views.subject import admins
from devilry.devilry_admin.views.subject import createperiod
from devilry.devilry_admin.views.subject import overview


class Menu(devilry_crmenu_admin.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        subject = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_subject_breadcrumb_item(subject=subject, active=True)


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Subject
    apps = [
        ('overview', overview.App),
        ('admins', admins.App),
        ('createperiod', createperiod.App)
    ]
    id = 'devilry_admin_subjectadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Subject.objects.filter_user_is_admin(user=self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a Subject.
        """
        subject = role
        return subject

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_admin/subject')
