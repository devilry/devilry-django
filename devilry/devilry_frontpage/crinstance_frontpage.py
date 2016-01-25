import re

from django_cradmin import crinstance

from devilry.devilry_frontpage.cradminextensions import devilry_crmenu_frontpage
from devilry.devilry_frontpage.views import frontpage


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = devilry_crmenu_frontpage.Menu
    apps = [
        ('frontpage', frontpage.App),
    ]
    id = 'devilry_frontpage'
    rolefrontpage_appname = 'frontpage'
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
        return re.match('^/$', urlpath)
