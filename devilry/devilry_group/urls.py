from django.conf.urls import patterns, url, include

from devilry.devilry_group.cradmin_instances import crinstance_student
from devilry.devilry_group.cradmin_instances import crinstance_examiner
from devilry.devilry_group.cradmin_instances import crinstance_subjectadmin
from devilry.devilry_group.cradmin_instances import crinstance_nodeadmin
from devilry.devilry_group.views import feedbackfeed_download_files

urlpatterns = patterns(
    'devilry.devilry_group',
    url(r'^student/', include(crinstance_student.StudentCrInstance.urls())),
    url(r'^examiner/', include(crinstance_examiner.ExaminerCrInstance.urls())),
    url(r'^nodeadmin/', include(crinstance_nodeadmin.NodeAdminCrInstance.urls())),
    url(r'^subjectadmin/', include(crinstance_subjectadmin.SubjectAdminCrInstance.urls())),

    url(r'devilry-feedbackfeed-file-download/(?P<feedbackset_id>[0-9]+)/(?P<commentfile_id>[0-9]+)',
        feedbackfeed_download_files.FileDownloadFeedbackfeedView.as_view(),
        name='devilry-feedbackfeed-file-download'),

    url(r'devilry-feedbackfeed-compressed-file-download/(?P<feedbackset_id>[0-9]+)',
        feedbackfeed_download_files.CompressedFileDownloadView.as_view(),
        name='devilry-feedbackfeed-compressed-file-download'),
)