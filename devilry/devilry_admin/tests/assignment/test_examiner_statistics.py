from django.test import TestCase

from model_bakery import baker
from cradmin_legacy import cradmin_testhelpers

from devilry.devilry_admin.views.assignment.statistics import statistics_overview
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestExaminerStatistics(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = statistics_overview.Overview

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_all_groups_have_examiner_sanity(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Candidate', relatedstudent__period=assignment.parentnode, assignment_group=group)
        baker.make('core.Examiner', relatedexaminer__period=assignment.parentnode, assignmentgroup=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertFalse(mockresponse.selector.exists('#id_examiner_statistics_no_examiners_assigned_to_groups'))
    
    def test_all_groups_missing_examiner_sanity(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Candidate', relatedstudent__period=assignment.parentnode, assignment_group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertTrue(mockresponse.selector.exists('#id_examiner_statistics_no_examiners_assigned_to_groups'))
        self.assertEqual(
            mockresponse.selector.one('#id_examiner_statistics_no_examiners_assigned_to_groups').alltext_normalized,
            'No data available. There are no examiners assigned to any groups.'
        )
    
    def test_single_examiner_on_group_warning_message_is_not_shown_sanity(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Candidate', relatedstudent__period=assignment.parentnode, assignment_group=group)
        baker.make('core.Examiner', relatedexaminer__period=assignment.parentnode, assignmentgroup=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertFalse(mockresponse.selector.exists('.alert-paragraph'))

    def test_multiple_examiners_on_group_warning_message_is_shown_sanity(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Candidate', relatedstudent__period=assignment.parentnode, assignment_group=group)
        baker.make('core.Examiner', relatedexaminer__period=assignment.parentnode, assignmentgroup=group)
        baker.make('core.Examiner', relatedexaminer__period=assignment.parentnode, assignmentgroup=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertTrue(mockresponse.selector.exists('.alert-paragraph'))
        self.assertEqual(
            mockresponse.selector.one('.alert-paragraph').alltext_normalized,
            'WARNING: This assignment has student groups with multiple examiners '
            'assigned to them. Multiple examiners are assumed to be collaborating '
            'on the grading, thus giving the same credit to all assigned examiners '
            'regardless of who added the grade or posted a feedback to the student group.')
