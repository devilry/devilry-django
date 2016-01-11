import re

from django_cradmin import crinstance

from devilry.apps.core.models import Assignment
from devilry.devilry_examiner.cradminextensions import devilry_crmenu_examiner
from devilry.devilry_examiner.views.assignment import grouplist


class Menu(devilry_crmenu_examiner.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        assignment = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_assignment_breadcrumb_item(assignment=assignment, active=True)


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Assignment
    apps = [
        ('grouplist', grouplist.App),
    ]
    id = 'devilry_examiner_assignment'
    rolefrontpage_appname = 'grouplist'
    flatten_rolefrontpage_url = True

    def get_rolequeryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        assignment = role
        return assignment.get_path()

    @classmethod
    def matches_urlpath(cls, urlpath):
        return re.match('^/devilry_examiner/assignment/.*$', urlpath)
