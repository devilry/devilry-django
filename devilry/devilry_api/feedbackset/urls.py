# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url

from devilry.devilry_api.feedbackset.views.feedbackset_student import FeedbacksetViewStudent
from devilry.devilry_api.feedbackset.views.feedbackset_examiner import FeedbacksetViewExaminer
from devilry.devilry_api.feedbackset.views.feedbackset_period_admin import FeedbacksetViewPeriodAdmin
urlpatterns = [
    url('^student/$', FeedbacksetViewStudent.as_view(), name='student-feedbackset'),
    url('^examiner/$', FeedbacksetViewExaminer.as_view(), name='examiner-feedbackset'),
    url('^period-admin/$', FeedbacksetViewPeriodAdmin.as_view(), name='period-admin-feedbackset')
]
