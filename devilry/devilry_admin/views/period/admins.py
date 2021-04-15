

from django.contrib import messages
from django.db import models
from django.http import Http404
from django.utils.translation import gettext_lazy
from cradmin_legacy import crapp
from cradmin_legacy.crispylayouts import DangerSubmit
from cradmin_legacy.viewhelpers import listbuilderview

from devilry.devilry_account.models import PermissionGroupUser, PeriodPermissionGroup, PermissionGroup, \
    SubjectPermissionGroup
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_multiselect2
from devilry.devilry_cradmin.viewhelpers import devilry_confirmview


class OverviewItemValue(devilry_listbuilder.permissiongroupuser.ItemValue):
    template_name = 'devilry_admin/period/admins/overview-itemvalue.django.html'


class GetCustomManagablePermissionGroupMixin(object):
    def get_custom_managable_periodpermissiongroup(self):
        period = self.request.cradmin_role
        try:
            return PeriodPermissionGroup.objects\
                .get_custom_managable_periodpermissiongroup_for_period(period=period)
        except PeriodPermissionGroup.DoesNotExist:
            return None


class Overview(GetCustomManagablePermissionGroupMixin, listbuilderview.View):
    value_renderer_class = OverviewItemValue
    template_name = 'devilry_admin/period/admins/overview.django.html'
    model = PermissionGroupUser

    def dispatch(self, request, *args, **kwargs):
        self.custom_managable_periodpermissiongroup = self.get_custom_managable_periodpermissiongroup()
        return super(Overview, self).dispatch(request, *args, **kwargs)

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def get_queryset_for_role(self, role):
        if self.custom_managable_periodpermissiongroup:
            return PermissionGroupUser.objects \
                .filter(permissiongroup=self.custom_managable_periodpermissiongroup.permissiongroup)\
                .select_related('user')\
                .order_by('user__shortname')
        else:
            return PermissionGroupUser.objects.none()

    def __prefetch_permissiongroupuser_queryset(self):
        return PermissionGroupUser.objects\
            .select_related('user')\
            .order_by('user__shortname')

    def __get_periodpermissiongroups(self):
        period = self.request.cradmin_role
        queryset = PeriodPermissionGroup.objects\
            .filter(period=period)\
            .select_related('period')\
            .prefetch_related(
                models.Prefetch(
                        'permissiongroup__permissiongroupuser_set',
                        queryset=self.__prefetch_permissiongroupuser_queryset()))
        if self.custom_managable_periodpermissiongroup:
            queryset = queryset.exclude(id=self.custom_managable_periodpermissiongroup.id)
        return queryset

    def __get_subjectpermissiongroups(self):
        period = self.request.cradmin_role
        return SubjectPermissionGroup.objects\
            .filter(subject=period.subject)\
            .select_related('subject')\
            .prefetch_related(
                models.Prefetch(
                        'permissiongroup__permissiongroupuser_set',
                        queryset=self.__prefetch_permissiongroupuser_queryset()))

    def __make_permissiongroup_listbuilderlist(self):
        listbuilderlist = devilry_listbuilder.permissiongroup.SubjectAndPeriodPermissionGroupList()
        listbuilderlist.add_periodpermissiongroups(
            periodpermissiongroups=self.__get_periodpermissiongroups())
        listbuilderlist.add_subjectpermissiongroups(
            subjectpermissiongroups=self.__get_subjectpermissiongroups())
        return listbuilderlist

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['period'] = self.request.cradmin_role
        context['other_permissiongroups_listbuilderlist'] = self.__make_permissiongroup_listbuilderlist()
        return context


class AddAdminsTarget(devilry_multiselect2.user.Target):
    def get_submit_button_text(self):
        return gettext_lazy('Add selected users as semester admins')


