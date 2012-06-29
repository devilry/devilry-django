from django.conf.urls.defaults import patterns, url

from .group import RestGroupRoot
#from .relateduser import RestRelatedStudent
#from .relateduser import RestRelatedExaminer
from .createnewassignment import RestCreateNewAssignment
from .subject import ListOrCreateSubjectRest
from .subject import InstanceSubjectRest
from .period import InstancePeriodRest
from .period import ListOrCreatePeriodRest
from .assignment import InstanceAssignmentRest
from .assignment import ListOrCreateAssignmentRest
from .relateduser import ListOrCreateRelatedExaminerRest
from .relateduser import InstanceRelatedExaminerRest


urlpatterns = patterns('devilry_subjectadmin.rest',
                       url(r'^group/(?P<id>[^/]+)/$', RestGroupRoot.as_view()),
                       url(r'^createnewassignment/$', RestCreateNewAssignment.as_view()),
                       url(r'^subject/$', ListOrCreateSubjectRest.as_view()),
                       url(r'^subject/(?P<id>[^/]+)$', InstanceSubjectRest.as_view()),
                       url(r'^period/$', ListOrCreatePeriodRest.as_view()),
                       url(r'^period/(?P<id>[^/]+)$', InstancePeriodRest.as_view()),
                       url(r'^relatedexaminer/$', ListOrCreateRelatedExaminerRest.as_view()),
                       url(r'^relatedexaminer/(?P<id>[^/]+)/$', InstanceRelatedExaminerRest.as_view()),
                       url(r'^assignment/$', ListOrCreateAssignmentRest.as_view()),
                       url(r'^assignment/(?P<id>[^/]+)$', InstanceAssignmentRest.as_view()),
                       #RestRelatedStudent.create_url("relatedstudent", "restrelatedstudent-api", "1.0"),
                       #RestRelatedExaminer.create_url("relatedexaminer", "restrelatedexaminer-api", "1.0"),
                       #RestCreateNewAssignment.create_url("createnewassignment", "restgroup-api", "1.0"),
                      )
