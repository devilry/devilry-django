

from cradmin_legacy import crapp
from cradmin_legacy.crispylayouts import DangerSubmit
from django.contrib import messages
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy

from devilry.apps.core.models import RelatedStudent, Assignment
from devilry.devilry_account.models import PermissionGroup, User
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedstudent
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relateduser
from devilry.devilry_admin.views.common import bulkimport_users_common
from devilry.devilry_cradmin import devilry_multiselect2
from devilry.devilry_cradmin.viewhelpers import devilry_confirmview


class GetQuerysetForRoleMixin(object):
    model = RelatedStudent

    def get_queryset_for_role(self, role):
        period = role
        return self.model.objects \
            .filter(period=period) \
            .order_by('user__shortname')


class OverviewItemValue(listbuilder_relatedstudent.ReadOnlyItemValue):
    template_name = 'devilry_admin/period/students/overview-itemvalue.django.html'


class Overview(listbuilder_relatedstudent.VerticalFilterListView):
    value_renderer_class = OverviewItemValue
    template_name = 'devilry_admin/period/students/overview.django.html'

    def get_period(self):
        return self.request.cradmin_role

    def add_filterlist_items(self, filterlist):
        super(Overview, self).add_filterlist_items(filterlist=filterlist)
        filterlist.append(listfilter_relateduser.IsActiveFilter())

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def get_unfiltered_queryset_for_role(self, role):
        period = role
        return self.model.objects \
            .filter(period=period)\
            .prefetch_syncsystemtag_objects()\
            .select_related('user').order_by('user__shortname')

    def __user_is_department_admin(self):
        requestuser_devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        return requestuser_devilryrole == PermissionGroup.GROUPTYPE_DEPARTMENTADMIN

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['period'] = self.request.cradmin_role
        context['user_is_department_admin'] = self.__user_is_department_admin()
        return context


class SingleRelatedStudentMixin(GetQuerysetForRoleMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.relatedstudent = self.get_queryset_for_role(role=self.request.cradmin_role)\
                .select_related('user')\
                .get(id=kwargs['pk'])
        except RelatedStudent.DoesNotExist:
            raise Http404()
        return super(SingleRelatedStudentMixin, self).dispatch(request, *args, **kwargs)


class DeactivateView(SingleRelatedStudentMixin, devilry_confirmview.View):
    """
    View used to deactivate students from a period.
    """
    def get_pagetitle(self):
        return gettext_lazy('Deactivate student: %(user)s?') % {
            'user': self.relatedstudent.user.get_full_name(),
        }

    def get_confirm_message(self):
        period = self.request.cradmin_role
        return gettext_lazy(
                'Are you sure you want to make %(user)s '
                'an inactive student for %(period)s? Inactive students '
                'can not be added to new assignments, but they still have access '
                'to assignments that they have already been granted access to. Inactive '
                'students are clearly marked with warning messages throughout the student, examiner '
                'and admin UI, but students and examiners are not notified in any way when you '
                'deactivate a student. You can re-activate a deactivated student at any time.'
        ) % {
            'user': self.relatedstudent.user.get_full_name(),
            'period': period.get_path(),
        }

    def get_submit_button_label(self):
        return gettext_lazy('Deactivate')

    def get_submit_button_class(self):
        return DangerSubmit

    def get_backlink_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_backlink_label(self):
        return gettext_lazy('Back to students on semester overview')

    def __get_success_message(self):
        return gettext_lazy('%(user)s was deactivated.') % {
            'user': self.relatedstudent.user.get_full_name(),
        }

    def form_valid(self, form):
        self.relatedstudent.active = False
        self.relatedstudent.save()
        messages.success(self.request, self.__get_success_message())
        return super(DeactivateView, self).form_valid(form=form)


class ActivateView(SingleRelatedStudentMixin, devilry_confirmview.View):
    def get_context_data(self, **kwargs):
        context = super(ActivateView, self).get_context_data(**kwargs)
        context['period'] = self.request.cradmin_role
        return context

    def get_pagetitle(self):
        return gettext_lazy('Re-activate student: %(user)s?') % {
            'user': self.relatedstudent.user.get_full_name()
        }

    def get_submit_button_label(self):
        return gettext_lazy('Re-activate')

    def get_confirm_message(self):
        return gettext_lazy('Please confirm that you want to re-activate %(user)s.') % {
            'user': self.relatedstudent.user.get_full_name()
        }

    def get_backlink_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_backlink_label(self):
        return gettext_lazy('Back to students on semester overview')

    def get_success_url(self):
        return str(self.request.cradmin_app.reverse_appindexurl())

    def __get_success_message(self):
        return gettext_lazy('%(user)s was re-activated.') % {
            'user': self.relatedstudent.user.get_full_name()
        }

    def form_valid(self, form):
        self.relatedstudent.active = True
        self.relatedstudent.save()
        messages.success(self.request, self.__get_success_message())
        return super(ActivateView, self).form_valid(form=form)


class AddStudentsTarget(devilry_multiselect2.user.Target):
    def get_submit_button_text(self):
        return gettext_lazy('Add selected students')


def students_not_added_to_assignments_warning(request, period):
    assignment_queryset = Assignment.objects.filter(parentnode=period)
    if not assignment_queryset.exists():
        return
    message = render_to_string('devilry_admin/period/students/students-not-added-to-assignments-warning.django.html', {
        'assignment_queryset': assignment_queryset
    })
    messages.info(request, message)

class AddView(devilry_multiselect2.user.BaseMultiselectUsersView):
    value_renderer_class = devilry_multiselect2.user.ItemValue
    template_name = 'devilry_admin/period/students/add.django.html'
    model = User

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'add', kwargs={'filters_string': filters_string})

    def __get_userids_already_relatedstudent_queryset(self):
        period = self.request.cradmin_role
        return RelatedStudent.objects.filter(period=period)\
            .values_list('user_id', flat=True)

    def get_unfiltered_queryset_for_role(self, role):
        return super(AddView, self).get_unfiltered_queryset_for_role(role=self.request.cradmin_role)\
            .exclude(id__in=self.__get_userids_already_relatedstudent_queryset())

    def get_target_renderer_class(self):
        return AddStudentsTarget

    def get_context_data(self, **kwargs):
        context = super(AddView, self).get_context_data(**kwargs)
        context['period'] = self.request.cradmin_role
        return context

    def get_success_url(self):
        return str(self.request.cradmin_app.reverse_appindexurl())

    def __get_success_message(self, added_users):
        added_users_names = ['"{}"'.format(user.get_full_name()) for user in added_users]
        added_users_names.sort()
        return gettext_lazy('Added %(usernames)s.') % {
            'usernames': ', '.join(added_users_names)
        }

    def __create_relatedstudents(self, selected_users):
        period = self.request.cradmin_role
        relatedstudents = []
        for user in selected_users:
            relatedstudent = RelatedStudent(
                    period=period,
                    user=user)
            relatedstudents.append(relatedstudent)
        RelatedStudent.objects.bulk_create(relatedstudents)

    def form_valid(self, form):
        selected_users = list(form.cleaned_data['selected_items'])
        self.__create_relatedstudents(selected_users=selected_users)
        messages.success(self.request, self.__get_success_message(added_users=selected_users))
        students_not_added_to_assignments_warning(
            request=self.request,
            period=self.request.cradmin_role)
        return super(AddView, self).form_valid(form=form)


