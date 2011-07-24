from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from restful import student_restful
from views import (MainView, AddDeliveryView, FileUploadView)

urlpatterns = patterns('devilry.apps.student',
                       url(r'^$', login_required(MainView.as_view()), name='student'),
                       url(r'^add-delivery/(?P<deliveryid>\d+)$', 
                           login_required(AddDeliveryView.as_view()), 
                           name='add-delivery'),
                       url(r'^add-delivery/fileupload/(?P<deadlineid>\d+)$',
                           login_required(FileUploadView.as_view()),
                           name='file-upload'),
                       )

urlpatterns += student_restful
