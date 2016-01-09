from django.utils.translation import pgettext_lazy
from django_cradmin import crapp

from devilry.devilry_admin.views.assignment.students import create_groups


class ChooseMethod(create_groups.ChooseMethod):
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


class ConfirmView(create_groups.ConfirmView):
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


class ManualSelectStudentsView(create_groups.ManualSelectStudentsView):
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
