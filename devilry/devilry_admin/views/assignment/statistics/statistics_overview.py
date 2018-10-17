# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.utils.translation import pgettext
from django_cradmin import crapp
from django_cradmin.viewhelpers.detail import DetailRoleView

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Examiner, RelatedExaminer


class Overview(DetailRoleView):
    model = coremodels.Assignment
    template_name = 'devilry_admin/assignment/statistics/overview.django.html'

    @property
    def assignment(self):
        return self.request.cradmin_role

    def __examiners_with_published_feedbackset_exist(self):
        return Examiner.objects\
            .filter(
                assignmentgroup__parentnode=self.request.cradmin_role,
                assignmentgroup__cached_data__last_published_feedbackset__isnull=False)\
            .exists()

    def __get_relatedexaminer_ids(self):
        return RelatedExaminer.objects\
            .select_related('user')\
            .filter(period_id=self.assignment.parentnode_id) \
            .filter(examiner__assignmentgroup__parentnode_id=self.assignment.id)\
            .only('id')\
            .distinct('id')\
            .values_list('id', flat=True)

    def get_default_ievv_js_base_widget_config(self):
        return {
            'chart_label': pgettext('devilry_admin assignment examiner statistics', 'Points (average)'),
            'loading_label': pgettext('devilry_admin assignment examiner statistics', 'Fetching data'),
            'assignment_id': self.assignment.id,
            'assignment_max_points': self.assignment.max_points,
            'relatedexaminer_ids': list(self.__get_relatedexaminer_ids())
        }

    def get_examiner_detail_js_base_widget_config(self):
        default_config = self.get_default_ievv_js_base_widget_config()
        default_config.update({
            'groups_corrected_count_label': pgettext(
                'devilry_admin assignment examiner statistics', 'Corrected groups'),
            'groups_with_passing_grade_count_label': pgettext(
                'devilry_admin assignment examiner statistics', 'Groups with passing grade'),
            'groups_with_failing_grade_count_label': pgettext(
                'devilry_admin assignment examiner statistics', 'Groups with failing grade'),
            'groups_waiting_for_feedback_count_label': pgettext(
                'devilry_admin assignment examiner statistics', 'Groups waiting for feedback'),
            'groups_waiting_for_deadline_to_expire_count_label': pgettext(
                'devilry_admin assignment examiner statistics', 'Groups where the deadline has not expired'),
            'points_label': pgettext(
                'devilry_admin assignment examiner statistics', 'Points'),
            'points_average_label': pgettext(
                'devilry_admin assignment examiner statistics', 'Average'),
            'points_highest_label': pgettext(
                'devilry_admin assignment examiner statistics', 'Highest'),
            'points_lowest_label': pgettext(
                'devilry_admin assignment examiner statistics', 'Lowest')
        })
        return default_config

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        default_ievv_js_base_widget_config = self.get_default_ievv_js_base_widget_config()
        context['examiner_average_point_chart_config'] = json.dumps(
            default_ievv_js_base_widget_config)
        context['examiner_percentage_graded_chart_config'] = json.dumps(
            default_ievv_js_base_widget_config)
        context['examiner_detail_config'] = json.dumps(
            self.get_examiner_detail_js_base_widget_config())
        context['examiners_with_published_feedbackset_exist'] = self.__examiners_with_published_feedbackset_exist()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  Overview.as_view(),
                  name=crapp.INDEXVIEW_NAME)
    ]
