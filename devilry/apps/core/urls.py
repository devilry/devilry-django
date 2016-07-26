from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views.download_staticfeedbackfileattachment import DownloadStaticFeedbackFileAttachmentView

urlpatterns = [
    url(r'^feedbackfileattachment/(?P<pk>\d+)/(?P<asciifilename>.+)?$',
        login_required(DownloadStaticFeedbackFileAttachmentView.as_view()),
        name='devilry_core_feedbackfileattachment'),
]
