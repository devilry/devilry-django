from datetime import timedelta, datetime

import htmls
from django import test
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core.models import Assignment, AssignmentGroup
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories


class TestFullyAnonymousSubjectAdminItemValue(test.TestCase):
    def test_non_anonymous_not_allowed(self):
        testgroup = mommy.make('core.AssignmentGroup')
        with self.assertRaisesMessage(ValueError,
                                      'Can only use FullyAnonymousSubjectAdminItemValue for fully '
                                      'anonymous assignments.'):
            devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminItemValue(
                value=testgroup,
                assignment=testgroup.assignment)

    def test_semi_anonymous_is_not_allowed(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        with self.assertRaisesMessage(ValueError,
                                      'Can only use FullyAnonymousSubjectAdminItemValue for fully '
                                      'anonymous assignments.'):
            devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminItemValue(
                value=testgroup,
                assignment=testgroup.assignment)

    def test_name_fully_anonymous_is_not_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)


class TestStudentItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __render_studentitemvalue(self, group, **kwargs):
        assignment = Assignment.objects.prefetch_point_to_grade_map()\
            .get(id=group.parentnode_id)
        return htmls.S(devilry_listbuilder.assignmentgroup.StudentItemValue(
            value=group,
            assignment_id_to_assignment_map={assignment.id: assignment},
            **kwargs).render())

    def test_title_default(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode__parentnode__short_name='testsubject',
                               parentnode__parentnode__short_name='testperiod',
                               parentnode__long_name='Test Assignment')
        mommy.make('core.Candidate',
                   assignment_group=testgroup)
        selector = self.__render_studentitemvalue(group=testgroup)
        self.assertEqual(
            'testsubject.testperiod - Test Assignment',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_include_periodpath_false(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__long_name='Test Assignment')
        mommy.make('core.Candidate',
                   assignment_group=testgroup)
        selector = self.__render_studentitemvalue(group=testgroup, include_periodpath=False)
        self.assertEqual(
            'Test Assignment',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_examiners_not_included(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = self.__render_studentitemvalue(group=testgroup)
        self.assertFalse(
            selector.exists('.devilry-cradmin-groupitemvalue-examiners-names'))

    def test_grade_students_can_see_points_false(self):
        testgroup = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1).group
        selector = self.__render_studentitemvalue(group=testgroup)
        self.assertEqual(
            'Grade: passed',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        testgroup = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1).group
        selector = self.__render_studentitemvalue(group=testgroup)
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_deadline_first_attempt(self):
        testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=datetime(2000, 1, 15, 12, 0)))
        with self.settings(DATETIME_FORMAT='Y-m-d H:i', USE_L10N=False):
            selector = self.__render_studentitemvalue(group=testgroup)
        self.assertEqual(
            '2000-01-15 12:00',
            selector.one(
                    '.devilry-cradmin-groupitemvalue-deadline__datetime').alltext_normalized)

    def test_deadline_new_attempt(self):
        testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=datetime(2000, 1, 15, 12, 0)))
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=datetime(2200, 1, 2, 12, 30))
        with self.settings(DATETIME_FORMAT='Y-m-d H:i', USE_L10N=False):
            selector = self.__render_studentitemvalue(group=testgroup)
        self.assertEqual(
            '2200-01-02 12:30',
            selector.one(
                    '.devilry-cradmin-groupitemvalue-deadline__datetime').alltext_normalized)

    def test_attempt_number_first_attempt(self):
        testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start'))
        selector = self.__render_studentitemvalue(group=testgroup)
        self.assertFalse(
            selector.exists(
                    '.devilry-cradmin-groupitemvalue-deadline__attemptnumber'))

    def test_attempt_number_new_attempt1(self):
        testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start'))
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup)
        selector = self.__render_studentitemvalue(group=testgroup)
        self.assertEqual(
            '(second attempt)',
            selector.one(
                    '.devilry-cradmin-groupitemvalue-deadline__attemptnumber').alltext_normalized)

    def test_attempt_number_new_attempt2(self):
        testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start'))
        devilry_group_mommy_factories.feedbackset_new_attempt_published(
            group=testgroup)
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup)
        selector = self.__render_studentitemvalue(group=testgroup)
        self.assertEqual(
            '(third attempt)',
            selector.one(
                    '.devilry-cradmin-groupitemvalue-deadline__attemptnumber').alltext_normalized)


class TestExaminerItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_name(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_semi_anonymous_is_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'MyAnonymousID',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_fully_anonymous_is_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'MyAnonymousID',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_examiners_include_examiners_false(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment, include_examiners=False).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-examiners-names'))
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-examiners'))

    def test_examiners_include_examiners_true(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment, include_examiners=True).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_semi_anonymous_include_examiners_true(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment, include_examiners=True).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_fully_anonymous_include_examiners_true(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment, include_examiners=True).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_has_unpublished_feedbackdraft_draft_false(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-unpublished-feedbackdraft'))

    def test_has_unpublished_feedbackdraft_draft_true(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Unpublished feedback draft: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-unpublished-feedbackdraft').alltext_normalized)

    def test_grade_students_can_see_points_false(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group__parentnode__students_can_see_points=False,
                                                 grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group__parentnode__students_can_see_points=True,
                                                 grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)


class TestPeriodAdminItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_name(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_anonymous_not_allowed(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        with self.assertRaisesRegexp(ValueError, '^.*for anonymous assignments.*$'):
            devilry_listbuilder.assignmentgroup.PeriodAdminItemValue(value=testgroup, assignment=testgroup.assignment)

    def test_examiners(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_grade_students_can_see_points_false(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group__parentnode__students_can_see_points=False,
                                                 grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group__parentnode__students_can_see_points=True,
                                                 grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)


class TestSubjectAdminItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_name(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_semi_anonymous_is_not_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_fully_anonymous_is_not_allowed(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaisesRegexp(ValueError, '^.*for fully anonymous assignments.*$'):
            devilry_listbuilder.assignmentgroup.SubjectAdminItemValue(value=testgroup, assignment=testgroup.assignment)

    def test_examiners(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_grade_students_can_see_points_false(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group__parentnode__students_can_see_points=False,
                                                 grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group__parentnode__students_can_see_points=True,
                                                 grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)


class TestDepartmentAdminItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_name(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_semi_anonymous_is_not_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_fully_anonymous_is_not_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_examiners(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_fully_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_grade_students_can_see_points_false(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group__parentnode__students_can_see_points=False,
                                                 grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group__parentnode__students_can_see_points=True,
                                                 grading_points=1)\
            .group
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)


class MockNoMultiselectItemValue(devilry_listbuilder.assignmentgroup.ItemValueMixin,
                                 devilry_listbuilder.assignmentgroup.NoMultiselectItemValue):
    def get_devilryrole(self):
        return 'student'  # Should not affect any of the tests that uses this class


class TestItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_status_is_corrected(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(grading_points=1)\
            .group
        selector = htmls.S(MockNoMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-status'))

    def test_status_is_waiting_for_feedback(self):
        testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                         first_deadline=timezone.now() - timedelta(days=2)))
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup)
        testgroup.refresh_from_db()
        selector = htmls.S(MockNoMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for feedback',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_status_is_waiting_for_deliveries(self):
        testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                         first_deadline=timezone.now() + timedelta(days=2)))
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup)
        testgroup.refresh_from_db()
        selector = htmls.S(MockNoMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for deliveries',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_not_available_unless_corrected(self):
        testgroup = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished().group
        selector = htmls.S(MockNoMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_comment_summary_is_available(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testgroup.refresh_from_db()
        selector = htmls.S(MockNoMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertTrue(selector.exists('.devilry-cradmin-groupitemvalue-comments'))
        self.assertEqual(
            '0 comments from student. 0 files from student. 0 comments from examiner.',
            selector.one('.devilry-cradmin-groupitemvalue-comments').alltext_normalized)


class TestFullyAnonymousSubjectAdminMultiselectItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_non_anonymous_not_allowed(self):
        testgroup = mommy.make('core.AssignmentGroup')
        with self.assertRaisesMessage(ValueError,
                                      'Can only use FullyAnonymousSubjectAdminMultiselectItemValue for fully '
                                      'anonymous assignments.'):
            devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminMultiselectItemValue(
                value=testgroup,
                assignment=testgroup.assignment)

    def test_semi_anonymous_is_not_allowed(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        with self.assertRaisesMessage(ValueError,
                                      'Can only use FullyAnonymousSubjectAdminMultiselectItemValue for fully '
                                      'anonymous assignments.'):
            devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminMultiselectItemValue(
                value=testgroup,
                assignment=testgroup.assignment)

    def test_name_fully_anonymous_is_not_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_arialabels_fully_anonymous_is_not_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Select "Test User"',
            selector.one('.django-cradmin-multiselect2-itemvalue-button')['aria-label'])
        self.assertEqual(
            'Deselect "Test User"',
            selector.one('.django-cradmin-multiselect2-target-selected-item-deselectbutton')['aria-label'])

    def test_selected_item_title(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)


class TestExaminerMultiselectItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_name(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_semi_anonymous_is_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'MyAnonymousID',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_fully_anonymous_is_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'MyAnonymousID',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_selected_item_title_not_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_selected_item_title_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'MyAnonymousID',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_selected_item_title_fully_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'MyAnonymousID',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_arialabels_not_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Select "Test User"',
            selector.one('.django-cradmin-multiselect2-itemvalue-button')['aria-label'])
        self.assertEqual(
            'Deselect "Test User"',
            selector.one('.django-cradmin-multiselect2-target-selected-item-deselectbutton')['aria-label'])

    def test_arialabels_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Select "MyAnonymousID"',
            selector.one('.django-cradmin-multiselect2-itemvalue-button')['aria-label'])
        self.assertEqual(
            'Deselect "MyAnonymousID"',
            selector.one('.django-cradmin-multiselect2-target-selected-item-deselectbutton')['aria-label'])

    def test_arialabels_fully_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Select "MyAnonymousID"',
            selector.one('.django-cradmin-multiselect2-itemvalue-button')['aria-label'])
        self.assertEqual(
            'Deselect "MyAnonymousID"',
            selector.one('.django-cradmin-multiselect2-target-selected-item-deselectbutton')['aria-label'])

    def test_examiners_include_examiners_false(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment, include_examiners=False).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-examiners-names'))
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-examiners'))

    def test_examiners_include_examiners_true(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment, include_examiners=True).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_semi_anonymous_include_examiners_true(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment, include_examiners=True).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_fully_anonymous_include_examiners_true(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment, include_examiners=True).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_has_unpublished_feedbackdraft_draft_false(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(grading_points=1)\
            .group
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-unpublished-feedbackdraft'))

    def test_has_unpublished_feedbackdraft_draft_true(self):
        testgroup = devilry_group_mommy_factories\
                        .feedbackset_first_attempt_unpublished(grading_points=1)\
                        .group
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Unpublished feedback draft: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-unpublished-feedbackdraft').alltext_normalized)

    def __get_both_grades(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-cradmin-groupitemvalue-grade')]

    def test_grade_students_can_see_points_false(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_see_points=False)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=1)
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))

    def test_grade_students_can_see_points_true(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_see_points=False)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=1)
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))


class TestPeriodAdminMultiselectItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_anonymous_not_allowed(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        with self.assertRaisesRegexp(ValueError, '^.*for anonymous assignments.*$'):
            devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue(
                    value=testgroup, assignment=testgroup.assignment)

    def test_name(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_selected_item_title(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_arialabels(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Select "Test User"',
            selector.one('.django-cradmin-multiselect2-itemvalue-button')['aria-label'])
        self.assertEqual(
            'Deselect "Test User"',
            selector.one('.django-cradmin-multiselect2-target-selected-item-deselectbutton')['aria-label'])

    def test_examiners(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def __get_both_grades(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-cradmin-groupitemvalue-grade')]

    def test_grade_students_can_see_points_false(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_see_points=False)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=1)
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))

    def test_grade_students_can_see_points_true(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_see_points=True)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=1)
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))


class TestSubjectAdminMultiselectItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_fully_anonymous_is_not_allowed(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaisesRegexp(ValueError, '^.*for fully anonymous assignments.*$'):
            devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(value=testgroup, assignment=testgroup.assignment)

    def test_name(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_semi_anonymous_is_not_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_selected_item_title(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_selected_item_title_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_arialabels(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Select "Test User"',
            selector.one('.django-cradmin-multiselect2-itemvalue-button')['aria-label'])
        self.assertEqual(
            'Deselect "Test User"',
            selector.one('.django-cradmin-multiselect2-target-selected-item-deselectbutton')['aria-label'])

    def test_arialabels_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Select "Test User"',
            selector.one('.django-cradmin-multiselect2-itemvalue-button')['aria-label'])
        self.assertEqual(
            'Deselect "Test User"',
            selector.one('.django-cradmin-multiselect2-target-selected-item-deselectbutton')['aria-label'])

    def test_examiners(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def __get_both_grades(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-cradmin-groupitemvalue-grade')]

    def test_grade_students_can_see_points_false(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_see_points=False)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=1)
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))

    def test_grade_students_can_see_points_true(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_see_points=True)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=1)
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))


class TestDepartmentAdminMultiselectItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_name(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_semi_anonymous_is_not_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_fully_anonymous_is_not_anonymized(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_selected_item_title(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_selected_item_title_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_selected_item_title_fully_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup,
            assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_examiners(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_fully_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def __get_both_grades(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-cradmin-groupitemvalue-grade')]

    def test_grade_students_can_see_points_false(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_see_points=False)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=1)
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))

    def test_grade_students_can_see_points_true(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_see_points=True)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=1)
        testgroup.refresh_from_db()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))


class MockMultiselectItemValue(devilry_listbuilder.assignmentgroup.ItemValueMixin,
                               devilry_listbuilder.assignmentgroup.NoMultiselectItemValue):
    def get_devilryrole(self):
        return 'student'  # Should not affect any of the tests that uses this class


class TestMultiselectItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_status_is_corrected(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(grading_points=1)\
            .group
        testgroup.refresh_from_db()
        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-status'))

    def test_status_is_waiting_for_feedback(self):
        testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup)
        testgroup.refresh_from_db()
        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for feedback',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_status_is_waiting_for_deliveries(self):
        testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                         first_deadline=timezone.now() + timedelta(days=2)))
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup)
        testgroup.refresh_from_db()
        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for deliveries',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_not_available_unless_corrected(self):
        testgroup = devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished()\
            .group
        testgroup.refresh_from_db()
        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_comment_summary_is_available(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        testgroup = mommy.make('core.AssignmentGroup')
        testgroup.refresh_from_db()
        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertTrue(selector.exists('.devilry-cradmin-groupitemvalue-comments'))
        self.assertEqual(
            '0 comments from student. 0 files from student. 0 comments from examiner.',
            selector.one('.devilry-cradmin-groupitemvalue-comments').alltext_normalized)
