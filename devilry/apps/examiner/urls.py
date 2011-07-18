from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from restful import examiner_restful
from views import MainView
from feedbackeditorviews import FeedbackEditorView

urlpatterns = patterns('devilry.apps.examiner',
                       url(r'^$', login_required(MainView.as_view()), name='examiner'),
                       url(r'^create-feedback/(?P<deliveryid>\d+)$',
                           login_required(FeedbackEditorView.as_view()),
                           name='examiner-create-feedback')
                      )

urlpatterns += examiner_restful
