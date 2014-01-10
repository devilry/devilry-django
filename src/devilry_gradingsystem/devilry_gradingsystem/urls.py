from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from .views.feedbackdraft_preview import FeedbackDraftPreviewView



urlpatterns = patterns('devilry_gradingsystem',
    url('^feedbackdraft_preview/(?P<deliveryid>\d+)/(?P<draftid>\d+)$', FeedbackDraftPreviewView.as_view(),
        name='devilry_gradingsystem_feedbackdraft_preview'),
)