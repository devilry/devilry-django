import re

from devilry.devilry_account.cradminextensions import devilry_crmenu_account
from devilry.devilry_account.crapps import account
from devilry.devilry_cradmin import devilry_crinstance


class Menu(devilry_crmenu_account.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        self.add_role_menuitem_object(active=True)


class CrAdminInstance(devilry_crinstance.BaseDevilryCrInstance):
    menuclass = Menu
    roleclass = None
    id = 'devilry_account'
    rolefrontpage_appname = 'account'
    flatten_rolefrontpage_url = True
    apps = [
        ('account', account.App),
    ]

    def get_devilryrole_type(self):
        return None

    def has_access(self):
        """
        We give any user access to this instance, including unauthenticated users.
        """
        return self.request.user.is_authenticated

    @classmethod
    def matches_urlpath(cls, urlpath):
        return re.match('^/account/.*$', urlpath)
