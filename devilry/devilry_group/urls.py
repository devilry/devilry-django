# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# django imports
from django.conf.urls import url, include

# devilry imports
from devilry.devilry_group.cradmin_instances import crinstance_admin
from devilry.devilry_group.cradmin_instances import crinstance_examiner
from devilry.devilry_group.cradmin_instances import crinstance_student
from devilry.devilry_group.views import feedbackfeed_download_files
from devilry.devilry_group.views import feedbackfeed_filedownload_new

urlpatterns = [
    url(r'^student/', include(crinstance_student.StudentCrInstance.urls())),
    url(r'^examiner/', include(crinstance_examiner.ExaminerCrInstance.urls())),
    url(r'^admin/', include(crinstance_admin.AdminCrInstance.urls())),

    url(r'devilry-feedbackfeed-file-download/(?P<feedbackset_id>[0-9]+)/(?P<commentfile_id>[0-9]+)',
        feedbackfeed_download_files.FileDownloadFeedbackfeedView.as_view(),
        name='devilry-feedbackfeed-file-download'),

    url(r'devilry-feedbackfeed-compressed-all-feedbacksets-file-download/(?P<assignmentgroup_id>[0-9]+)',
        feedbackfeed_download_files.CompressedAllFeedbackSetsFileDownloadView.as_view(),
        name='devilry-feedbackfeed-compressed-all-feedbacksets-file-download'),

    url(r'devilry-feedbackfeed-compressed-feedback-file-download/(?P<feedbackset_id>[0-9]+)',
        feedbackfeed_download_files.CompressedFeedbackSetFileDownloadView.as_view(),
        name='devilry-feedbackfeed-compressed-feedbackset-file-download'),

    url(r'devilry-feedbackfeed-download',
        feedbackfeed_filedownload_new.FeedbackfeedFileDownload.as_view(),
        name='devilry-feedbackfeed-download')
]
