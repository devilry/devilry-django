# Django imports
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

# Devilry imports
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.feedbackfeed_builder import builder_base
from devilry.devilry_group.feedbackfeed_builder.feedbackfeed_sidebarbuilder import FeedbackFeedSidebarBuilder
from devilry.devilry_group import models as group_models


class TestFeedbackfeedSidebarBuilder(TestCase):

    def test_feedbackset_numbering(self):
        # Test that the numbering of the feedbacksets are in ascending order.
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                is_last_in_group=None)
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() + timezone.timedelta(days=3)
        )

        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(testgroup, testuser, 'unused')
        sidebarbuilder = FeedbackFeedSidebarBuilder(feedbacksets=feedbackset_queryset)
        sidebarbuilder.build()
        sidebarlist = sidebarbuilder.get_as_list()

        # Loop through and check the numbering.
        for numbering, feedbackset_dict in enumerate(sidebarlist):
            self.assertEquals(numbering+1, feedbackset_dict['feedbackset_num'])

    def test_num_queries(self):
        # Must be refactored
        # Test that the number of queries performed is manageable
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset1 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                is_last_in_group=None)
        testfeedbackset2 = devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() + timezone.timedelta(days=3)
        )

        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset1)
        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset2)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment1)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment1)

        with self.assertNumQueries(4):
            feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(testgroup, testuser, 'unused')
            sidebarbuilder = FeedbackFeedSidebarBuilder(feedbacksets=feedbackset_queryset)
            sidebarbuilder.build()
            sidebarbuilder.get_as_list()

    def test_no_comments_if_no_files(self):
        # Test that the feedbacksets appears, but no comments if there are no files attached.
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset1 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                is_last_in_group=None)
        testfeedbackset2 = devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() + timezone.timedelta(days=3)
        )
        mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset1)
        mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset2)

        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(testgroup, testuser, 'unused')
        sidebarbuilder = FeedbackFeedSidebarBuilder(feedbacksets=feedbackset_queryset)
        sidebarbuilder.build()
        sidebarlist = sidebarbuilder.get_as_list()

        self.assertEquals(len(sidebarlist), 2)
        self.assertEquals(len(sidebarlist[0]['comments']), 0)
        self.assertEquals(len(sidebarlist[1]['comments']), 0)

    def test_feedbackset_ordering_get_as_list(self):
        # Must be refactored
        # Tests the ordering of FeedbackFeedSidebarBuilder
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=1),
                is_last_in_group=None)
        testfeedbackset1 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() + timezone.timedelta(days=2))

        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment)

        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset1)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment1)

        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(testgroup, testuser, 'unused')
        sidebarbuilder = FeedbackFeedSidebarBuilder(feedbacksets=feedbackset_queryset)
        sidebarbuilder.build()

        sidebarlist = sidebarbuilder.get_as_list()
        self.assertTrue(
                sidebarlist[0]['feedbackset'].current_deadline() < sidebarlist[1]['feedbackset'].current_deadline())

    def test_comments_ordering_get_as_list(self):
        # Must be refactored
        # Tests the ordering of FeedbackFeedSidebarBuilder
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment1)
        testcomment2 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment2)
        testcomment3 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment3)

        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(testgroup, testuser, 'unused')
        sidebarbuilder = FeedbackFeedSidebarBuilder(feedbacksets=feedbackset_queryset)
        sidebarbuilder.build()
        sidebarlist = sidebarbuilder.get_as_list()
        comments = sidebarlist[0]['comments']
        self.assertTrue(
                comments[0]['groupcomment'].published_datetime < comments[1]['groupcomment'].published_datetime)
        self.assertTrue(
                comments[1]['groupcomment'].published_datetime < comments[2]['groupcomment'].published_datetime)

    def test_files_for_comments(self):
        # Test the correct number of files for each comment and that it's the correct files.
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=1))

        # testcomment 1 with 3 CommentFiles
        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset, text='comment1')
        testfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile1')
        testfile2 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile2')
        testfile3 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile3')

        # testcomment 2 with 1 CommentFile
        testcomment2 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset, text='comment2')
        testfile4 = mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile1')

        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(testgroup, testuser, 'unused')
        sidebarbuilder = FeedbackFeedSidebarBuilder(feedbacksets=feedbackset_queryset)
        sidebarbuilder.build()
        sidebarlist = sidebarbuilder.get_as_list()

        # Test the number of files per GroupComment
        comments = sidebarlist[0]['comments']
        self.assertEquals(len(comments[0]['files']), 3)
        self.assertEquals(len(comments[1]['files']), 1)

        # Test CommentFiles for testcomment1
        testcomment1_files = comments[0]['files']
        self.assertEquals(testcomment1_files[0].filename, testfile1.filename)
        self.assertEquals(testcomment1_files[1].filename, testfile2.filename)
        self.assertEquals(testcomment1_files[2].filename, testfile3.filename)

        # Test CommentFiles for testcomment2
        testcomment2_files = comments[1]['files']
        self.assertEquals(testcomment2_files[0].filename, testfile4.filename)

    def test_items_in_builder_student(self):
        # Test that private comments are not fetched for student
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=1))

        # testcomment 1
        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset, text='comment1')
        mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile1')
        mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile2')
        mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile3')

        # testcomment 2
        testcomment2 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset, text='comment2')
        mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile1')

        # testcomment with visibility set to private
        private_comment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        mommy.make('devilry_comment.CommentFile', comment=private_comment, filename='private file')

        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(testgroup, testuser, 'student')
        sidebarbuilder = FeedbackFeedSidebarBuilder(feedbacksets=feedbackset_queryset)
        sidebarbuilder.build()
        sidebarlist = sidebarbuilder.get_as_list()

        # Get comments and loop through and check private_comments' published_datetime is not in any of the comment
        # dictionaries
        feedbackset_comments = sidebarlist[0]['comments']
        self.assertEquals(len(feedbackset_comments), 2)
        for comment_dict in feedbackset_comments:
            self.assertNotEquals(private_comment.published_datetime, comment_dict['groupcomment'].published_datetime)

    def test_items_in_builder_examiner(self):
        # Test that examiner can see private comment
        testuser_examiner = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=1))

        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset, text='comment1')
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment,
                   filename='testfile1')
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment,
                   filename='testfile2')
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment,
                   filename='testfile3')
        testcomment2 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset, text='comment2')
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment2,
                   filename='testfile1')
        private_comment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                     user=testuser_examiner)
        mommy.make('devilry_comment.CommentFile',
                   comment=private_comment,
                   filename='private file')

        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(testgroup, testuser_examiner, 'examiner')
        sidebarbuilder = FeedbackFeedSidebarBuilder(feedbacksets=feedbackset_queryset)
        sidebarbuilder.build()
        sidebarlist = sidebarbuilder.get_as_list()

        comments = sidebarlist[0]['comments']
        self.assertEquals(len(comments), 3)
        self.assertEquals(
                private_comment.published_datetime, comments[2]['groupcomment'].published_datetime)
