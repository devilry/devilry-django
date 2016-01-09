from django.utils.translation import pgettext_lazy
from django_cradmin import crmenu
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_cradmin import devilry_crmenu
from django_cradmin import crapp


class Menu(devilry_crmenu.Menu):
    devilryrole = 'admin'

    def add_role_menuitem_object(self, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=pgettext_lazy('breadcrumb',
                                'Administrator'),
            url=reverse_cradmin_url(
                instanceid='devilry_admin',
                appname='overview',
                roleid=self.request.user.id,
                viewname=crapp.INDEXVIEW_NAME
            ),
            active=active
        ))

    def add_subject_breadcrumb_item(self, subject, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=subject.short_name,
            url=reverse_cradmin_url(
                instanceid='devilry_admin_subjectadmin',
                appname='overview',
                roleid=self.request.user.id,
                viewname=crapp.INDEXVIEW_NAME
            ),
            active=active
        ))

    def add_period_breadcrumb_item(self, period, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=period.short_name,
            url=reverse_cradmin_url(
                instanceid='devilry_admin_periodadmin',
                appname='overview',
                roleid=self.request.user.id,
                viewname=crapp.INDEXVIEW_NAME
            ),
            active=active
        ))

    def add_assignment_breadcrumb_item(self, assignment, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=assignment.short_name,
            url=reverse_cradmin_url(
                instanceid='devilry_admin_assignmentadmin',
                appname='overview',
                roleid=self.request.user.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            active=active
        ))
