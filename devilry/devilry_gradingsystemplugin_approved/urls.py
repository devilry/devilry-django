from django.urls import re_path

from .views.feedbackeditor import ApprovedFeedbackBulkEditorView
from .views.feedbackeditor import ApprovedFeedbackEditorView


urlpatterns = [
    re_path('^feedbackeditor/(?P<deliveryid>\d+)$', ApprovedFeedbackEditorView.as_view(),
        name='devilry_gradingsystemplugin_approved_feedbackeditor'),
    re_path('^feedbackbulkeditor/(?P<assignmentid>\d+)$', ApprovedFeedbackBulkEditorView.as_view(),
        name='devilry_gradingsystemplugin_approved_feedbackbulkeditor'),
]
