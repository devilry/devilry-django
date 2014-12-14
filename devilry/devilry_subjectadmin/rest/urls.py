from django.conf.urls import patterns, url

from .group import ListOrCreateGroupRest













#from .group import InstanceGroupRest
from devilry.devilry_subjectadmin.rest.createnewassignment import RestCreateNewAssignment
from devilry.devilry_subjectadmin.rest.subject import ListOrCreateSubjectRest
from devilry.devilry_subjectadmin.rest.subject import InstanceSubjectRest
from devilry.devilry_subjectadmin.rest.period import InstancePeriodRest
from devilry.devilry_subjectadmin.rest.period import ListOrCreatePeriodRest
from devilry.devilry_subjectadmin.rest.assignment import InstanceAssignmentRest
from devilry.devilry_subjectadmin.rest.assignment import ListOrCreateAssignmentRest
from devilry.devilry_subjectadmin.rest.relateduser import ListOrCreateRelatedExaminerRest
from devilry.devilry_subjectadmin.rest.relateduser import InstanceRelatedExaminerRest
from devilry.devilry_subjectadmin.rest.relateduser import ListOrCreateRelatedStudentRest
from devilry.devilry_subjectadmin.rest.relateduser import InstanceRelatedStudentRest
from devilry.devilry_subjectadmin.rest.relateduser_assignment_ro import ListRelatedStudentsOnAssignmentRest
from devilry.devilry_subjectadmin.rest.relateduser_assignment_ro import ListRelatedExaminersOnAssignmentRest
from devilry.devilry_subjectadmin.rest.allwhereisadmin import AllWhereIsAdmin
from devilry.devilry_subjectadmin.rest.deadlinesbulk import DeadlinesBulkListOrCreate
from devilry.devilry_subjectadmin.rest.deadlinesbulk import DeadlinesBulkUpdateReadOrDelete
from devilry.devilry_subjectadmin.rest.popfromgroup import PopFromGroup
from devilry.devilry_subjectadmin.rest.mergeintogroup import MergeIntoGroup
from devilry.devilry_subjectadmin.rest.aggregated_groupinfo import AggregatedGroupInfo
from devilry.devilry_subjectadmin.rest.passedinpreviousperiod import PassedInPreviousPeriod
from devilry.devilry_subjectadmin.rest.detailedperiodoverview import DetailedPeriodOverview
from devilry.devilry_subjectadmin.rest.examinerstats import ExaminerStats


urlpatterns = patterns('devilry.devilry_subjectadmin.rest',
                       url(r'^group/(?P<assignment_id>\d+)/$', ListOrCreateGroupRest.as_view()),
                       url(r'^createnewassignment/$', RestCreateNewAssignment.as_view()),
                       url(r'^subject/$', ListOrCreateSubjectRest.as_view()),
                       url(r'^subject/(?P<id>[^/]+)$', InstanceSubjectRest.as_view()),
                       url(r'^period/$',
                           ListOrCreatePeriodRest.as_view(),
                           name='devilry-subjectadmin-rest-period'),
                       url(r'^period/(?P<id>[^/]+)$',
                           InstancePeriodRest.as_view(),
                           name='devilry-subjectadmin-rest-period-instance'),
                       url(r'^detailedperiodoverview/(?P<id>[^/]+)$',
                           DetailedPeriodOverview.as_view(),
                           name='devilry-subjectadmin-rest-detailedperiodoverview'),
                       url(r'^relatedexaminer/(?P<period_id>\d+)/$',
                           ListOrCreateRelatedExaminerRest.as_view()),
                       url(r'^relatedexaminer/(?P<period_id>\d+)/(?P<id>\d+)$',
                           InstanceRelatedExaminerRest.as_view()),
                       url(r'^relatedstudent/(?P<period_id>\d+)/$',
                           ListOrCreateRelatedStudentRest.as_view()),
                       url(r'^relatedstudent/(?P<period_id>\d+)/(?P<id>\d+)$',
                           InstanceRelatedStudentRest.as_view()),
                       url(r'^assignment/$', ListOrCreateAssignmentRest.as_view()),
                       url(r'^assignment/(?P<id>[^/]+)$', InstanceAssignmentRest.as_view()),
                       url(r'^relatedstudent_assignment_ro/(?P<assignment_id>\d+)/$',
                           ListRelatedStudentsOnAssignmentRest.as_view()),
                       url(r'^relatedexaminer_assignment_ro/(?P<assignment_id>\d+)/$',
                           ListRelatedExaminersOnAssignmentRest.as_view()),
                       url(r'^allwhereisadmin/$', AllWhereIsAdmin.as_view()),
                       url(r'^aggregated-groupinfo/(?P<id>[^/]+)$', AggregatedGroupInfo.as_view()),
                       url(r'^examinerstats/(?P<id>[^/]+)$',
                           ExaminerStats.as_view(),
                           name='devilry-subjectadmin-rest-examinerstats'),
                       url(r'^popfromgroup/(?P<id>[^/]+)$', PopFromGroup.as_view()),
                       url(r'^mergeintogroup/(?P<id>[^/]+)$', MergeIntoGroup.as_view()),
                       url(r'^deadlinesbulk/(?P<id>[^/]+)/$', DeadlinesBulkListOrCreate.as_view()),
                       url(r'^deadlinesbulk/(?P<id>[^/]+)/(?P<bulkdeadline_id>\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2}--(?:.{40})?)$',
                           DeadlinesBulkUpdateReadOrDelete.as_view(),
                           name='devilry_subjectadmin_rest_deadlinesbulkinstance'),
                       url(r'^passedinpreviousperiod/(?P<id>[^/]+)$',
                           PassedInPreviousPeriod.as_view())
                      )
