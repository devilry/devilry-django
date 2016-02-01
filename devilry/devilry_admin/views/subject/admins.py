from __future__ import unicode_literals

from django.contrib import messages
from django.db import models
from django.http import Http404
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp
from django_cradmin.crispylayouts import DangerSubmit
from django_cradmin.viewhelpers import listbuilderview

from devilry.devilry_account.models import PermissionGroupUser, PermissionGroup, \
    SubjectPermissionGroup
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_multiselect2
from devilry.devilry_cradmin.viewhelpers import devilry_confirmview


class OverviewItemValue(devilry_listbuilder.permissiongroupuser.ItemValue):
    template_name = 'devilry_admin/subject/admins/overview-itemvalue.django.html'


class GetCustomManagablePermissionGroupMixin(object):
    def get_custom_managable_subjectpermissiongroup(self):
        subject = self.request.cradmin_role
        try:
            return SubjectPermissionGroup.objects\
                .get_custom_managable_subjectpermissiongroup_for_subject(subject=subject)
        except SubjectPermissionGroup.DoesNotExist:
            return None


class Overview(GetCustomManagablePermissionGroupMixin, listbuilderview.View):
    value_renderer_class = OverviewItemValue
    template_name = 'devilry_admin/subject/admins/overview.django.html'
    model = PermissionGroupUser

    def dispatch(self, request, *args, **kwargs):
        self.custom_managable_subjectpermissiongroup = self.get_custom_managable_subjectpermissiongroup()
        return super(Overview, self).dispatch(request, *args, **kwargs)

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def get_queryset_for_role(self, role):
        if self.custom_managable_subjectpermissiongroup:
            return PermissionGroupUser.objects \
                .filter(permissiongroup=self.custom_managable_subjectpermissiongroup.permissiongroup)\
                .select_related('user')\
                .order_by('user__shortname')
        else:
            return PermissionGroupUser.objects.none()

    def __prefetch_permissiongroupuser_queryset(self):
        return PermissionGroupUser.objects\
            .select_related('user')\
            .order_by('user__shortname')

    def __get_subjectpermissiongroups(self):
        subject = self.request.cradmin_role
        queryset = SubjectPermissionGroup.objects\
            .filter(subject=subject)\
            .select_related('subject')\
            .prefetch_related(
                models.Prefetch(
                        'permissiongroup__permissiongroupuser_set',
                        queryset=self.__prefetch_permissiongroupuser_queryset()))
        if self.custom_managable_subjectpermissiongroup:
            queryset = queryset.exclude(id=self.custom_managable_subjectpermissiongroup.id)
        return queryset

    def __make_permissiongroup_listbuilderlist(self):
        listbuilderlist = devilry_listbuilder.permissiongroup.SubjectAndPeriodPermissionGroupList()
        listbuilderlist.add_subjectpermissiongroups(
            subjectpermissiongroups=self.__get_subjectpermissiongroups())
        return listbuilderlist

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['subject'] = self.request.cradmin_role
        context['other_permissiongroups_listbuilderlist'] = self.__make_permissiongroup_listbuilderlist()
        return context


class AddAdminsTarget(devilry_multiselect2.user.Target):
    def get_submit_button_text(self):
        return ugettext_lazy('Add selected users as course admins')


