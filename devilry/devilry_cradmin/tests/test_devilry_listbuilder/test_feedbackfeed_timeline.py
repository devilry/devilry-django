import htmls
from model_mommy import mommy
from django import test
from django.conf import settings
from django.utils import timezone

from devilry.devilry_cradmin.devilry_listbuilder import feedbackfeed_timeline as listbuilder
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.feedbackfeed_builder import feedbackfeed_timelinebuilder
from devilry.devilry_group.feedbackfeed_builder import builder_base
from devilry.apps.core import models as core_models
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy


class TestGroupCommentItemValueStudentViewrole(test.TestCase):
    """
    Test with student as the viewrole.
    """
    def test_student_group_comment_item_value_non_anonymous(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent__user__fullname='Test User',
                               relatedstudent__user__shortname='testuser@example.com')
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set__group=testgroup)
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            value=comment,
            devilry_viewrole='examiner',
            user_obj=candidate,
            assignment=testassignment
        ).render())
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-fullname'))

    def test_student_group_comment_item_value_semi_anonymous(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent__user__fullname='Test User',
                               relatedstudent__user__shortname='testuser@example.com')
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set__group=testgroup)
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            value=comment,
            devilry_viewrole='examiner',
            user_obj=candidate,
            assignment=testassignment
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-fullname'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_student_group_comment_item_value_fully_anonymous(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent__user__fullname='Test User',
                               relatedstudent__user__shortname='testuser@example.com')
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set__group=testgroup)
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            value=comment,
            devilry_viewrole='examiner',
            user_obj=candidate,
            assignment=testassignment
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-fullname'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))


class TestGroupCommentItemValueExaminerViewrole(test.TestCase):
    """
    Test with examiner as the viewrole.
    """
    def test_examiner_group_comment_item_value_non_anonymous(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer__user__fullname='Test User',
                              relatedexaminer__user__shortname='testuser@example.com')
        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             feedback_set__group=testgroup)
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            value=comment,
            devilry_viewrole='student',
            user_obj=examiner,
            assignment=testassignment
        ).render())
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-fullname'))

    def test_examiner_group_comment_item_value_semi_anonymous(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer__user__fullname='Test User',
                              relatedexaminer__user__shortname='testuser@example.com')
        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             feedback_set__group=testgroup)
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            value=comment,
            devilry_viewrole='student',
            user_obj=examiner,
            assignment=testassignment
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-fullname'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_examiner_group_comment_item_value_fully_anonymous(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer__user__fullname='Test User',
                              relatedexaminer__user__shortname='testuser@example.com')
        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             feedback_set__group=testgroup)
        selector = htmls.S(listbuilder.StudentGroupCommentItemValue(
            value=comment,
            devilry_viewrole='student',
            user_obj=examiner,
            assignment=testassignment
        ).render())
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-fullname'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))
