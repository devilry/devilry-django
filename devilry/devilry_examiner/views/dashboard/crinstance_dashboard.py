import re

from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_examiner.cradminextensions import devilry_crmenu_examiner
from devilry.devilry_examiner.views.dashboard import assignmentlist


class Menu(devilry_crmenu_examiner.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        self.add_role_menuitem_object(active=True)


class CrAdminInstance(devilry_crinstance.BaseCrInstanceExaminer):
    menuclass = Menu
    apps = [
        ('assignmentlist', assignmentlist.App),
    ]
    id = 'devilry_examiner'
    rolefrontpage_appname = 'assignmentlist'
    flatten_rolefrontpage_url = True

    def has_access(self):
        """
        We give any user access to this instance as long as they are authenticated.
        """
        return self.request.user.is_authenticated()

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        return str(role.id)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return re.match('^/devilry_examiner/$', urlpath) or \
            re.match('^/devilry_examiner/filter/.*$', urlpath)
