from django.urls import re_path
from django.contrib.auth.decorators import login_required

from .views.download_staticfeedbackfileattachment import DownloadStaticFeedbackFileAttachmentView
from .api.applicationstate import ReadyCheck, LiveCheck

urlpatterns = [
    re_path(r'^feedbackfileattachment/(?P<pk>\d+)/(?P<asciifilename>.+)?$',
        login_required(DownloadStaticFeedbackFileAttachmentView.as_view()),
        name='devilry_core_feedbackfileattachment'),
    
    re_path('_api/application-state/ready', ReadyCheck.as_view(), name='devilry_core_application_state_ready'),
    re_path('_api/application-state/alive', LiveCheck.as_view(), name='devilry_core_application_state_alive'),
]
