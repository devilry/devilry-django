from django.conf.urls.defaults import patterns, url

from group import RestGroupRoot
from relateduser import RestRelatedStudent
from relateduser import RestRelatedExaminer
from createnewassignment import RestCreateNewAssignmentRoot

urlpatterns = patterns('devilry_subjectadmin.rest',
                       url(r'^group/(\w+)/$', RestGroupRoot.as_view()),
                       url(r'^createnewassignment/(\w+)/$', RestCreateNewAssignmentRoot.as_view()),
                       RestRelatedStudent.create_url("relatedstudent", "restrelatedstudent-api", "1.0"),
                       RestRelatedExaminer.create_url("relatedexaminer", "restrelatedexaminer-api", "1.0"),
                       #RestCreateNewAssignment.create_url("createnewassignment", "restgroup-api", "1.0"),
                      )
