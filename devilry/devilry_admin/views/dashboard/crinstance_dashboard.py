import re

from devilry.devilry_admin.views.dashboard import createsubject
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_admin.views.dashboard import overview
from devilry.devilry_admin.views.dashboard import student_feedbackfeed_wizard


class Menu(devilry_crmenu_admin.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        self.add_role_menuitem_object(active=True)


class CrAdminInstance(devilry_crinstance.BaseCrInstanceAdmin):
    menuclass = Menu
    apps = [
        ('overview', overview.App),
        ('createsubject', createsubject.App),
        ('studentfeedbackfeedwizard', student_feedbackfeed_wizard.App)
    ]
    id = 'devilry_admin'
    rolefrontpage_appname = 'overview'
    flatten_rolefrontpage_url = True

    def has_access(self):
        """
        We give any user access to this instance as long as they are authenticated.
        """
        return self.request.user.is_authenticated

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        return str(role.id)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return re.match('/devilry_admin/', urlpath)
