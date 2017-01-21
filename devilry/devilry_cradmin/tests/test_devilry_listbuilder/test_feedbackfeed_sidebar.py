import htmls
import mock
from django import test
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from django_cradmin.cradmin_testhelpers import TestCaseMixin
from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.feedbackfeed_builder import builder_base
from devilry.devilry_group.feedbackfeed_builder import feedbackfeed_sidebarbuilder
from devilry.devilry_cradmin.devilry_listbuilder import feedbackfeed_sidebar


class TestFeedbackfeedSidebarListBuilderList(TestCaseMixin, test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    # def test_listbuilder_sidebar_complete_example(self):
    #     # Just a sanity check with a full example comprising of two FeedbackSets
    #     # with one GroupComment each and one CommentFile for each GroupComment.
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
    #     testcomment1 = mommy.make('devilry_group.GroupComment',
    #                               created_datetime=testfeedbackset1.current_deadline() - timezone.timedelta(hours=1),
    #                               published_datetime=testfeedbackset1.current_deadline() - timezone.timedelta(hours=1),
    #                               user=candidate.relatedstudent.user,
    #                               user_role='student',
    #                               feedback_set=testfeedbackset1)
    #     commentfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile1.txt')
    #     commentfile1.file.save('testfile1.txt', ContentFile(''))
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
    #     testcomment2 = mommy.make('devilry_group.GroupComment',
    #                               created_datetime=testfeedbackset2.current_deadline() - timezone.timedelta(hours=1),
    #                               published_datetime=testfeedbackset2.current_deadline() - timezone.timedelta(hours=1),
    #                               user=candidate.relatedstudent.user,
    #                               user_role='student',
    #                               feedback_set=testfeedbackset2)
    #     commentfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile2.txt')
    #     commentfile1.file.save('testfile2.txt', ContentFile(''))
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
    #
    #     built_sidebar = feedbackfeed_sidebarbuilder.FeedbackFeedSidebarBuilder(
    #         group=testgroup,
    #         feedbacksets=feedbackset_queryset,
    #     )
    #     built_sidebar.build()
    #
    #     listbuilder_list = feedbackfeed_sidebar.SidebarListBuilderList.from_built_sidebar(
    #         built_sidebar=built_sidebar,
    #         group=testgroup,
    #         devilryrole='student',
    #         assignment=testassignment
    #     )
    #
    #     # Checks the structure of the built list:
    #     #
    #     # FeedbackSetItemValue
    #     #     GroupCommentListBuilderList
    #     #     GroupCommentItemValue
    #     #         FileListBuilderList
    #     #         FileItemValue
    #     # FeedbackSetItemValue
    #     #     GroupCommentListBuilderList
    #     #     GroupCommentItemValue
    #     #         FileListBuilderList
    #     #         FileItemValue
    #
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[0],
    #                                feedbackfeed_sidebar.FeedbackSetItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[1],
    #                                feedbackfeed_sidebar.GroupCommentListBuilderList))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[1].renderable_list[0],
    #                                feedbackfeed_sidebar.GroupCommentItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[1].renderable_list[1],
    #                                feedbackfeed_sidebar.FileListBuilderList))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[1].renderable_list[1].renderable_list[0],
    #                                feedbackfeed_sidebar.FileItemValue))
    #
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[2],
    #                                feedbackfeed_sidebar.FeedbackSetItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[3],
    #                                feedbackfeed_sidebar.GroupCommentListBuilderList))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[3].renderable_list[0],
    #                                feedbackfeed_sidebar.GroupCommentItemValue))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[3].renderable_list[1],
    #                                feedbackfeed_sidebar.FileListBuilderList))
    #     self.assertTrue(isinstance(listbuilder_list.renderable_list[3].renderable_list[1].renderable_list[0],
    #                                feedbackfeed_sidebar.FileItemValue))
