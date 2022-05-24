import re

from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url

from devilry.apps.core.models import Period
from devilry.devilry_cradmin import devilry_crmenu
from devilry.devilry_examiner.cradminextensions import devilry_crmenu_examiner
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_examiner.views.selfassign import selfassign, utils


class Menu(devilry_crmenu_examiner.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        period = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=period.get_path(),
            url=reverse_cradmin_url(
                instanceid='devilry_examiner_selfassign',
                appname='self-assign',
                roleid=period.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            active=True
        ))



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
