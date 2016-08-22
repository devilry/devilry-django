# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url

from devilry.devilry_api.group_comment.views.groupcomment_student import GroupCommentViewStudent
from devilry.devilry_api.group_comment.views.groupcomment_examiner import GroupCommentViewExaminer
urlpatterns = [
    url('^student/(?P<feedback_set>.+)$', GroupCommentViewStudent.as_view(), name='student-group-comment'),
    url('^examiner/(?P<feedback_set>.+)$', GroupCommentViewExaminer.as_view(), name='examiner-group-comment')
]
