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
from .relateduser import ListOrCreateRelatedStudentRest
from .relateduser import InstanceRelatedStudentRest


urlpatterns = patterns('devilry_subjectadmin.rest',
                       url(r'^group/(?P<id>[^/]+)/$', RestGroupRoot.as_view()),
                       url(r'^createnewassignment/$', RestCreateNewAssignment.as_view()),
                       url(r'^subject/$', ListOrCreateSubjectRest.as_view()),
                       url(r'^subject/(?P<id>[^/]+)$', InstanceSubjectRest.as_view()),
                       url(r'^period/$', ListOrCreatePeriodRest.as_view()),
                       url(r'^period/(?P<id>[^/]+)$', InstancePeriodRest.as_view()),
                       url(r'^relatedexaminer/(?P<period_id>\d+)/$', ListOrCreateRelatedExaminerRest.as_view()),
                       url(r'^relatedexaminer/(?P<period_id>\d+)/(?P<id>\d+)/$', InstanceRelatedExaminerRest.as_view()),
                       url(r'^relatedstudent/(?P<period_id>\d+)/$', ListOrCreateRelatedStudentRest.as_view()),
                       url(r'^relatedstudent/(?P<period_id>\d+)/(?P<id>\d+)/$', InstanceRelatedStudentRest.as_view()),
                       url(r'^assignment/$', ListOrCreateAssignmentRest.as_view()),
                       url(r'^assignment/(?P<id>[^/]+)$', InstanceAssignmentRest.as_view()),
                      )
