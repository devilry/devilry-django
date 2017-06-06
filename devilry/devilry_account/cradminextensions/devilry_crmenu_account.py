from django.utils.translation import ugettext_lazy
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_cradmin import devilry_crmenu


class Menu(devilry_crmenu.Menu):
    def add_role_menuitem_object(self, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=ugettext_lazy('Account'),
            url=reverse_cradmin_url(
                instanceid='devilry_account',
                appname='account'
            ),
            active=active
        ))