class AddView(GetCustomManagablePermissionGroupMixin,
              devilry_multiselect2.user.BaseMultiselectUsersView):
    template_name = 'devilry_admin/period/admins/add.django.html'

    def dispatch(self, request, *args, **kwargs):
        self.custom_managable_periodpermissiongroup = self.get_custom_managable_periodpermissiongroup()
        return super(AddView, self).dispatch(request, *args, **kwargs)

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'add', kwargs={'filters_string': filters_string})

    def __get_userids_already_admin_queryset(self):
        period = self.request.cradmin_role
        subject = period.subject
        periodpermissiongroups_with_access_to_period = PeriodPermissionGroup.objects\
            .filter(period=period)\
            .values_list('permissiongroup_id', flat=True)
        subjectpermissiongroups_with_access_to_period = SubjectPermissionGroup.objects\
            .filter(subject=subject)\
            .values_list('permissiongroup_id', flat=True)
        return PermissionGroupUser.objects\
            .filter(models.Q(permissiongroup__in=periodpermissiongroups_with_access_to_period) |
                    models.Q(permissiongroup__in=subjectpermissiongroups_with_access_to_period))\
            .values_list('user_id', flat=True)\
            .distinct()

    def get_unfiltered_queryset_for_role(self, role):
        return super(AddView, self).get_unfiltered_queryset_for_role(role=self.request.cradmin_role)\
            .exclude(id__in=self.__get_userids_already_admin_queryset())

    def get_target_renderer_class(self):
        return AddAdminsTarget

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

    def __create_permissiongroup_if_it_does_not_exist(self):
        if self.custom_managable_periodpermissiongroup:
            return self.custom_managable_periodpermissiongroup
        period = self.request.cradmin_role

        permissiongroup = PermissionGroup(
            name='Custom manageable permissiongroup for Period#{}'.format(period.id),
            is_custom_manageable=True,
            grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN
        )
        permissiongroup.full_clean()
        permissiongroup.save()

        periodpermissiongroup = PeriodPermissionGroup(
                permissiongroup=permissiongroup,
                period=period)
        periodpermissiongroup.full_clean()
        periodpermissiongroup.save()
        return periodpermissiongroup

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
        periodpermissiongroup = self.__create_permissiongroup_if_it_does_not_exist()
        self.__create_permissiongroupusers(
                selected_users=selected_users,
                permissiongroup=periodpermissiongroup.permissiongroup)
        messages.success(self.request, self.__get_success_message(added_users=selected_users))
        return super(AddView, self).form_valid(form=form)


class DeleteView(GetCustomManagablePermissionGroupMixin, devilry_confirmview.View):
    """
    View used to deactivate examiners from a period.
    """
    def __get_permissiongroupuser(self, permissiongroup):
        period = self.request.cradmin_role
        try:
            return permissiongroup.permissiongroupuser_set.get(pk=self.kwargs['pk'])
        except PermissionGroupUser.DoesNotExist:
            raise Http404(
                    'No PermissionGroupUser in custom managable '
                    'permissiongroup for Period#{} found.'.format(
                            period.id))

    def dispatch(self, request, *args, **kwargs):
        period = self.request.cradmin_role
        self.custom_managable_periodpermissiongroup = self.get_custom_managable_periodpermissiongroup()
        if self.custom_managable_periodpermissiongroup is None:
            raise Http404('No custom managable permissiongroup for Period#{} found.'.format(
                period.id))
        self.permissiongroupuser = self.__get_permissiongroupuser(
            permissiongroup=self.custom_managable_periodpermissiongroup.permissiongroup)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_pagetitle(self):
        return gettext_lazy('Remove semester administrator: %(user)s?') % {
            'user': self.permissiongroupuser.user.get_full_name(),
        }

    def get_confirm_message(self):
        period = self.request.cradmin_role
        return gettext_lazy(
                'Are you sure you want to remove %(user)s as semester administrator '
                'for %(period)s? You can re-add a removed administrator at any time.'
        ) % {
            'user': self.permissiongroupuser.user.get_full_name(),
            'period': period.get_path(),
        }

    def get_submit_button_label(self):
        return gettext_lazy('Remove')

    def get_submit_button_class(self):
        return DangerSubmit

    def get_backlink_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_backlink_label(self):
        return gettext_lazy('Back to admins on semester overview')

    def __get_success_message(self):
        period = self.request.cradmin_role
        return gettext_lazy('%(user)s is no longer semester administrator for %(period)s.') % {
            'user': self.permissiongroupuser.user.get_full_name(),
            'period': period.get_path(),
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
