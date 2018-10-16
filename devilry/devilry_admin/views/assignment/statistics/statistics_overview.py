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

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['ievv_jsbase_widget_config'] = json.dumps({
            'chart_label': pgettext('devilry_admin assignment statistics', 'Points (average)'),
            'loading_label': pgettext('devilry_admin assignment statistics', 'Fetching data'),
            'assignment_id': self.assignment.id,
            'assignment_max_points': self.assignment.max_points,
            'relatedexaminer_ids': list(self.__get_relatedexaminer_ids())
        })
        context['examiners_with_published_feedbackset_exist'] = self.__examiners_with_published_feedbackset_exist()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  Overview.as_view(),
                  name=crapp.INDEXVIEW_NAME)
    ]
