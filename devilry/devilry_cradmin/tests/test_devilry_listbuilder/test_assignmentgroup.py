from datetime import timedelta

import htmls
from django import test
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core.models import Assignment, AssignmentGroup
from devilry.devilry_cradmin import devilry_listbuilder
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
    def test_name(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.StudentItemValue(
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
        selector = htmls.S(devilry_listbuilder.assignmentgroup.StudentItemValue(
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
        selector = htmls.S(devilry_listbuilder.assignmentgroup.StudentItemValue(
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
        selector = htmls.S(devilry_listbuilder.assignmentgroup.StudentItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_semi_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.StudentItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'MyAnonymousID',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_fully_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(devilry_listbuilder.assignmentgroup.StudentItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'MyAnonymousID',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_grade_students_can_see_points_false(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.StudentItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.StudentItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)


class TestExaminerItemValue(test.TestCase):
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
        devilry_group_mommy_factories.feedbackset_first_try_published(grading_points=1),
        testgroup = AssignmentGroup.objects\
            .annotate_with_grading_points()\
            .annotate_with_has_unpublished_feedbackdraft().first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-unpublished-feedbackdraft'))

    def test_has_unpublished_feedbackdraft_draft_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(grading_points=1),
        testgroup = AssignmentGroup.objects\
            .annotate_with_grading_points()\
            .annotate_with_has_unpublished_feedbackdraft().first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Unpublished feedback draft: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-unpublished-feedbackdraft').alltext_normalized)

    def test_grade_students_can_see_points_false(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)


class TestPeriodAdminItemValue(test.TestCase):
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
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)


class TestSubjectAdminItemValue(test.TestCase):
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
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)


class TestDepartmentAdminItemValue(test.TestCase):
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
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
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
    def test_status_is_corrected(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            grading_points=1)
        testgroup = AssignmentGroup.objects.annotate_with_is_corrected().first()
        selector = htmls.S(MockNoMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-status'))

    def test_status_is_waiting_for_feedback(self):
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        testgroup = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback().first()
        selector = htmls.S(MockNoMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for feedback',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_status_is_waiting_for_deliveries(self):
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                first_deadline=timezone.now() + timedelta(days=2)))
        testgroup = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries().first()
        selector = htmls.S(MockNoMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for deliveries',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_not_available_unless_corrected(self):
        devilry_group_mommy_factories.feedbackset_first_try_unpublished()
        testgroup = AssignmentGroup.objects.annotate_with_is_corrected().first()
        selector = htmls.S(MockNoMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_comment_summary_is_available(self):
        mommy.make('core.AssignmentGroup')
        testgroup = AssignmentGroup.objects\
            .annotate_with_number_of_commentfiles_from_students()\
            .annotate_with_number_of_groupcomments_from_students()\
            .annotate_with_number_of_groupcomments_from_examiners()\
            .annotate_with_number_of_groupcomments_from_admins()\
            .first()

        selector = htmls.S(MockNoMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertTrue(selector.exists('.devilry-cradmin-groupitemvalue-comments'))
        self.assertEqual(
            '0 comments from student. 0 files from student. 0 comments from examiner.',
            selector.one('.devilry-cradmin-groupitemvalue-comments').alltext_normalized)


class TestFullyAnonymousSubjectAdminMultiselectItemValue(test.TestCase):
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
        devilry_group_mommy_factories.feedbackset_first_try_published(grading_points=1),
        testgroup = AssignmentGroup.objects\
            .annotate_with_grading_points()\
            .annotate_with_has_unpublished_feedbackdraft().first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-unpublished-feedbackdraft'))

    def test_has_unpublished_feedbackdraft_draft_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(grading_points=1),
        testgroup = AssignmentGroup.objects\
            .annotate_with_grading_points()\
            .annotate_with_has_unpublished_feedbackdraft().first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Unpublished feedback draft: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-unpublished-feedbackdraft').alltext_normalized)

    def __get_both_grades(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-cradmin-groupitemvalue-grade')]

    def test_grade_students_can_see_points_false(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))

    def test_grade_students_can_see_points_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))


class TestPeriodAdminMultiselectItemValue(test.TestCase):
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
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))

    def test_grade_students_can_see_points_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))


class TestSubjectAdminMultiselectItemValue(test.TestCase):
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
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))

    def test_grade_students_can_see_points_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))


class TestDepartmentAdminMultiselectItemValue(test.TestCase):
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
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
        selector = htmls.S(devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            ['Grade: passed (1/1)', 'Grade: passed (1/1)'],
            self.__get_both_grades(selector))

    def test_grade_students_can_see_points_true(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects\
            .annotate_with_is_corrected()\
            .annotate_with_grading_points()\
            .first()
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
    def test_status_is_corrected(self):
        devilry_group_mommy_factories.feedbackset_first_try_published(
            grading_points=1)
        testgroup = AssignmentGroup.objects.annotate_with_is_corrected().first()
        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-status'))

    def test_status_is_waiting_for_feedback(self):
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        testgroup = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback().first()
        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for feedback',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_status_is_waiting_for_deliveries(self):
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                first_deadline=timezone.now() + timedelta(days=2)))
        testgroup = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries().first()
        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for deliveries',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_not_available_unless_corrected(self):
        devilry_group_mommy_factories.feedbackset_first_try_unpublished()
        testgroup = AssignmentGroup.objects.annotate_with_is_corrected().first()
        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_comment_summary_is_available(self):
        mommy.make('core.AssignmentGroup')
        testgroup = AssignmentGroup.objects\
            .annotate_with_number_of_commentfiles_from_students()\
            .annotate_with_number_of_groupcomments_from_students()\
            .annotate_with_number_of_groupcomments_from_examiners()\
            .annotate_with_number_of_groupcomments_from_admins()\
            .first()

        selector = htmls.S(MockMultiselectItemValue(value=testgroup, assignment=testgroup.assignment).render())
        self.assertTrue(selector.exists('.devilry-cradmin-groupitemvalue-comments'))
        self.assertEqual(
            '0 comments from student. 0 files from student. 0 comments from examiner.',
            selector.one('.devilry-cradmin-groupitemvalue-comments').alltext_normalized)
