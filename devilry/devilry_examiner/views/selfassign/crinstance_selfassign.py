import re

from devilry.apps.core.models import Period, RelatedExaminer
from devilry.devilry_examiner.cradminextensions import devilry_crmenu_examiner
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_examiner.views.selfassign import selfassign, utils


class Menu(devilry_crmenu_examiner.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        self.add_role_menuitem_object()


class CrAdminInstance(devilry_crinstance.BaseCrInstanceExaminer):
    menuclass = Menu
    roleclass = Period
    apps = [
        ('self-assign', selfassign.App)
    ]
    id = 'devilry_examiner_selfassign'
    rolefrontpage_appname = 'self-assign'
    flatten_rolefrontpage_url = True

    def get_rolequeryset(self):
        return utils.selfassign_available_periods(user=self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        period = role
        return period.get_path()

    @property
    def period(self):
        return self.request.cradmin_role

    @classmethod
    def matches_urlpath(cls, urlpath):
        return re.match('^/devilry_examiner/self-assign/.*$', urlpath)
