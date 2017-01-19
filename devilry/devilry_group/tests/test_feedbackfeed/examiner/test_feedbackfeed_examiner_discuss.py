# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.tests.test_feedbackfeed.mixins import test_feedbackfeed_examiner
from devilry.devilry_group.views.examiner import feedbackfeed_examiner


class TestFeedbackfeedExaminerDiscuss(TestCase, test_feedbackfeed_examiner.TestFeedbackfeedExaminerMixin):
    viewclass = feedbackfeed_examiner.ExaminerDiscussView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choice_add_comment_for_examiners_and_admins_button(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_comment_for_examiners'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choice_add_comment_public_button(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_public_comment'))

    def test_get_no_form_grade_option(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertFalse(mockresponse.selector.exists('#div_id_passed'))
        self.assertFalse(mockresponse.selector.exists('#div_id_points'))

    def test_get_examiner_no_comment_delete_option_when_published(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'),)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=examiner.assignmentgroup)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   text='this was a draft, and is now a feedback',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   feedback_set=feedbackset)
        feedbackset.publish(published_by=examiner.relatedexaminer.user, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertFalse(mockresponse.selector.exists('.btn-danger'))

    def test_post_feedbackset_comment_with_text(self):
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testfeedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())

    def test_post_feedbackset_comment_with_text_published_datetime_is_set(self):
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testfeedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_public_comment': 'unused value'
                }
            })
        self.assertIsNotNone(group_models.GroupComment.objects.all()[0].published_datetime)

    def test_post_feedbackset_comment_visible_to_everyone(self):
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testfeedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_public_comment': 'unused value'
                }
            })
        self.assertEquals('visible-to-everyone', group_models.GroupComment.objects.all()[0].visibility)

    def test_post_feedbackset_comment_visible_to_examiner_and_admins(self):
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testfeedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_comment_for_examiners': 'unused value'
                }
            })
        self.assertEquals('visible-to-examiner-and-admins', group_models.GroupComment.objects.all()[0].visibility)

    def test_post_comment_always_to_last_feedbackset(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment
                                       .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        feedbackset_first = group_mommy.feedbackset_first_attempt_published(group=group)
        feedbackset_last = group_mommy.feedbackset_new_attempt_unpublished(group=group)
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_add_public_comment': 'unused value',
                }
            })
        comments = group_models.GroupComment.objects.all()
        self.assertEquals(len(comments), 1)
        self.assertNotEquals(feedbackset_first, comments[0].feedback_set)
        self.assertEquals(feedbackset_last, comments[0].feedback_set)
        self.assertEquals(2, group_models.FeedbackSet.objects.count())

    def test_get_num_queries(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mommy.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        with self.assertNumQueries(12):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=examiner.relatedexaminer.user)

    def test_get_num_queries_with_commentfiles(self):
        """
        NOTE: (works as it should)
        Checking that no more queries are executed even though the
        :func:`devilry.devilry_group.feedbackfeed_builder.FeedbackFeedTimelineBuilder.__get_feedbackset_queryset`
        duplicates comment_file query.
        """
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mommy.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        comment1 = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set=testfeedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user=examiner.relatedexaminer.user,
                              user_role='examiner',
                              feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   filename='test.py',
                   comment=comment1,
                   _quantity=20)
        mommy.make('devilry_comment.CommentFile',
                   filename='test2.py',
                   comment=comment2,
                   _quantity=20)
        with self.assertNumQueries(12):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=examiner.relatedexaminer.user)


