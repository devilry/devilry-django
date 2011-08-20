from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from restful import student_restful
from views import (MainView, AddDeliveryView, 
                   FileUploadView, AssignmentGroupView,
                   FileDownloadView, ShowDeliveryView,
                   CompressedFileDownloadView, TarFileDownloadView)

urlpatterns = patterns('devilry.apps.student',
                       url(r'^$', login_required(MainView.as_view()), name='student'),
                       url(r'^add-delivery/(?P<deadlineid>\d+)$', 
                           login_required(AddDeliveryView.as_view()), 
                           name='add-delivery'),
                       url(r'^add-delivery/fileupload/(?P<deadlineid>\d+)$',
                           login_required(FileUploadView.as_view()),
                           name='file-upload-id'),
                       url(r'^add-delivery/fileupload/(?P<deadlineid>\d+)$',
                           login_required(FileUploadView.as_view()),
                           name='file-upload'),
                       url(r'^assignmentgroup/(?P<assignmentgroupid>\d+)$',
                           login_required(AssignmentGroupView.as_view())),
                       url(r'^show-delivery/(?P<deliveryid>\d+)$',
                           login_required(ShowDeliveryView.as_view()),
                           name='show-delivery'),
                       url(r'^show-delivery/filedownload/(?P<filemetaid>\d+)$',
                           login_required(FileDownloadView.as_view()),
                           name='file-download'),
                       url(r'^show-delivery/compressedfiledownload/(?P<deliveryid>\d+)$',
                           login_required(CompressedFileDownloadView.as_view()),
                           name='compressed-file-download'),
                       url(r'^show-delivery/tarfiledownload/(?P<deliveryid>\d+)$',
                           login_required(TarFileDownloadView.as_view()),
                           name='tar-file-download'),
                       )

urlpatterns += student_restful
