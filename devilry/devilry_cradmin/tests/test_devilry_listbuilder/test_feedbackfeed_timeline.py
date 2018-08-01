import htmls
from model_mommy import mommy
from django import test
from django.conf import settings

from devilry.apps.core.group_user_lookup import GroupUserLookup
from devilry.devilry_cradmin.devilry_listbuilder import feedbackfeed_timeline as listbuilder
from devilry.apps.core import models as core_models


class TestStudentGroupCommentItemValue(test.TestCase):
    """
    Test StudentGroupCommentItemValue info.
    """
    def __model_setup(self, anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF, request_devilryrole='examiner'):
        self.testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            anonymizationmode=anonymizationmode)
        self.testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=self.testassignment)
        self.candidate = mommy.make(
            'core.Candidate',
            assignment_group=self.testgroup,
            relatedstudent__user__fullname='Test User',
            relatedstudent__user__shortname='testuser@example.com',
            relatedstudent__period=self.testassignment.parentnode,
            relatedstudent__automatic_anonymous_id='Anonymous student')
        self.comment = mommy.make(
            'devilry_group.GroupComment',
            user=self.candidate.relatedstudent.user,
            user_role='student',
            feedback_set__group=self.testgroup)
        self.group_user_lookup = GroupUserLookup(
            group=self.testgroup,
            assignment=self.testassignment,
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            requestuser_devilryrole=request_devilryrole)

    def test_student_comment_devilryrole_examiner_is_not_anonymized(self):
        self.__model_setup()
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=self.candidate,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-both'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertIn('Test User(testuser@example.com)',
                      selector.one('.devilry-user-verbose-inline-both').alltext_normalized)

    def test_student_comment_devilryrole_examiner_assignment_semi_anonymized(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=self.candidate,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-fullname'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertNotIn('Test User(testuser@example.com)', selector.html)
        self.assertIn('Anonymous student', selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)

    def test_student_comment_devilryrole_examiner_assignment_fully_anonymized(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=self.candidate,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-fullname'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertNotIn('Test User(testuser@example.com)', selector.html)
        self.assertIn('Anonymous student', selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)

    def test_student_comment_devilryrole_student_assignment_fully_anonymized(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS, request_devilryrole='student')
        selector = htmls.S(listbuilder.ExaminerGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=None,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-both'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertIn('Test User(testuser@example.com)',
                      selector.one('.devilry-user-verbose-inline-both').alltext_normalized)

    def test_student_comment_devilryrole_subjectadmin_assignment_fully_anonymized(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS,
                           request_devilryrole='subjectadmin')
        selector = htmls.S(listbuilder.ExaminerGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=None,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-both'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertNotIn('Test User(testuser@example.com)', selector.html)

    def test_student_comment_devilryrole_subjectadmin_assignment_semi_anonymized(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS,
                           request_devilryrole='subjectadmin')
        selector = htmls.S(listbuilder.ExaminerGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=None,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-both'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertIn('Test User(testuser@example.com)',
                      selector.one('.devilry-user-verbose-inline-both').alltext_normalized)

    def test_student_comment_devilryrole_examiner_candidate_removed_relatedstudent_fallback(self):
        self.__model_setup()
        self.candidate.delete()
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=self.candidate,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-both'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertIn('Test User(testuser@example.com)',
                      selector.one('.devilry-user-verbose-inline-both').alltext_normalized)


class TestExaminerGroupCommentItemValue(test.TestCase):
    """
    Test ExaminerGroupCommentItemValue info.
    """
    def __model_setup(self, anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF, request_devilryrole='student'):
        self.testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            anonymizationmode=anonymizationmode)
        self.testgroup = mommy.make(
            'core.AssignmentGroup',
            parentnode=self.testassignment)
        self.relatedexaminer = mommy.make(
            'core.RelatedExaminer',
            user__fullname='Test User',
            user__shortname='testuser@example.com',
            period=self.testassignment.parentnode,
            automatic_anonymous_id='Anonymous examiner')
        self.comment = mommy.make(
            'devilry_group.GroupComment',
            user=self.relatedexaminer.user,
            user_role='examiner',
            feedback_set__group=self.testgroup)
        self.group_user_lookup = GroupUserLookup(
            group=self.testgroup,
            assignment=self.testassignment,
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            requestuser_devilryrole=request_devilryrole)

    def test_examiner_comment_devilryrole_student_non_anonymous(self):
        self.__model_setup()
        selector = htmls.S(listbuilder.ExaminerGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=None,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-fullname'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertIn('Test User(testuser@example.com)',
                      selector.one('.devilry-user-verbose-inline-both').alltext_normalized)

    def test_examiner_comment_devilryrole_student_semi_anonymous(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        selector = htmls.S(listbuilder.ExaminerGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=None,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-fullname'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertNotIn('Test User(testuser@example.com)', selector.html)
        self.assertIn('Anonymous examiner',
                      selector.one('.devilry-core-examiner-anonymous-name').alltext_normalized)

    def test_examiner_comment_devilryrole_student_fully_anonymous(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        selector = htmls.S(listbuilder.ExaminerGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=None,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-fullname'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertNotIn('Test User(testuser@example.com)', selector.html)
        self.assertIn('Anonymous examiner',
                      selector.one('.devilry-core-examiner-anonymous-name').alltext_normalized)

    def test_examiner_comment_devilryrole_examiner_not_anonymized_for_examiners(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS,
                           request_devilryrole='examiner')
        selector = htmls.S(listbuilder.ExaminerGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=None,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-both'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertIn('Test User(testuser@example.com)',
                      selector.one('.devilry-user-verbose-inline-both').alltext_normalized)

    def test_examiner_comment_devilryrole_subjectadmin_assignment_fully_anonymous(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS,
                           request_devilryrole='subjectadmin')
        selector = htmls.S(listbuilder.ExaminerGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=None,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-both'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertNotIn('Test User(testuser@example.com)', selector.html)

    def test_examiner_comment_devilryrole_subjectadmin_assignment_semi_anonymous(self):
        self.__model_setup(anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS,
                           request_devilryrole='subjectadmin')
        selector = htmls.S(listbuilder.ExaminerGroupCommentItemValue(
            requestuser=mommy.make(settings.AUTH_USER_MODEL),
            value=self.comment,
            devilry_viewrole=None,
            user_obj=None,
            assignment=self.testassignment,
            group_user_lookup=self.group_user_lookup
        ).render())
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-both'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertIn('Test User(testuser@example.com)',
                      selector.one('.devilry-user-verbose-inline-both').alltext_normalized)
