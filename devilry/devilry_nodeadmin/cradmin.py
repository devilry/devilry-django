from devilry.apps.core.models.node import Node

from django_cradmin import crmenu, crinstance

from .crapps import dashboard
from .crapps import pages


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add(label=_('Dashboard'), url=self.appindex_url('dashboard'), icon="home",
                 active=self.request.cradmin_app.appname == 'dashboard')


class NodeListingCrAdminInstance(crinstance.BaseCrAdminInstance):
    id = 'nodepermission_listing'
    menuclass = Menu
    roleclass = Node
    rolefrontpage_appname = 'nodeadmin_index'

    apps = [
        ('dashboard', dashboard.App),
    ]

    def get_rolequeryset(self):
        '''

        :return:
        '''

    def get_titletext_for_role(self, role):
        '''

        :param role:
        :return:
        '''

    def get_descriptiontext_for_role(self, role):
        '''

        :param role:
        :return:
        '''

    @classmethod
    def matches_urlpath(cls, urlpath):
        '''

        :param cls:
        :param urlpath:
        :return:
        '''