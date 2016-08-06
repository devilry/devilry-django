# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url

from devilry.devilry_api.feedbackset.views.feedbackset_student import FeedbacksetListViewStudent
from devilry.devilry_api.feedbackset.views.feedbackset_examiner import FeedbacksetListViewExaminer
urlpatterns = [
    url('^student/$', FeedbacksetListViewStudent.as_view(), name='student-feedbackset'),
    url('^examiner/$', FeedbacksetListViewExaminer.as_view(), name='examiner-feedbackset'),
]