class AddView(GetCustomManagablePermissionGroupMixin,
              devilry_multiselect2.user.BaseMultiselectUsersView):
    template_name = 'devilry_admin/subject/admins/add.django.html'

    def dispatch(self, request, *args, **kwargs):
        self.custom_managable_subjectpermissiongroup = self.get_custom_managable_subjectpermissiongroup()
        return super(AddView, self).dispatch(request, *args, **kwargs)

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'add', kwargs={'filters_string': filters_string})

    def __get_userids_already_admin_queryset(self):
        subject = self.request.cradmin_role
        subjectpermissiongroups_with_access_to_subject = SubjectPermissionGroup.objects\
            .filter(subject=subject)\
            .values_list('permissiongroup_id', flat=True)
        return PermissionGroupUser.objects\
            .filter(permissiongroup__in=subjectpermissiongroups_with_access_to_subject)\
            .values_list('user_id', flat=True)\
            .distinct()

    def get_unfiltered_queryset_for_role(self, role):
        return super(AddView, self).get_unfiltered_queryset_for_role(role=self.request.cradmin_role)\
            .exclude(id__in=self.__get_userids_already_admin_queryset())

    def get_target_renderer_class(self):
        return AddAdminsTarget

    def get_context_data(self, **kwargs):
        context = super(AddView, self).get_context_data(**kwargs)
        context['subject'] = self.request.cradmin_role
        return context

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def __get_success_message(self, added_users):
        added_users_names = ['"{}"'.format(user.get_full_name()) for user in added_users]
        added_users_names.sort()
        return ugettext_lazy('Added %(usernames)s.') % {
            'usernames': ', '.join(added_users_names)
        }

    def __create_permissiongroup_if_it_does_not_exist(self):
        if self.custom_managable_subjectpermissiongroup:
            return self.custom_managable_subjectpermissiongroup
        subject = self.request.cradmin_role

        permissiongroup = PermissionGroup(
            name='Custom manageable permissiongroup for Subject#{}'.format(subject.id),
            is_custom_manageable=True,
            grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN
        )
        permissiongroup.full_clean()
        permissiongroup.save()

        subjectpermissiongroup = SubjectPermissionGroup(
                permissiongroup=permissiongroup,
                subject=subject)
        subjectpermissiongroup.full_clean()
        subjectpermissiongroup.save()
        return subjectpermissiongroup

    def __create_permissiongroupusers(self, selected_users, permissiongroup):
        permissiongroupusers = []
        for user in selected_users:
            permissiongroupuser = PermissionGroupUser(
                    permissiongroup=permissiongroup,
                    user=user)
            permissiongroupusers.append(permissiongroupuser)
        PermissionGroupUser.objects.bulk_create(permissiongroupusers)

    def form_valid(self, form):
        selected_users = list(form.cleaned_data['selected_items'])
        subjectpermissiongroup = self.__create_permissiongroup_if_it_does_not_exist()
        self.__create_permissiongroupusers(
                selected_users=selected_users,
                permissiongroup=subjectpermissiongroup.permissiongroup)
        messages.success(self.request, self.__get_success_message(added_users=selected_users))
        return super(AddView, self).form_valid(form=form)


class DeleteView(GetCustomManagablePermissionGroupMixin, devilry_confirmview.View):
    """
    View used to deactivate examiners from a subject.
    """
    def __get_permissiongroupuser(self, permissiongroup):
        subject = self.request.cradmin_role
        try:
            return permissiongroup.permissiongroupuser_set.get(pk=self.kwargs['pk'])
        except PermissionGroupUser.DoesNotExist:
            raise Http404(
                    'No PermissionGroupUser in custom managable '
                    'permissiongroup for Subject#{} found.'.format(
                            subject.id))

    def dispatch(self, request, *args, **kwargs):
        subject = self.request.cradmin_role
        self.custom_managable_subjectpermissiongroup = self.get_custom_managable_subjectpermissiongroup()
        if self.custom_managable_subjectpermissiongroup is None:
            raise Http404('No custom managable permissiongroup for Subject#{} found.'.format(
                subject.id))
        self.permissiongroupuser = self.__get_permissiongroupuser(
            permissiongroup=self.custom_managable_subjectpermissiongroup.permissiongroup)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_pagetitle(self):
        return ugettext_lazy('Remove course administrator: %(user)s?') % {
            'user': self.permissiongroupuser.user.get_full_name(),
        }

    def get_confirm_message(self):
        subject = self.request.cradmin_role
        return ugettext_lazy(
                'Are you sure you want to remove %(user)s as course administrator '
                'for %(subject)s? You can re-add a removed administrator at any time.'
        ) % {
            'user': self.permissiongroupuser.user.get_full_name(),
            'subject': subject.short_name,
        }

    def get_submit_button_label(self):
        return ugettext_lazy('Remove')

    def get_submit_button_class(self):
        return DangerSubmit

    def get_backlink_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_backlink_label(self):
        return ugettext_lazy('Back to admins on course overview')

    def __get_success_message(self):
        subject = self.request.cradmin_role
        return ugettext_lazy('%(user)s is no longer course administrator for %(subject)s.') % {
            'user': self.permissiongroupuser.user.get_full_name(),
            'subject': subject.short_name,
        }

    def form_valid(self, form):
        self.permissiongroupuser.delete()
        messages.success(self.request, self.__get_success_message())
        return super(DeleteView, self).form_valid(form=form)


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^add/(?P<filters_string>.+)?$',
                  AddView.as_view(),
                  name="add"),
        crapp.Url(r'^delete/(?P<pk>\d+)$',
                  DeleteView.as_view(),
                  name="delete"),
    ]
