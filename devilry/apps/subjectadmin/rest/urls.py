from django.conf.urls.defaults import patterns, url

from group import RestGroup
from group import AltRestGroup, AltRestGroupRoot
from relateduser import RestRelatedStudent
from relateduser import RestRelatedExaminer
from createnewassignment import RestCreateNewAssignment

urlpatterns = patterns('devilry.apps.subjectadmin.rest',
                       url(r'^group/(\w+)$', AltRestGroupRoot.as_view()),
                       #url(r'^group/(\w+)/$', AltRestGroup.as_view()),
                       #RestGroup.create_url("group", "restgroup-api", "1.0")
                       RestRelatedStudent.create_url("relatedstudent", "restrelatedstudent-api", "1.0"),
                       RestRelatedExaminer.create_url("relatedexaminer", "restrelatedexaminer-api", "1.0"),
                       RestCreateNewAssignment.create_url("createnewassignment", "restgroup-api", "1.0"),
                      )
