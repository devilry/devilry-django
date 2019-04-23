# -*- coding: utf-8 -*-


from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from cradmin_legacy import crapp

from devilry.devilry_admin.views.assignment.students import create_groups


class RequireUnpublishedAssignmentMixin(object):
    published_assignment_error_message = pgettext_lazy(
            'admin replace_groups',
            'You can not use the replace students wizard on a published assignment. '
            'You can still add new students and remove students without feedback or deliveries.')

    def dispatch(self, *args, **kwargs):
        assignment = self.request.cradmin_role
        if assignment.publishing_time < timezone.now():
            messages.error(self.request, self.published_assignment_error_message)
            return redirect(str(self.request.cradmin_instance.rolefrontpage_url()))
        return super(RequireUnpublishedAssignmentMixin, self).dispatch(*args, **kwargs)


class ChooseMethod(RequireUnpublishedAssignmentMixin, create_groups.ChooseMethod):
    def get_pagetitle(self):
        assignment = self.request.cradmin_role
        return pgettext_lazy('admin create_group', 'Replace students on %(assignment)s') % {
            'assignment': assignment.long_name
        }

    def get_pageheading(self):
        return pgettext_lazy('admin create_group', 'Replace students')

    def get_page_subheading(self):
        return pgettext_lazy('admin create_group',
                             'Please select how you would like to add students. Your current students for this '
                             'assignment will be removed, but you will not be able to remove students with '
                             'deliveries or feedback. You will get a preview of your choice on the next page '
                             'before any students are added.')


class ConfirmView(RequireUnpublishedAssignmentMixin, create_groups.ConfirmView):
    replace_groups = True

    def get_pagetitle(self):
        return pgettext_lazy('admin create_groups',
                             'Confirm that you want to remove the current students '
                             'on %(assignment)s and replace them with the students shown below') % {
            'assignment': self.assignment.long_name
        }

    def get_pageheading(self):
        return pgettext_lazy('admin create_groups',
                             'Confirm that you want to remove the current students on '
                             '%(assignment)s and replace them with the students shown below') % {
            'assignment': self.assignment.long_name
        }


class RelatedStudentMultiselectTarget(create_groups.RelatedStudentMultiselectTarget):
    def get_submit_button_text(self):
        return pgettext_lazy('admin create_groups',
                             'Replace students')


class ManualSelectStudentsView(RequireUnpublishedAssignmentMixin, create_groups.ManualSelectStudentsView):
    multiselect_target_class = RelatedStudentMultiselectTarget
    replace_groups = True


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', ChooseMethod.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^confirm/(?P<selected_students>\w+)/(?P<filters_string>.+)?$',
                  ConfirmView.as_view(),
                  name='confirm'),
        crapp.Url(
            r'^manual-select/(?P<filters_string>.+)?$',
            ManualSelectStudentsView.as_view(),
            name='manual-select'),
    ]
