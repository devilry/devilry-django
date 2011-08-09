from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from restful import administrator_restful
from views import (MainView, RestfulSimplifiedView,
                   RestfulSimplifiedViewWithGradeEditors)

urlpatterns = patterns('devilry.apps.administrator',
                       url(r'^$',
                           login_required(MainView.as_view()),
                           name='administrator'),
                       RestfulSimplifiedView.as_url('node',
                                                    'administrator/node.django.html'),
                       RestfulSimplifiedView.as_url('subject',
                                                    'administrator/subject.django.html'),
                       RestfulSimplifiedView.as_url('period',
                                                    'administrator/period.django.html'),
                       RestfulSimplifiedViewWithGradeEditors.as_url('assignment',
                                                                    'administrator/assignment.django.html'),
                       RestfulSimplifiedViewWithGradeEditors.as_url('assignmentgroup',
                                                                    'administrator/assignmentgroupview.django.html')
                      )
urlpatterns += administrator_restful