class ImportStudentsView(bulkimport_users_common.AbstractTypeInUsersView):
    create_button_label = gettext_lazy('Bulk import students')

    def get_backlink_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_backlink_label(self):
        return gettext_lazy('Back to students on semester overview')

    def get_pagetitle(self):
        return gettext_lazy('Bulk import students')

    def import_users_from_emails(self, emails):
        period = self.request.cradmin_role
        result = RelatedStudent.objects.bulk_create_from_emails(period=period, emails=emails)
        if result.new_relatedusers_was_created():
            messages.success(self.request, gettext_lazy('Added %(count)s new students to %(period)s.') % {
                'count': result.created_relatedusers_queryset.count(),
                'period': period.get_path()
            })
            students_not_added_to_assignments_warning(
                request=self.request,
                period=self.request.cradmin_role)
        else:
            messages.warning(self.request, gettext_lazy('No new students was added.'))

        if result.existing_relateduser_emails_set:
            messages.info(self.request, gettext_lazy('%(count)s users was already student on %(period)s.') % {
                'count': len(result.existing_relateduser_emails_set),
                'period': period.get_path()
            })

    def import_users_from_usernames(self, usernames):
        period = self.request.cradmin_role
        result = RelatedStudent.objects.bulk_create_from_usernames(period=period, usernames=usernames)
        if result.new_relatedusers_was_created():
            messages.success(self.request, gettext_lazy('Added %(count)s new students to %(period)s.') % {
                'count': result.created_relatedusers_queryset.count(),
                'period': period.get_path()
            })
            students_not_added_to_assignments_warning(
                request=self.request,
                period=self.request.cradmin_role)
        else:
            messages.warning(self.request, gettext_lazy('No new students was added.'))

        if result.existing_relateduser_usernames_set:
            messages.info(self.request, gettext_lazy('%(count)s users was already student on %(period)s.') % {
                'count': len(result.existing_relateduser_usernames_set),
                'period': period.get_path()
            })


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  Overview.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  Overview.as_view(),
                  name='filter'),
        crapp.Url(r'^deactivate/(?P<pk>\d+)$',
                  DeactivateView.as_view(),
                  name="deactivate"),
        crapp.Url(r'^activate/(?P<pk>\d+)$',
                  ActivateView.as_view(),
                  name="activate"),
        crapp.Url(r'^add/(?P<filters_string>.+)?$',
                  AddView.as_view(),
                  name="add"),
        crapp.Url(r'^importstudents',
                  ImportStudentsView.as_view(),
                  name="importstudents"),
    ]
