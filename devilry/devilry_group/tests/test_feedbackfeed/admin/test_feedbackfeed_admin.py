# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from model_mommy import mommy

from django.test import TestCase
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.tests.test_feedbackfeed.mixins.test_feedbackfeed_admin import TestFeedbackfeedAdminMixin
from devilry.devilry_group.views.admin import feedbackfeed_admin
from devilry.devilry_comment import models as comment_models


class TestFeedbackfeedAdminDiscussPublicView(TestCase, TestFeedbackfeedAdminMixin):
    viewclass = feedbackfeed_admin.AdminPublicDiscussView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_admin_form_heading(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-form-heading'))
        self.assertEquals(
            'Discuss with the student(s). Anything you write or upload here is visible to the student(s), '
            'examiners, and admins.',
            mockresponse.selector.one('.devilry-group-feedbackfeed-form-heading').alltext_normalized
        )

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choice_add_comment_public_button(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('#submit-id-admin_add_public_comment'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_post_feedbackset_comment_visible_to_everyone(self):
        admin = mommy.make('devilry_account.User', shortname='periodadmin', fullname='Thor')
        period = mommy.make_recipe('devilry.apps.core.period_active', admins=[admin])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=admin,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment'
                }
            })
        comments = group_models.GroupComment.objects.all()
        self.assertEquals(1, len(comments))
        self.assertEquals('visible-to-everyone', comments[0].visibility)
        self.assertEquals('periodadmin', comments[0].user.shortname)
        self.assertEquals(feedbackset.id, comments[0].feedback_set.id)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_upload_single_file_visibility_everyone(self):
        # Test that a CommentFile is created on upload.
        # Posting comment with visibility visible to everyone
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfile(
            user=testuser)
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEquals(1, comment_models.CommentFile.objects.count())

    def test_upload_single_file_content_visibility_everyone(self):
        # Test the content of a CommentFile after upload.
        # Posting comment with visibility visible to everyone
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile.txt', content=b'Test content', content_type='text/txt')
            ],
            user=testuser
        )
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, comment_models.CommentFile.objects.count())
        comment_file = comment_models.CommentFile.objects.all()[0]
        group_comment = group_models.GroupComment.objects.get(id=comment_file.comment.id)
        self.assertEquals(group_comment.visibility, group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEquals('testfile.txt', comment_file.filename)
        self.assertEquals('Test content', comment_file.file.file.read())
        self.assertEquals(len('Test content'), comment_file.filesize)
        self.assertEquals('text/txt', comment_file.mimetype)

    def test_upload_multiple_files_visibility_everyone(self):
        # Test the content of CommentFiles after upload.
        # Posting comment with visibility visible to everyone
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testuser
        )
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEqual(group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                         group_models.GroupComment.objects.all()[0].visibility)
        self.assertEquals(3, comment_models.CommentFile.objects.count())

    def test_upload_multiple_files_contents_visibility_everyone(self):
        # Test the content of a CommentFile after upload.
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testuser
        )
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEqual(group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                         group_models.GroupComment.objects.all()[0].visibility)
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

    def test_upload_files_and_comment_text(self):
        # Test the content of a CommentFile after upload.
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
            ],
            user=testuser
        )
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': 'Test comment',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(2, comment_models.CommentFile.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals('Test comment', group_comments[0].text)


class TestFeedbackfeedAdminWithExaminersDiscussView(TestCase, TestFeedbackfeedAdminMixin):
    viewclass = feedbackfeed_admin.AdminWithExaminersDiscussView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_admin_form_heading(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-form-heading'))
        self.assertEquals(
            'Internal notes for this student or project group. Visible only to examiners and admins. '
            'Notes are not visible to students.',
            mockresponse.selector.one('.devilry-group-feedbackfeed-form-heading').alltext_normalized
        )

    def test_get_feedbackfeed_admin_wysiwyg_get_comment_choice_add_comment_for_examiners_and_admins_button(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('#submit-id-admin_add_comment_for_examiners_and_admins'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_post_feedbackset_comment_visible_to_examiner_and_admins(self):
        admin = mommy.make('devilry_account.User', shortname='periodadmin', fullname='Thor')
        period = mommy.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=admin,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment'
                }
            })
        comments = group_models.GroupComment.objects.all()
        self.assertEquals(1, len(comments))
        self.assertEquals('visible-to-examiner-and-admins', comments[0].visibility)
        self.assertEquals('periodadmin', comments[0].user.shortname)
        self.assertEquals(feedbackset.id, comments[0].feedback_set.id)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_upload_single_file_visibility_examiners_and_admins(self):
        # Test that a CommentFile is created on upload.
        # Posting comment with visibility visible to examiners and admins
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfile(
            user=testuser)
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEqual(group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                         group_models.GroupComment.objects.all()[0].visibility)
        self.assertEquals(1, comment_models.CommentFile.objects.count())

    def test_upload_single_file_content_visibility_examiners_and_admins(self):
        # Test the content of a CommentFile after upload.
        # Posting comment with visibility visible to examiners and admins
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile.txt', content=b'Test content', content_type='text/txt')
            ],
            user=testuser
        )
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEqual(group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                         group_models.GroupComment.objects.all()[0].visibility)
        self.assertEquals(1, comment_models.CommentFile.objects.count())
        comment_file = comment_models.CommentFile.objects.all()[0]
        self.assertEqual('testfile.txt', comment_file.filename)
        self.assertEqual('Test content', comment_file.file.file.read())
        self.assertEqual(len('Test content'), comment_file.filesize)
        self.assertEqual('text/txt', comment_file.mimetype)

    def test_upload_multiple_files_visibility_examiners_and_admins(self):
        # Test the content of CommentFiles after upload.
        # Posting comment with visibility visible to everyone
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testuser
        )
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEqual(group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                         group_models.GroupComment.objects.all()[0].visibility)
        self.assertEquals(3, comment_models.CommentFile.objects.count())

    def test_upload_multiple_files_contents_visibility_examiners_and_admins(self):
        # Test the content of a CommentFile after upload.
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testuser
        )
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEqual(group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                         group_models.GroupComment.objects.all()[0].visibility)
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
