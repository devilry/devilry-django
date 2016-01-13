from django.db import models
from itertools import groupby

from django.views.generic import TemplateView
from django_cradmin import crapp

from devilry.apps.core.models import Period, Subject
from devilry.devilry_account.models import SubjectPermissionGroup, PeriodPermissionGroup


class Overview(TemplateView):
    template_name = 'devilry_admin/dashboard/overview.django.html'

    def __get_all_subjects_where_user_is_subjectadmin(self):
        return Subject.objects.filter_user_is_admin(user=self.request.user)\
            .order_by('long_name')\
            .distinct()

    def __get_all_periods_where_user_is_subjectadmin_or_periodadmin(self):
        groups = []
        periods = Period.objects.filter_user_is_admin(user=self.request.user)\
            .select_related('parentnode')\
            .order_by('short_name', 'parentnode__long_name')\
            .distinct()
        for key, items in groupby(periods, lambda period: period.short_name):
            groups.append(list(items))
        return groups

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
