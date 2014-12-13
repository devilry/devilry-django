from django.conf.urls import patterns
from django.conf.urls import url

from .views.feedbackeditor import ApprovedFeedbackEditorView
from .views.feedbackeditor import ApprovedFeedbackBulkEditorView


urlpatterns = patterns('devilry.devilry_gradingsystemplugin_approved',
    url('^feedbackeditor/(?P<deliveryid>\d+)$', ApprovedFeedbackEditorView.as_view(),
        name='devilry_gradingsystemplugin_approved_feedbackeditor'),
    url('^feedbackbulkeditor/(?P<assignmentid>\d+)$', ApprovedFeedbackBulkEditorView.as_view(),
        name='devilry_gradingsystemplugin_approved_feedbackbulkeditor'),
)
