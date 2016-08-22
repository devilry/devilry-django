# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url

from devilry.devilry_api.feedbackset.views.feedbackset_student import FeedbacksetViewStudent
from devilry.devilry_api.feedbackset.views.feedbackset_examiner import FeedbacksetViewExaminer
urlpatterns = [
    url('^student/$', FeedbacksetViewStudent.as_view(), name='student-feedbackset'),
    url('^examiner/$', FeedbacksetViewExaminer.as_view(), name='examiner-feedbackset'),
]
