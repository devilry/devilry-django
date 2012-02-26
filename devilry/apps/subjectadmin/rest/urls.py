from django.conf.urls.defaults import patterns

from group import RestGroup
from relateduser import RestRelatedStudent
from relateduser import RestRelatedExaminer
from createnewassignment import RestCreateNewAssignment

urlpatterns = patterns('devilry.apps.subjectadmin.rest',
                       RestRelatedStudent.create_url("relatedstudent", "restrelatedstudent-api", "1.0"),
                       RestRelatedExaminer.create_url("relatedexaminer", "restrelatedexaminer-api", "1.0"),
                       RestCreateNewAssignment.create_url("createnewassignment", "restgroup-api", "1.0"),
                       RestGroup.create_url("group", "restgroup-api", "1.0"))
