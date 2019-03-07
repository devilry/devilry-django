

from django.template import defaultfilters
from django.utils.translation import pgettext_lazy
from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url

from devilry.devilry_cradmin import devilry_crmenu


class Menu(devilry_crmenu.Menu):
    devilryrole = 'student'

    def add_role_menuitem_object(self, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=pgettext_lazy('breadcrumb',
                                'Student'),
            url=reverse_cradmin_url(
                instanceid='devilry_student',
                appname='dashboard',
                roleid=None,
                viewname=crapp.INDEXVIEW_NAME
            ),
            active=active
        ))

    def add_allperiods_breadcrumb_item(self, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=pgettext_lazy('student', 'Your courses'),
            url=reverse_cradmin_url(
                instanceid='devilry_student',
                appname='allperiods',
                roleid=None,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            active=active
        ))

    def add_singleperiods_breadcrumb_item(self, period, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=period.get_path(),
            url=reverse_cradmin_url(
                instanceid='devilry_student_period',
                appname='overview',
                roleid=period.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            active=active
        ))

    def get_group_label(self, group):
        return group.assignment.short_name

    def add_group_breadcrumb_item(self, group, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=defaultfilters.truncatechars(self.get_group_label(group), 25),
            url=reverse_cradmin_url(
                instanceid='devilry_group_student',
                appname='feedbackfeed',
                roleid=group.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            active=active
        ))
