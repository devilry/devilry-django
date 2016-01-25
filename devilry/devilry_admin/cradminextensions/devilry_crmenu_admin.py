from django.utils.translation import pgettext_lazy
from django_cradmin import crmenu
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_cradmin import devilry_crmenu
from django_cradmin import crapp


class Menu(devilry_crmenu.Menu):
    devilryrole = 'admin'

    def add_role_menuitem_object(self, active=False):
        return self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=pgettext_lazy('breadcrumb',
                                'Administrator'),
            url=reverse_cradmin_url(
                instanceid='devilry_admin',
                appname='overview',
                roleid=None,
                viewname=crapp.INDEXVIEW_NAME
            ),
            active=active
        ))

    def add_subject_breadcrumb_item(self, subject, active=False):
        if self.cradmin_instance.get_devilryrole_for_requestuser() == 'periodadmin':
            return None
        else:
            return self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
                label=subject.short_name,
                url=reverse_cradmin_url(
                    instanceid='devilry_admin_subjectadmin',
                    appname='overview',
                    roleid=subject.id,
                    viewname=crapp.INDEXVIEW_NAME
                ),
                active=active
            ))

    def add_period_breadcrumb_item(self, period, active=False):
        if self.cradmin_instance.get_devilryrole_for_requestuser() == 'periodadmin':
            label = period.get_path()
        else:
            label = period.short_name
        return self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=label,
            url=reverse_cradmin_url(
                instanceid='devilry_admin_periodadmin',
                appname='overview',
                roleid=period.id,
                viewname=crapp.INDEXVIEW_NAME
            ),
            active=active
        ))

    def add_assignment_breadcrumb_item(self, assignment, active=False):
        return self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=assignment.short_name,
            url=reverse_cradmin_url(
                instanceid='devilry_admin_assignmentadmin',
                appname='overview',
                roleid=assignment.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            active=active
        ))
