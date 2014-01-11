from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from .views.feedbackdraft_preview import FeedbackDraftPreviewView
from .views.admin.selectplugin import SelectPluginView



urlpatterns = patterns('devilry_gradingsystem',
    url('^feedbackdraft_preview/(?P<deliveryid>\d+)/(?P<draftid>\d+)$', FeedbackDraftPreviewView.as_view(),
        name='devilry_gradingsystem_feedbackdraft_preview'),
    url('^admin/selectplugin/(?P<assignmentid>\d+)$', SelectPluginView.as_view(),
        name='devilry_gradingsystem_admin_selectplugin'),
)