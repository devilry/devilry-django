from django.conf.urls import url

from .views.feedbackeditor import PointsFeedbackBulkEditorView
from .views.feedbackeditor import PointsFeedbackEditorView


urlpatterns = [
    url('^feedbackeditor/(?P<deliveryid>\d+)$', PointsFeedbackEditorView.as_view(),
        name='devilry_gradingsystemplugin_points_feedbackeditor'),
    url('^feedbackbulkeditor/(?P<assignmentid>\d+)$', PointsFeedbackBulkEditorView.as_view(),
        name='devilry_gradingsystemplugin_points_feedbackbulkeditor'),
]
