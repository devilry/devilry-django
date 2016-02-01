from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy
from django.views.generic.edit import BaseFormView
from django_cradmin import crapp
from django_cradmin.viewhelpers import delete
from django_cradmin.viewhelpers import objecttable

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedstudent
from devilry.devilry_admin.views.common import bulkimport_users_common
from devilry.devilry_admin.views.common import userselect_common


class GetQuerysetForRoleMixin(object):
    model = RelatedStudent

    def get_queryset_for_role(self, role):
        period = role
        return self.model.objects \
            .filter(period=period) \
            .order_by('user__shortname')


class InfoColumn(objecttable.MultiActionColumn):
    modelfield = 'id'
    template_name = 'devilry_admin/common/user-info-column.django.html'

    def get_header(self):
        return ugettext_lazy('Students')

    def get_buttons(self, obj):
        return [
            objecttable.Button(
                label=ugettext_lazy('Remove'),
                url=self.reverse_appurl('deactivate', args=[obj.id]),
                buttonclass="btn btn-danger btn-sm devilry-relatedstudentlist-deactivate-button"),
        ]

    def get_context_data(self, obj):
        context = super(InfoColumn, self).get_context_data(obj=obj)
        context['relateduser'] = obj.user
        return context


class Overview(listbuilder_relatedstudent.VerticalFilterListView):
    value_renderer_class = listbuilder_relatedstudent.ReadOnlyItemValue
    template_name = 'devilry_admin/period/students/overview.django.html'

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def get_unfiltered_queryset_for_role(self, role):
        period = role
        return self.model.objects \
            .filter(period=period)\
            .select_related('user')

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['period'] = self.request.cradmin_role
        return context


class DeactivateView(GetQuerysetForRoleMixin, delete.DeleteView):
    """
    View used to deactivate students from a period.
    """
    def get_object(self, *args, **kwargs):
        if not hasattr(self, '_object'):
            self._object = super(DeactivateView, self).get_object(*args, **kwargs)
        return self._object

    def get_pagetitle(self):
        return ugettext_lazy('Deactivate student: %(user)s') % {'user': self.get_object().user.get_full_name()}

    def get_success_message(self, object_preview):
        relatedstudent = self.get_object()
        user = relatedstudent.user
        return ugettext_lazy('%(user)s was deactivated.') % {
            'user': user.get_full_name(),
        }

    def get_confirm_message(self):
        relatedstudent = self.get_object()
        period = relatedstudent.period
        user = relatedstudent.user
        return ugettext_lazy(
                'Are you sure you want to make %(user)s '
                'an inactive student for %(period)s? Inactive students '
                'can not be added to new assignments, but they still have access '
                'to assignments that they have already been granted access to. Inactive '
                'students are clearly marked with warning messages throughout the student, examiner '
                'and admin UI, but students and examiners are not notified in any way when you '
                'deactivate a student. You can re-activate a deactivated student at any time.'
        ) % {
            'user': user.get_full_name(),
            'period': period.get_path(),
        }

    def get_action_label(self):
        return ugettext_lazy('Deactivate')

    def delete(self, request, *args, **kwargs):
        object_preview = self.get_object_preview()
        relatedstudent = self.get_object()
        relatedstudent.active = False
        relatedstudent.save()
        self.add_success_messages(object_preview)
        return redirect(self.get_success_url())


class UserInfoColumn(userselect_common.UserInfoColumn):
    modelfield = 'shortname'
    select_label = ugettext_lazy('Add as student')


class UserSelectView(userselect_common.AbstractUserSelectView):
    columns = [
        UserInfoColumn,
    ]

    def get_pagetitle(self):
        return ugettext_lazy('Please select the user you want to add as students for %(what)s') % {
            'what': self.request.cradmin_role.long_name
        }

    def get_form_action(self):
        return self.request.cradmin_app.reverse_appurl('add-user-as-student')

    def get_excluded_user_ids(self):
        period = self.request.cradmin_role
        return period.relatedstudent_set.values_list('user_id', flat=True)

    def get_no_searchresults_message_template_name(self):
        return 'devilry_admin/period/students/userselectview-no-searchresults-message.django.html'


class AddView(BaseFormView):
    """
    View used to add a RelatedStudent to a Period.
    """
    http_method_names = ['post']

    model = RelatedStudent

    def get_form_class(self):
        period = self.request.cradmin_role
        userqueryset = get_user_model().objects \
            .exclude(pk__in=period.relatedstudent_set.values_list('user_id', flat=True))

        class AddAdminForm(forms.Form):
            user = forms.ModelChoiceField(
                queryset=userqueryset)
            next = forms.CharField(required=False)

        return AddAdminForm

    def __make_user_student(self, user):
        period = self.request.cradmin_role
        self.model.objects.create(user=user,
                                  period=period)

    def form_valid(self, form):
        user = form.cleaned_data['user']
        self.__make_user_student(user)

        period = self.request.cradmin_role
        successmessage = ugettext_lazy('%(user)s added as student for %(what)s.') % {
            'user': user.get_full_name(),
            'what': period,
        }
        messages.success(self.request, successmessage)

        if form.cleaned_data['next']:
            nexturl = form.cleaned_data['next']
        else:
            nexturl = self.request.cradmin_app.reverse_appindexurl()
        return HttpResponseRedirect(nexturl)

    def form_invalid(self, form):
        messages.error(self.request,
                       ugettext_lazy('Error: The user may not exist, or it may already be student.'))
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appindexurl())


class ImportStudentsView(bulkimport_users_common.AbstractTypeInUsersView):
    create_button_label = ugettext_lazy('Bulk import students')

    def get_pagetitle(self):
        return ugettext_lazy('Bulk import students')

    def import_users_from_emails(self, emails):
        period = self.request.cradmin_role
        result = RelatedStudent.objects.bulk_create_from_emails(period=period, emails=emails)
        if result.new_relatedusers_was_created():
            messages.success(self.request, ugettext_lazy('Added %(count)s new students to %(period)s.') % {
                'count': result.created_relatedusers_queryset.count(),
                'period': period.get_path()
            })
        else:
            messages.warning(self.request, ugettext_lazy('No new students was added.'))

        if result.existing_relateduser_emails_set:
            messages.info(self.request, ugettext_lazy('%(count)s users was already student on %(period)s.') % {
                'count': len(result.existing_relateduser_emails_set),
                'period': period.get_path()
            })

    def import_users_from_usernames(self, usernames):
        period = self.request.cradmin_role
        result = RelatedStudent.objects.bulk_create_from_usernames(period=period, usernames=usernames)
        if result.new_relatedusers_was_created():
            messages.success(self.request, ugettext_lazy('Added %(count)s new students to %(period)s.') % {
                'count': result.created_relatedusers_queryset.count(),
                'period': period.get_path()
            })
        else:
            messages.warning(self.request, ugettext_lazy('No new students was added.'))

        if result.existing_relateduser_usernames_set:
            messages.info(self.request, ugettext_lazy('%(count)s users was already student on %(period)s.') % {
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
        crapp.Url(r'^select-user-to-add-as-student$',
                  UserSelectView.as_view(),
                  name="select-user-to-add-as-student"),
        crapp.Url(r'^add',
                  AddView.as_view(),
                  name="add-user-as-student"),
        crapp.Url(r'^importstudents',
                  ImportStudentsView.as_view(),
                  name="importstudents"),
    ]
