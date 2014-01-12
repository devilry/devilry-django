from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from .views.feedbackeditor import ApprovedFeedbackEditorView


urlpatterns = patterns('devilry_gradingsystemplugin_approved',
    url('^feedbackeditor/(?P<deliveryid>\d+)$', ApprovedFeedbackEditorView.as_view(),
        name='devilry_gradingsystemplugin_approved_feedbackeditor'),
)
