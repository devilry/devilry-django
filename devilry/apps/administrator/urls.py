from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from restful import administrator_restful
from views import MainView, RestfulSimplifiedView
import editorviews

urlpatterns = patterns('devilry.apps.administrator',
                       url(r'^$',
                           login_required(MainView.as_view()),
                           name='administrator'),
                       editorviews.NodeEditor.create_url(),
                       editorviews.SubjectEditor.create_url(),
                       editorviews.PeriodEditor.create_url(),
                       editorviews.AssignmentEditor.create_url(),
                       RestfulSimplifiedView.as_url('assignmentgroup',
                                                    'administrator/assignmentgroupview.django.html'),
                       RestfulSimplifiedView.as_url('assignment',
                                                    'administrator/assignment.django.html'),
                      )
urlpatterns += administrator_restful
