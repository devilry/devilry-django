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


class TestFeedbackfeedTimelineListBuilderList(test.TestCase):
    """
    Testing the listbuilder and the items it holds.
    """
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    # def test_listbuilder_list_items_complete_example(self):
    #     """
    #     Test a complete example of the listbuilder with all events.
    #     """
    #     testuser = mommy.make(settings.AUTH_USER_MODEL)
    #     testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
    #     testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
    #     candidate = mommy.make('core.Candidate',
    #                            assignment_group=testgroup,
    #                            relatedstudent__user__fullname='Test User1',
    #                            relatedstudent__user__shortname='testuser1@example.com')
    #     examiner = mommy.make('core.Examiner',
    #                           assignmentgroup=testgroup,
    #                           relatedexaminer_user__fullname='Test User2',
    #                           relatedexaminer__user__shortname='testuser2@example.com')
    #     testfeedbackset1 = group_mommy.feedbackset_first_attempt_published(
    #             grading_published_datetime=(testassignment.first_deadline + timezone.timedelta(days=1)),
    #             grading_points=10,
    #             created_by=examiner.relatedexaminer.user,
    #             created_datetime=(testassignment.publishing_time),
    #             is_last_in_group=None,
    #             group=testgroup,
    #             grading_published_by=examiner.relatedexaminer.user)
    #     mommy.make('devilry_group.GroupComment',
    #                created_datetime=testfeedbackset1.current_deadline() - timezone.timedelta(hours=1),
    #                published_datetime=testfeedbackset1.current_deadline() - timezone.timedelta(hours=1),
    #                user=candidate.relatedstudent.user,
    #                user_role='student',
    #                feedback_set=testfeedbackset1)
    #     mommy.make('devilry_group.GroupComment',
    #                created_datetime=testfeedbackset1.current_deadline() + timezone.timedelta(hours=1),
    #                published_datetime=testfeedbackset1.current_deadline() + timezone.timedelta(hours=1),
    #                user=examiner.relatedexaminer.user,
    #                user_role='examiner',
    #                part_of_grading=True,
    #                feedback_set=testfeedbackset1)
    #
    #     testfeedbackset2 = group_mommy.feedbackset_new_attempt_published(
    #             grading_published_datetime=testfeedbackset1.grading_published_datetime + timezone.timedelta(days=4),
    #             grading_points=10,
    #             created_by=examiner.relatedexaminer.user,
    #             created_datetime=testfeedbackset1.grading_published_datetime + timezone.timedelta(hours=10),
    #             deadline_datetime=testfeedbackset1.grading_published_datetime + timezone.timedelta(days=3),
    #             group=testgroup,
    #             grading_published_by=examiner.relatedexaminer.user)
    #     mommy.make('devilry_group.GroupComment',
    #                created_datetime=testfeedbackset2.current_deadline() - timezone.timedelta(hours=1),
    #                published_datetime=testfeedbackset2.current_deadline() - timezone.timedelta(hours=1),
    #                user=candidate.relatedstudent.user,
    #                user_role='student',
    #                feedback_set=testfeedbackset2)
    #     mommy.make('devilry_group.GroupComment',
    #                created_datetime=testfeedbackset2.current_deadline() + timezone.timedelta(hours=1),
    #                published_datetime=testfeedbackset2.current_deadline() + timezone.timedelta(hours=1),
    #                user=examiner.relatedexaminer.user,
    #                user_role='examiner',
    #                part_of_grading=True,
    #                feedback_set=testfeedbackset2)
    #
    #     feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
    #         group=testgroup,
    #         requestuser=testuser,
    #         devilryrole='student'
    #     )
    #     built_timeline = feedbackfeed_timelinebuilder.FeedbackFeedTimelineBuilder(
    #         assignment=testassignment,
    #         feedbacksets=feedbackset_queryset,
    #         group=testgroup
    #     )
    #
    #     built_timeline.build()
    #     listbuilder_list = listbuilder.TimelineListBuilderList.from_built_timeline(
    #         built_timeline,
    #         group=testgroup,
    #         devilryrole='student',
    #         assignment=testassignment
    #     )
    #
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[0], listbuilder.StudentGroupCommentItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[1], listbuilder.DeadlineExpiredItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[2], listbuilder.ExaminerGroupCommentItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[3], listbuilder.GradeItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[4], listbuilder.StudentGroupCommentItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[5], listbuilder.DeadlineExpiredItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[6], listbuilder.ExaminerGroupCommentItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[7], listbuilder.GradeItemValue))


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
