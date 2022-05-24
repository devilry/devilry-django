from datetime import timedelta

from django import test
from django.conf import settings
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_examiner.views.selfassign import selfassign


class TestSelfassignGrouplistView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = selfassign.SelfAssignGroupListView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __make_assignment_selfassign_enabled(self, **assignment_kwargs):
        return baker.make('core.Assignment', examiners_can_self_assign=True, **assignment_kwargs)

    def __make_group(self, student_user=None, num_other_examiners=0, **assignmentgroup_kwargs):
        group = baker.make('core.AssignmentGroup', **assignmentgroup_kwargs)

        # Add student to group.
        if not student_user:
            student_user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=group.parentnode.parentnode, user=student_user)
        baker.make('core.Candidate', assignment_group=group, relatedstudent=relatedstudent)

        # Add examiner to group.
        for num in range(num_other_examiners):
            baker.make(
                'core.Examiner',
                assignmentgroup=group, relatedexaminer=baker.make('core.RelatedExaminer', period=group.parentnode.parentnode))

        return group

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod)
        self.__make_group(parentnode=testassignment)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertIn(
            'The Semester - self-assign',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod)
        self.__make_group(parentnode=testassignment)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertIn(
            'The Semester - self-assign',
            mockresponse.selector.one('h1').alltext_normalized)
    
    def test_no_groups_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        self.__make_assignment_selfassign_enabled(parentnode=testperiod)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            0
        )

    def test_ordering_by_deadline_in_future_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment1 = self.__make_assignment_selfassign_enabled(
            parentnode=testperiod, first_deadline=timezone.now() + timedelta(days=16))
        testassignment2 = self.__make_assignment_selfassign_enabled(
            parentnode=testperiod, first_deadline=timezone.now() + timedelta(days=5))
        testassignment3 = self.__make_assignment_selfassign_enabled(
            parentnode=testperiod, first_deadline=timezone.now() + timedelta(days=10))

        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, shortname='student1@example.com'),
            parentnode=testassignment1)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, shortname='student2@example.com'),
            parentnode=testassignment2)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, shortname='student3@example.com'),
            parentnode=testassignment3)

        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 3)
        self.assertIn('student2@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn('student3@example.com', group_itemvalue_list[1].alltext_normalized)
        self.assertIn('student1@example.com', group_itemvalue_list[2].alltext_normalized)
    
    def test_ordering_by_deadline_in_past_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment1 = self.__make_assignment_selfassign_enabled(
            parentnode=testperiod, first_deadline=timezone.now() - timedelta(days=16))
        testassignment2 = self.__make_assignment_selfassign_enabled(
            parentnode=testperiod, first_deadline=timezone.now() - timedelta(days=5))
        testassignment3 = self.__make_assignment_selfassign_enabled(
            parentnode=testperiod, first_deadline=timezone.now() - timedelta(days=10))

        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, shortname='student1@example.com'),
            parentnode=testassignment1)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, shortname='student2@example.com'),
            parentnode=testassignment2)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, shortname='student3@example.com'),
            parentnode=testassignment3)

        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 3)
        self.assertIn('student1@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn('student3@example.com', group_itemvalue_list[1].alltext_normalized)
        self.assertIn('student2@example.com', group_itemvalue_list[2].alltext_normalized)

    def test_selfassign_limit_one_group_available(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, fullname='Student User', shortname='student@example.com'),
            parentnode=testassignment)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            1
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')
        self.assertEqual(len(group_itemvalue_list), 1)
        self.assertIn('student@example.com', group_itemvalue_list[0].alltext_normalized)

    def test_selfassign_limit_one_group_unavailable_has_other_examiner(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod)
        self.__make_group(num_other_examiners=1, parentnode=testassignment)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            0
        )

    def test_selfassign_limit_one_group_available_user_is_examiner(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod)
        testgroup = self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, fullname='Student User', shortname='student@example.com'),
            parentnode=testassignment)
        relatedexaminer = baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        baker.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            1
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')
        self.assertEqual(len(group_itemvalue_list), 1)
        self.assertIn('student@example.com', group_itemvalue_list[0].alltext_normalized)

    def test_selfassign_limit_two_group_available_no_examiners_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod, examiner_self_assign_limit=2)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, fullname='Student User', shortname='student@example.com'),
            parentnode=testassignment)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            1
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')
        self.assertEqual(len(group_itemvalue_list), 1)
        self.assertIn('student@example.com', group_itemvalue_list[0].alltext_normalized)

    def test_selfassign_limit_two_group_available_one_examiner_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod, examiner_self_assign_limit=2)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, fullname='Student User', shortname='student@example.com'),
            num_other_examiners=1,
            parentnode=testassignment)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            1
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')
        self.assertEqual(len(group_itemvalue_list), 1)
        self.assertIn('student@example.com', group_itemvalue_list[0].alltext_normalized)

    def test_selfassign_limit_two_group_unavailable_two_examiners_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod, examiner_self_assign_limit=2)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, fullname='Student User', shortname='student@example.com'),
            num_other_examiners=2,
            parentnode=testassignment)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            0
        )

    def test_selfassign_limit_two_group_available_two_examiners_user_is_examiner_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod, examiner_self_assign_limit=2)
        testgroup = self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL, fullname='Student User', shortname='student@example.com'),
            num_other_examiners=1,
            parentnode=testassignment)
        relatedexaminer = baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        baker.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            1
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')
        self.assertEqual(len(group_itemvalue_list), 1)
        self.assertIn('student@example.com', group_itemvalue_list[0].alltext_normalized)
    
    def test_multiple_groups_available_single_assignment_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment = self.__make_assignment_selfassign_enabled(parentnode=testperiod, long_name='Assignment')
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL,
                fullname='Student User1', shortname='student1@example.com'),
            parentnode=testassignment)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL,
                fullname='Student User2', shortname='student2@example.com'),
            parentnode=testassignment)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            2
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')
        self.assertEqual(len(group_itemvalue_list), 2)
        self.assertIn('Assignment', group_itemvalue_list[0].alltext_normalized)
        self.assertIn('student1@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn('Assignment', group_itemvalue_list[1].alltext_normalized)
        self.assertIn('student2@example.com', group_itemvalue_list[1].alltext_normalized)

    def test_multiple_groups_available_multiple_assignments_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        testassignment1 = self.__make_assignment_selfassign_enabled(parentnode=testperiod, long_name='Assignment 1')
        testassignment2 = self.__make_assignment_selfassign_enabled(parentnode=testperiod, long_name='Assignment 2')
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL,
                fullname='Student Assignment1', shortname='studentassignment1@example.com'),
            parentnode=testassignment1)
        self.__make_group(
            student_user=baker.make(settings.AUTH_USER_MODEL,
                fullname='Student Assignment2', shortname='studentassignment2@example.com'),
            parentnode=testassignment2)
        baker.make('core.RelatedExaminer', period=testperiod, user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'),
            2
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')
        self.assertEqual(len(group_itemvalue_list), 2)
        self.assertIn('Assignment 1', group_itemvalue_list[0].alltext_normalized)
        self.assertIn('studentassignment1@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn('Assignment 2', group_itemvalue_list[1].alltext_normalized)
        self.assertIn('studentassignment2@example.com', group_itemvalue_list[1].alltext_normalized)


class TestSelfassignGrouplistViewFilters(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = selfassign.SelfAssignGroupListView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.period = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        self.examiner_user = baker.make(settings.AUTH_USER_MODEL)
        self.related_examiner = baker.make('core.RelatedExaminer', period=self.period, user=self.examiner_user)

    def __make_group_with_student(self, assignment, fullname, shortname):
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        relatedstudent = baker.make(
            'core.RelatedStudent',
            period=assignment.parentnode,
            user=baker.make(settings.AUTH_USER_MODEL, fullname=fullname, shortname=shortname)
        )
        baker.make('core.Candidate', assignment_group=group, relatedstudent=relatedstudent)
        return group

    def __make_assignment(self, long_name, short_name):
        return baker.make(
            'core.Assignment',
            examiners_can_self_assign=True, parentnode=self.period,
            long_name=long_name, short_name=short_name)

    def __make_single_assignment_with_multiple_groups(self):
        assignment = self.__make_assignment(long_name='Assignment', short_name='assignment')
        self.__make_group_with_student(assignment, 'Student1', 'student1@example.com')
        self.__make_group_with_student(assignment, 'Student2', 'student2@example.com')
        self.__make_group_with_student(assignment, 'Student3', 'student3@example.com')
        return assignment

    def __make_multiple_assignments_with_single_group(self):
        assignment1 = self.__make_assignment(long_name='Assignment 1', short_name='assignment1')
        self.__make_group_with_student(assignment1, 'Assignment1 Student', 'assignment1student@example.com')
        assignment2 = self.__make_assignment(long_name='Assignment 2', short_name='assignment2')
        self.__make_group_with_student(assignment2, 'Assignment2 Student', 'assignment2student@example.com')
        assignment3 = self.__make_assignment(long_name='Assignment 3', short_name='assignment3')
        self.__make_group_with_student(assignment3, 'Assignment3 Student', 'assignment3student@example.com')
        return assignment1, assignment2, assignment3

    def __make_multiple_assignments_with_multiple_groups(self):
        assignment1 = self.__make_assignment(long_name='Assignment 1', short_name='assignment1')
        self.__make_group_with_student(assignment1, 'Assignment1 Student1', 'assignment1student1@example.com')
        self.__make_group_with_student(assignment1, 'Assignment1 Student2', 'assignment1student2@example.com')
        self.__make_group_with_student(assignment1, 'Assignment1 Student3', 'assignment1student3@example.com')
        assignment2 = self.__make_assignment(long_name='Assignment 2', short_name='assignment2')
        self.__make_group_with_student(assignment2, 'Assignment2 Student1', 'assignment2student1@example.com')
        self.__make_group_with_student(assignment2, 'Assignment2 Student2', 'assignment2student2@example.com')
        self.__make_group_with_student(assignment2, 'Assignment2 Student3', 'assignment2student3@example.com')
        assignment3 = self.__make_assignment(long_name='Assignment 3', short_name='assignment3')
        self.__make_group_with_student(assignment3, 'Assignment3 Student1', 'assignment3student1@example.com')
        self.__make_group_with_student(assignment3, 'Assignment3 Student2', 'assignment3student2@example.com')
        self.__make_group_with_student(assignment3, 'Assignment3 Student3', 'assignment3student3@example.com')
        return assignment1, assignment2, assignment3
    
    def test_assignment_filter_label_sanity(self):
        self.__make_single_assignment_with_multiple_groups()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user
        )
        self.assertEqual(
            mockresponse.selector.one('#cradmin_legacy_listfilter_assignmentname_label').alltext_normalized,
            'Assignments'
        )        

    def test_assignment_filter_name_single_assignment_sanity(self):
        assignment = self.__make_single_assignment_with_multiple_groups()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user
        )
        self.assertEqual(
            mockresponse.selector.one(f'#cradmin_legacy_listfilter_assignmentname_input_{assignment.short_name}_label').alltext_normalized,
            'Assignment'
        )

    def test_assignment_filter_name_multiple_assignments_sanity(self):
        assignment1, assignment2, assignment3 = self.__make_multiple_assignments_with_single_group()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user
        )
        self.assertEqual(
            mockresponse.selector.one(f'#cradmin_legacy_listfilter_assignmentname_input_{assignment1.short_name}_label').alltext_normalized,
            'Assignment 1'
        )
        self.assertEqual(
            mockresponse.selector.one(f'#cradmin_legacy_listfilter_assignmentname_input_{assignment2.short_name}_label').alltext_normalized,
            'Assignment 2'
        )
        self.assertEqual(
            mockresponse.selector.one(f'#cradmin_legacy_listfilter_assignmentname_input_{assignment3.short_name}_label').alltext_normalized,
            'Assignment 3'
        )

    def test_filter_no_filter_sanity(self):
        assignment = self.__make_single_assignment_with_multiple_groups()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': ''}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 3)
        self.assertIn(assignment.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('student1@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn(assignment.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertIn('student2@example.com', group_itemvalue_list[1].alltext_normalized)
        self.assertIn(assignment.long_name, group_itemvalue_list[2].alltext_normalized)
        self.assertIn('student3@example.com', group_itemvalue_list[2].alltext_normalized)
    
    def test_assignment_filter_sanity(self):
        assignment = self.__make_single_assignment_with_multiple_groups()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': f'assignmentname-{assignment.short_name}'}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 3)
        self.assertIn(assignment.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('student1@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn(assignment.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertIn('student2@example.com', group_itemvalue_list[1].alltext_normalized)
        self.assertIn(assignment.long_name, group_itemvalue_list[2].alltext_normalized)
        self.assertIn('student3@example.com', group_itemvalue_list[2].alltext_normalized)

    def test_assignment_filter_single_assignment_sanity(self):
        assignment1, assignment2, assignment3 = self.__make_multiple_assignments_with_single_group()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': f'assignmentname-{assignment1.short_name}'}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 1)
        self.assertIn(assignment1.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('assignment1student@example.com', group_itemvalue_list[0].alltext_normalized)

    def test_assignment_filter_multiple_assignments_sanity(self):
        assignment1, assignment2, assignment3 = self.__make_multiple_assignments_with_single_group()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': f'assignmentname-{assignment1.short_name}%2C{assignment2.short_name}'}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 2)
        self.assertIn(assignment1.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('assignment1student@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn(assignment2.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertIn('assignment2student@example.com', group_itemvalue_list[1].alltext_normalized)

    def test_assignment_filter_all_assignments_sanity(self):
        assignment1, assignment2, assignment3 = self.__make_multiple_assignments_with_single_group()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': f'assignmentname-{assignment1.short_name}%2C{assignment2.short_name}%2C{assignment3.short_name}'}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 3)
        self.assertIn(assignment1.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('assignment1student@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn(assignment2.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertIn('assignment2student@example.com', group_itemvalue_list[1].alltext_normalized)
        self.assertIn(assignment3.long_name, group_itemvalue_list[2].alltext_normalized)
        self.assertIn('assignment3student@example.com', group_itemvalue_list[2].alltext_normalized)

    def test_assignment_filter_single_assignment_multiple_groups_sanity(self):
        assignment1, assignment2, assignment3 = self.__make_multiple_assignments_with_multiple_groups()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': f'assignmentname-{assignment1.short_name}'}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 3)
        self.assertIn(assignment1.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('assignment1student1@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn(assignment1.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertIn('assignment1student2@example.com', group_itemvalue_list[1].alltext_normalized)
        self.assertIn(assignment1.long_name, group_itemvalue_list[2].alltext_normalized)
        self.assertIn('assignment1student3@example.com', group_itemvalue_list[2].alltext_normalized)

        self.assertNotIn(assignment2.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertNotIn(assignment2.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertNotIn(assignment2.long_name, group_itemvalue_list[2].alltext_normalized)
        self.assertNotIn(assignment3.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertNotIn(assignment3.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertNotIn(assignment3.long_name, group_itemvalue_list[2].alltext_normalized)

    def test_assignment_filter_multiple_assignment_multiple_groups_sanity(self):
        assignment1, assignment2, assignment3 = self.__make_multiple_assignments_with_multiple_groups()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': f'assignmentname-{assignment1.short_name}%2C{assignment3.short_name}'}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 6)
        self.assertIn(assignment1.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('assignment1student1@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn(assignment1.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertIn('assignment1student2@example.com', group_itemvalue_list[1].alltext_normalized)
        self.assertIn(assignment1.long_name, group_itemvalue_list[2].alltext_normalized)
        self.assertIn('assignment1student3@example.com', group_itemvalue_list[2].alltext_normalized)

        self.assertIn(assignment3.long_name, group_itemvalue_list[3].alltext_normalized)
        self.assertIn('assignment3student1@example.com', group_itemvalue_list[3].alltext_normalized)
        self.assertIn(assignment3.long_name, group_itemvalue_list[4].alltext_normalized)
        self.assertIn('assignment3student2@example.com', group_itemvalue_list[4].alltext_normalized)
        self.assertIn(assignment3.long_name, group_itemvalue_list[5].alltext_normalized)
        self.assertIn('assignment3student3@example.com', group_itemvalue_list[5].alltext_normalized)

        self.assertNotIn(assignment2.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertNotIn(assignment2.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertNotIn(assignment2.long_name, group_itemvalue_list[2].alltext_normalized)
        self.assertNotIn(assignment2.long_name, group_itemvalue_list[3].alltext_normalized)
        self.assertNotIn(assignment2.long_name, group_itemvalue_list[4].alltext_normalized)
        self.assertNotIn(assignment2.long_name, group_itemvalue_list[5].alltext_normalized)

    def test_assignstatus_filter_all_groups(self):
        assignment1, assignment2, assignment3 = self.__make_multiple_assignments_with_single_group()
        baker.make('core.Examiner', relatedexaminer=self.related_examiner, assignmentgroup=AssignmentGroup.objects.get(parentnode=assignment1))
        baker.make('core.Examiner', relatedexaminer=self.related_examiner, assignmentgroup=AssignmentGroup.objects.get(parentnode=assignment2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': ''}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 3)
        self.assertIn(assignment1.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('assignment1student@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn(assignment2.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertIn('assignment2student@example.com', group_itemvalue_list[1].alltext_normalized)
        self.assertIn(assignment3.long_name, group_itemvalue_list[2].alltext_normalized)
        self.assertIn('assignment3student@example.com', group_itemvalue_list[2].alltext_normalized)

    def test_assignstatus_filter_assigned_groups_only(self):
        assignment1, assignment2, assignment3 = self.__make_multiple_assignments_with_single_group()
        baker.make('core.Examiner', relatedexaminer=self.related_examiner, assignmentgroup=AssignmentGroup.objects.get(parentnode=assignment1))
        baker.make('core.Examiner', relatedexaminer=self.related_examiner, assignmentgroup=AssignmentGroup.objects.get(parentnode=assignment2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': 'assignedstatus-assigned'}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 2)
        self.assertIn(assignment1.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('assignment1student@example.com', group_itemvalue_list[0].alltext_normalized)
        self.assertIn(assignment2.long_name, group_itemvalue_list[1].alltext_normalized)
        self.assertIn('assignment2student@example.com', group_itemvalue_list[1].alltext_normalized)

    def test_assignstatus_filter_unassigned_groups_only(self):
        assignment1, assignment2, assignment3 = self.__make_multiple_assignments_with_single_group()
        baker.make('core.Examiner', relatedexaminer=self.related_examiner, assignmentgroup=AssignmentGroup.objects.get(parentnode=assignment1))
        baker.make('core.Examiner', relatedexaminer=self.related_examiner, assignmentgroup=AssignmentGroup.objects.get(parentnode=assignment2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=self.period,
            requestuser=self.examiner_user,
            viewkwargs={'filters_string': 'assignedstatus-unassigned'}
        )
        group_itemvalue_list = mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')
        self.assertEqual(len(group_itemvalue_list), 1)
        self.assertIn(assignment3.long_name, group_itemvalue_list[0].alltext_normalized)
        self.assertIn('assignment3student@example.com', group_itemvalue_list[0].alltext_normalized)
