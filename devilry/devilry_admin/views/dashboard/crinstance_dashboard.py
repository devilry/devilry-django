import re

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu

from django_cradmin import crinstance

from devilry.devilry_account.models import User
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_admin.views.dashboard import overview


class Menu(devilry_crmenu_admin.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        self.add_role_menuitem_object(active=True)


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = User
    apps = [
        ('overview', overview.App),
    ]
    id = 'devilry_admin'
    rolefrontpage_appname = 'overview'
    flatten_rolefrontpage_url = True

    def get_rolequeryset(self):
        return get_user_model().objects.filter(id=self.request.user.id)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        return str(role.id)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return re.match('/devilry_admin/(\d+.*/)?$', urlpath)
