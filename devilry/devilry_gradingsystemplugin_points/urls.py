from django.conf.urls import patterns
from django.conf.urls import url

from .views.feedbackeditor import PointsFeedbackEditorView
from .views.feedbackeditor import PointsFeedbackBulkEditorView


urlpatterns = patterns('devilry.devilry_gradingsystemplugin_points',
    url('^feedbackeditor/(?P<deliveryid>\d+)$', PointsFeedbackEditorView.as_view(),
        name='devilry_gradingsystemplugin_points_feedbackeditor'),
    url('^feedbackbulkeditor/(?P<assignmentid>\d+)$', PointsFeedbackBulkEditorView.as_view(),
        name='devilry_gradingsystemplugin_points_feedbackbulkeditor'),
)
