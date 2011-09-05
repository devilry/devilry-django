from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from restful import examiner_restful
from views import (MainView, AssignmentGroupView, 
                    AssignmentView, CompressedFileDownloadView)

urlpatterns = patterns('devilry.apps.examiner',
                       url(r'^$', login_required(MainView.as_view()), name='examiner'),
                       url(r'^assignmentgroup/(?P<assignmentgroupid>\d+)$',
                           login_required(AssignmentGroupView.as_view()), name='examiner-agroup-view'),
                       url(r'^assignment/(?P<assignmentid>\d+)$',
                           login_required(AssignmentView.as_view()), name='examiner-assignment-view'),
                       url(r'^assignment/compressedfiledownload/(?P<assignmentid>\d+)$',
                           login_required(CompressedFileDownloadView.as_view()),
                           name='compressed-file-download')
                      )

urlpatterns += examiner_restful
