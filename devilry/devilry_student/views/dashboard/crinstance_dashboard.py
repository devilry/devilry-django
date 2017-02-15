import re

from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_student.cradminextensions import devilry_crmenu_student
from devilry.devilry_student.views.dashboard import allperiods
from devilry.devilry_student.views.dashboard import dashboard


class Menu(devilry_crmenu_student.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        if self.request.cradmin_app.appname == 'allperiods':
            self.add_role_menuitem_object()
            self.add_allperiods_breadcrumb_item(active=True)
        else:
            self.add_role_menuitem_object(active=True)


class CrAdminInstance(devilry_crinstance.BaseCrInstanceStudent):
    id = 'devilry_student'
    menuclass = Menu
    rolefrontpage_appname = 'dashboard'
    flatten_rolefrontpage_url = True

    apps = [
        ('dashboard', dashboard.App),
        ('allperiods', allperiods.App),
    ]

    def has_access(self):
        """
        We give any user access to this instance, including unauthenticated users.
        """
        return self.request.user.is_authenticated()

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        return str(role)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return re.match('^/devilry_student/$', urlpath) or \
            re.match('^/devilry_student/allperiods/.*$', urlpath) or \
            re.match('^/devilry_student/filter/.*$', urlpath)
