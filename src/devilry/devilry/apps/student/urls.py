from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from .restful import student_restful
from .views import FileDownloadView
from .views import CompressedFileDownloadView



urlpatterns = patterns('devilry.apps.student',
                       #url(r'^show-delivery/(?P<deliveryid>\d+)$',
                           #login_required(ShowDeliveryView.as_view()),
                           #name='show-delivery'),
                       url(r'^show-delivery/filedownload/(?P<filemetaid>\d+)$',
                           login_required(FileDownloadView.as_view()),
                           name='devilry-delivery-file-download'),
                       url(r'^show-delivery/compressedfiledownload/(?P<deliveryid>\d+)$',
                           login_required(CompressedFileDownloadView.as_view()),
                           name='devilry-delivery-download-all-zip')
                       )

urlpatterns += student_restful
