# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url

from devilry.devilry_api.group_comment.views.groupcomment_student import GroupCommentViewStudent

urlpatterns = [
    url('^student/(?P<feedback_set>.+)$', GroupCommentViewStudent.as_view(), name='student-group-comment'),
]
