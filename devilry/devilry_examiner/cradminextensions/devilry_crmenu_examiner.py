from django.template import defaultfilters
from django.utils.translation import pgettext_lazy
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_cradmin import devilry_crmenu


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

    def __get_candidate_names(self, group):
        # assignment = group.assignment
        # TODO: If assignment.anynymizationmode ....
        return [
            candidate.relatedstudent.user.get_full_name()
            for candidate in group.candidates.all()]

    def get_group_label(self, group):
        names = self.__get_candidate_names(group=group)
        if names:
            return u', '.join(names)
        else:
            return u'#{}'.format(group.id)

    def add_group_breadcrumb_item(self, group, active=False):
        self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
            label=defaultfilters.truncatechars(self.get_group_label(group=group), 25),
            url=reverse_cradmin_url(
                instanceid='devilry_group_examiner',
                appname='feedbackfeed',
                roleid=group.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            active=active
        ))
