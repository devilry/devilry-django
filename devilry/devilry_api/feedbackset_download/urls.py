# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url

from devilry.devilry_api.feedbackset_download.views.feedbackset_download_examiner import ExaminerFeedbacksetView
from devilry.devilry_api.feedbackset_download.views.feedbackset_download_student import StudentFeedbacksetView
urlpatterns = [
    url(r'^examiner/(?P<content_id>.+)$', ExaminerFeedbacksetView.as_view(), name='examiner-feedbackset-download'),
    url(r'^student/(?P<content_id>.+)$', StudentFeedbacksetView.as_view(), name='student-feedbackset-download')
]
