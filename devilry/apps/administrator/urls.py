from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from restful import administrator_restful
from views import MainView, AssignmentGroupView
import editorviews

urlpatterns = patterns('devilry.apps.administrator',
                       url(r'^$',
                           login_required(MainView.as_view()),
                           name='administrator'),
                       editorviews.NodeEditor.create_url(),
                       editorviews.SubjectEditor.create_url(),
                       editorviews.PeriodEditor.create_url(),
                       editorviews.AssignmentEditor.create_url(),
                       url(r'^assignmentgroup/(?P<assignmentgroupid>\d+)$',
                           login_required(AssignmentGroupView.as_view()))
                      )
urlpatterns += administrator_restful
