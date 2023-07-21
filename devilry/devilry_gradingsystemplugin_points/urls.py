from django.urls import re_path

from .views.feedbackeditor import PointsFeedbackBulkEditorView
from .views.feedbackeditor import PointsFeedbackEditorView


urlpatterns = [
    re_path('^feedbackeditor/(?P<deliveryid>\d+)$', PointsFeedbackEditorView.as_view(),
        name='devilry_gradingsystemplugin_points_feedbackeditor'),
    re_path('^feedbackbulkeditor/(?P<assignmentid>\d+)$', PointsFeedbackBulkEditorView.as_view(),
        name='devilry_gradingsystemplugin_points_feedbackbulkeditor'),
]