class TestFeedbackfeedFileUploadExaminer(TestCase, test_feedbackfeed_examiner.TestFeedbackfeedExaminerMixin):
    viewclass = feedbackfeed_examiner.ExaminerDiscussView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_comment_without_text_or_file_visibility_everyone(self):
        # Tests that error message pops up if trying to post a comment without either text or file.
        # Posting comment with visibility visible to everyone
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_public_comment': 'unused value'
                }
            })
        self.assertEquals(0, group_models.GroupComment.objects.count())
        self.assertEqual(
            'A comment must have either text or a file attached, or both. An empty comment is not allowed.',
            mockresponse.selector.one('#error_1_id_text').alltext_normalized)

    def test_comment_without_text_or_file_visibility_examiners_and_admins(self):
        # Tests that error message pops up if trying to post a comment without either text or file.
        # Posting comment with visibility for examiners and admins only
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_comment_for_examiners': 'unused value'
                }
            })
        self.assertEquals(0, group_models.GroupComment.objects.count())
        self.assertEqual(
            'A comment must have either text or a file attached, or both. An empty comment is not allowed.',
            mockresponse.selector.one('#error_1_id_text').alltext_normalized)

    def test_upload_single_file_visibility_everyone(self):
        # Test that a CommentFile is created on upload.
        # Posting comment with visibility visible to everyone
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfile(
            user=testexaminer.relatedexaminer.user)
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_public_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEquals(1, comment_models.CommentFile.objects.count())

    def test_upload_single_file_content_visibility_everyone(self):
        # Test the content of a CommentFile after upload.
        # Posting comment with visibility visible to everyone
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile.txt', content=b'Test content', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_public_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, comment_models.CommentFile.objects.count())
        comment_file = comment_models.CommentFile.objects.all()[0]
        self.assertEqual('testfile.txt', comment_file.filename)
        self.assertEqual('Test content', comment_file.file.file.read())
        self.assertEqual(len('Test content'), comment_file.filesize)
        self.assertEqual('text/txt', comment_file.mimetype)

    def test_upload_single_file_visibility_examiners_and_admins(self):
        # Test that a CommentFile is created on upload.
        # Posting comment with visibility visible to examiners and admins
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfile(
            user=testexaminer.relatedexaminer.user)
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_comment_for_examiners': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEquals(1, comment_models.CommentFile.objects.count())

    def test_upload_single_file_content_visibility_examiners_and_admins(self):
        # Test the content of a CommentFile after upload.
        # Posting comment with visibility visible to examiners and admins
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile.txt', content=b'Test content', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_comment_for_examiners': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, comment_models.CommentFile.objects.count())
        comment_file = comment_models.CommentFile.objects.all()[0]
        self.assertEqual('testfile.txt', comment_file.filename)
        self.assertEqual('Test content', comment_file.file.file.read())
        self.assertEqual(len('Test content'), comment_file.filesize)
        self.assertEqual('text/txt', comment_file.mimetype)

    def test_upload_multiple_files_visibility_everyone(self):
        # Test the content of CommentFiles after upload.
        # Posting comment with visibility visible to everyone
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_public_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(3, comment_models.CommentFile.objects.count())

    def test_upload_multiple_files_contents_visibility_everyone(self):
        # Test the content of a CommentFile after upload.
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_public_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(3, comment_models.CommentFile.objects.count())
        comment_file1 = comment_models.CommentFile.objects.get(filename='testfile1.txt')
        comment_file2 = comment_models.CommentFile.objects.get(filename='testfile2.txt')
        comment_file3 = comment_models.CommentFile.objects.get(filename='testfile3.txt')

        # Check content of testfile 1.
        self.assertEqual('testfile1.txt', comment_file1.filename)
        self.assertEqual('Test content1', comment_file1.file.file.read())
        self.assertEqual(len('Test content1'), comment_file1.filesize)
        self.assertEqual('text/txt', comment_file1.mimetype)

        # Check content of testfile 2.
        self.assertEqual('testfile2.txt', comment_file2.filename)
        self.assertEqual('Test content2', comment_file2.file.file.read())
        self.assertEqual(len('Test content2'), comment_file2.filesize)
        self.assertEqual('text/txt', comment_file2.mimetype)

        # Check content of testfile 3.
        self.assertEqual('testfile3.txt', comment_file3.filename)
        self.assertEqual('Test content3', comment_file3.file.file.read())
        self.assertEqual(len('Test content3'), comment_file3.filesize)
        self.assertEqual('text/txt', comment_file3.mimetype)

    def test_upload_multiple_files_visibility_examiners_and_admins(self):
        # Test the content of CommentFiles after upload.
        # Posting comment with visibility visible to everyone
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_comment_for_examiners': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(3, comment_models.CommentFile.objects.count())

    def test_upload_multiple_files_contents_visibility_examiners_and_admins(self):
        # Test the content of a CommentFile after upload.
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'examiner_add_comment_for_examiners': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(3, comment_models.CommentFile.objects.count())
        comment_file1 = comment_models.CommentFile.objects.get(filename='testfile1.txt')
        comment_file2 = comment_models.CommentFile.objects.get(filename='testfile2.txt')
        comment_file3 = comment_models.CommentFile.objects.get(filename='testfile3.txt')

        # Check content of testfile 1.
        self.assertEqual('testfile1.txt', comment_file1.filename)
        self.assertEqual('Test content1', comment_file1.file.file.read())
        self.assertEqual(len('Test content1'), comment_file1.filesize)
        self.assertEqual('text/txt', comment_file1.mimetype)

        # Check content of testfile 2.
        self.assertEqual('testfile2.txt', comment_file2.filename)
        self.assertEqual('Test content2', comment_file2.file.file.read())
        self.assertEqual(len('Test content2'), comment_file2.filesize)
        self.assertEqual('text/txt', comment_file2.mimetype)

        # Check content of testfile 3.
        self.assertEqual('testfile3.txt', comment_file3.filename)
        self.assertEqual('Test content3', comment_file3.file.file.read())
        self.assertEqual(len('Test content3'), comment_file3.filesize)
        self.assertEqual('text/txt', comment_file3.mimetype)

    def test_comment_only_with_text_visibility_everyone(self):
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'test',
                    'examiner_add_public_comment': 'unused value',
                }
            })

        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEqual('test', group_models.GroupComment.objects.all()[0].text)
        self.assertEqual(0, comment_models.CommentFile.objects.count())

    def test_comment_only_with_text_visibility_examiners_and_admins(self):
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'test',
                    'examiner_add_comment_for_examiners': 'unused value',
                }
            })

        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEqual('test', group_models.GroupComment.objects.all()[0].text)
        self.assertEqual(0, comment_models.CommentFile.objects.count())

    def test_upload_files_and_comment_text(self):
        # Test the content of a CommentFile after upload.
        testfeedbackset = group_mommy.feedbackset_first_attempt_published()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
            ],
            user=testexaminer.relatedexaminer.user
        )
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'Test comment',
                    'examiner_add_public_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(2, comment_models.CommentFile.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals('Test comment', group_comments[0].text)