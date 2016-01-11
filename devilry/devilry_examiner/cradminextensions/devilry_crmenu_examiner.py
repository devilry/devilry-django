from django.utils.translation import pgettext_lazy
from django_cradmin import crmenu
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_cradmin import devilry_crmenu
from django_cradmin import crapp


class Menu(devilry_crmenu.Menu):
    devilryrole = 'examiner'

    def add_role_menuitem_object(self, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=pgettext_lazy('breadcrumb',
                                'Examiner'),
            url=reverse_cradmin_url(
                instanceid='devilry_examiner',
                appname='assignmentlist',
                roleid=self.request.user.id,
                viewname=crapp.INDEXVIEW_NAME
            ),
            active=active
        ))

    def add_assignment_breadcrumb_item(self, assignment, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=assignment.get_path(),
            url=reverse_cradmin_url(
                instanceid='devilry_examiner_assignment',
                appname='grouplist',
                roleid=assignment.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            active=active
        ))
