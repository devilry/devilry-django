import re

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu

from django_cradmin import crinstance

from devilry.devilry_account.models import User
from devilry.devilry_admin.views.dashboard import overview


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add_menuitem(
            label=_('Dashboard'),
            active=self.request.cradmin_app.appname == 'overview',
            url=self.appindex_url('overview'))


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = User
    apps = [
        ('overview', overview.App),
    ]
    id = 'devilry_admin'
    rolefrontpage_appname = 'overview'

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
        return re.match('/devilry_admin/(\d+.*|$)', urlpath)
