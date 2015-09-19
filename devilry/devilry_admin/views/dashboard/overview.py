from django.db import models
from django.utils import timezone

from django.views.generic import TemplateView
from django_cradmin import crapp

from devilry.devilry_account.models import SubjectPermissionGroup, PeriodPermissionGroup


class Overview(TemplateView):
    template_name = 'devilry_admin/dashboard/overview.django.html'

    def __get_all_subjects_where_user_is_subjectadmin(self):
        if not hasattr(self, '_subjects_where_user_is_subjectadmin'):
            subjects = []
            for subjectpermissiongroup in SubjectPermissionGroup.objects\
                    .filter(permissiongroup__users=self.request.user)\
                    .select_related('subject')\
                    .order_by('subject__long_name')\
                    .distinct():
                subjects.append(subjectpermissiongroup.subject)
            self._subjects_where_user_is_subjectadmin = subjects
        return self._subjects_where_user_is_subjectadmin

    def __get_all_periods_where_user_is_subjectadmin_or_periodadmin(self):
        periods = []
        subjects_where_user_is_subjectadmin = self.__get_all_subjects_where_user_is_subjectadmin()
        now = timezone.now()
        for periodpermissiongroup in PeriodPermissionGroup.objects\
                .filter(
                    period__start_time__lt=now,
                    period__end_time__gt=now,
                )\
                .filter(
                    models.Q(permissiongroup__users=self.request.user) |
                    models.Q(period__parentnode__in=subjects_where_user_is_subjectadmin)
                )\
                .select_related('period', 'period__parentnode')\
                .order_by('period__parentnode__long_name', 'period__start_time')\
                .distinct():
            periods.append(periodpermissiongroup.period)
        return periods

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['subjects_where_user_is_subjectadmin'] = \
            self.__get_all_subjects_where_user_is_subjectadmin()
        context['periods_where_user_is_subjectadmin_or_periodadmin'] = \
            self.__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
