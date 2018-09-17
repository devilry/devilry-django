# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django.contrib import messages
from django.core import mail
from django.http import Http404
from django.utils import timezone
from model_mommy import mommy

from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django_cradmin import cradmin_testhelpers

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.apps.core import models as core_models
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.tests.test_feedbackfeed.mixins.test_feedbackfeed_admin import TestFeedbackfeedAdminMixin
from devilry.devilry_group.views.admin import feedbackfeed_admin
from devilry.devilry_comment import models as comment_models
from devilry.devilry_group.views import group_comment_edit_base


class TestFeedbackfeedAdminDiscussPublicView(TestCase, TestFeedbackfeedAdminMixin):
    viewclass = feedbackfeed_admin.AdminPublicDiscussView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_assignment_soft_deadline_info_box_not_rendered(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                      group__parentnode__deadline_handling=core_models.Assignment.DEADLINEHANDLING_SOFT)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-feedbackfeed-hard-deadline-info-box'))

    def test_assignment_hard_deadline_info_box_rendered(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                      group__parentnode__deadline_handling=core_models.Assignment.DEADLINEHANDLING_HARD)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-feedbackfeed-hard-deadline-info-box'))

    @override_settings(DEVILRY_HARD_DEADLINE_INFO_FOR_EXAMINERS_AND_ADMINS={
            '__default': 'Hard deadline info'
    })
    def test_assignment_hard_deadline_info_box_rendered_info_text_default(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                      group__parentnode__deadline_handling=core_models.Assignment.DEADLINEHANDLING_HARD)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser
        )
        self.assertEqual(
            mockresponse.selector.one('.devilry-feedbackfeed-hard-deadline-info-box').alltext_normalized,
            'Hard deadline info')

    def test_get_admin_form_heading(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-form-heading'))
        self.assertEquals(
            'Discuss with the student(s). Anything you write or upload here is visible to the student(s), '
            'examiners, and admins.',
            mockresponse.selector.one('.devilry-group-feedbackfeed-form-heading').alltext_normalized
        )

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choice_add_comment_public_button(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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

    def test_post_comment_mail_sent_to_everyone_in_group_sanity(self):
        admin = mommy.make('devilry_account.User', shortname='periodadmin', fullname='Thor')
        period = mommy.make_recipe('devilry.apps.core.period_active', admins=[admin])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # Create two examiners with mails
        examiner1 = mommy.make('core.Examiner', assignmentgroup=feedbackset.group)
        examiner1_email = mommy.make('devilry_account.UserEmail', user=examiner1.relatedexaminer.user,
                                     email='examiner1@example.com')
        examiner2 = mommy.make('core.Examiner', assignmentgroup=feedbackset.group)
        examiner2_email = mommy.make('devilry_account.UserEmail', user=examiner2.relatedexaminer.user,
                                     email='examiner2@example.com')

        # Create two students with mails
        student1 = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        student1_email = mommy.make('devilry_account.UserEmail', user=student1.relatedstudent.user,
                                    email='student1@example.com')
        student2 = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        student2_email = mommy.make('devilry_account.UserEmail', user=student2.relatedstudent.user,
                                    email='student2@example.com')
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=admin,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment'
                }
            })
        self.assertEqual(len(mail.outbox), 4)
        recipient_list = []
        for outbox in mail.outbox:
            recipient_list.append(outbox.recipients()[0])
        self.assertIn(examiner1_email.email, recipient_list)
        self.assertIn(examiner2_email.email, recipient_list)
        self.assertIn(student1_email.email, recipient_list)
        self.assertIn(student2_email.email, recipient_list)

    def test_upload_single_file_visibility_everyone(self):
        # Test that a CommentFile is created on upload.
        # Posting comment with visibility visible to everyone
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-form-heading'))
        self.assertEquals(
            'Internal notes for this student or project group. Visible only to examiners and admins. '
            'Notes are not visible to students.',
            mockresponse.selector.one('.devilry-group-feedbackfeed-form-heading').alltext_normalized
        )

    def test_get_feedbackfeed_admin_wysiwyg_get_comment_choice_add_comment_for_examiners_and_admins_button(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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

    def test_post_comment_email_sent_only_to_examiners_sanity(self):
        admin = mommy.make('devilry_account.User', shortname='periodadmin', fullname='Thor')
        period = mommy.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # Create two examiners with mails
        examiner1 = mommy.make('core.Examiner', assignmentgroup=feedbackset.group)
        examiner1_email = mommy.make('devilry_account.UserEmail', user=examiner1.relatedexaminer.user,
                                     email='examiner1@example.com')
        examiner2 = mommy.make('core.Examiner', assignmentgroup=feedbackset.group)
        examiner2_email = mommy.make('devilry_account.UserEmail', user=examiner2.relatedexaminer.user,
                                     email='examiner2@example.com')

        # Create two students with mails
        student1 = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        student1_email = mommy.make('devilry_account.UserEmail', user=student1.relatedstudent.user,
                                    email='student1@example.com')
        student2 = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        student2_email = mommy.make('devilry_account.UserEmail', user=student2.relatedstudent.user,
                                    email='student2@example.com')

        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=admin,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment'
                }
            })
        self.assertEqual(len(mail.outbox), 2)
        recipient_list = []
        for outbox in mail.outbox:
            recipient_list.append(outbox.recipients()[0])
        self.assertIn(examiner1_email.email, recipient_list)
        self.assertIn(examiner2_email.email, recipient_list)
        self.assertNotIn(student1_email.email, recipient_list)
        self.assertNotIn(student2_email.email, recipient_list)

    def test_upload_single_file_visibility_examiners_and_admins(self):
        # Test that a CommentFile is created on upload.
        # Posting comment with visibility visible to examiners and admins
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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


class TestAdminEditGroupCommentView(TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    Comment edit history related tests.
    """
    viewclass = feedbackfeed_admin.AdminEditGroupCommentView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __make_admin_comment(self, feedback_set, user=None):
        if not user:
            user = mommy.make(settings.AUTH_USER_MODEL)
        return mommy.make('devilry_group.GroupComment',
                          text='Test',
                          user=user,
                          user_role=group_models.GroupComment.USER_ROLE_ADMIN,
                          published_datetime=timezone.now(),
                          feedback_set=feedback_set)

    def __make_user_admin(self, user, assignment, permissiongroup_type='period'):
        if permissiongroup_type == 'period':
            permissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                         period=assignment.period)
        else:
            permissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                         period=assignment.period)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=user,
                   permissiongroup=permissiongroup.permissiongroup)

    def test_no_comment_raises_404(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        self.__make_user_admin(user=testuser, assignment=testgroup.parentnode)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'pk': 1})

    def test_raise_404_admin_can_not_edit_other_admins_comments_sanity(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = self.__make_admin_comment(feedback_set=testfeedbackset)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'pk': groupcomment.id})

    def test_raise_404_admin_can_not_edit_student_comments_sanity(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = mommy.make('devilry_group.GroupComment',
                                  user_role=group_models.GroupComment.USER_ROLE_STUDENT,
                                  published_datetime=timezone.now(),
                                  feedback_set=testfeedbackset)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'pk': groupcomment.id})

    def test_raise_404_admin_can_not_edit_examiner_comments_sanity(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = mommy.make('devilry_group.GroupComment',
                                  user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                                  published_datetime=timezone.now(),
                                  feedback_set=testfeedbackset)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'pk': groupcomment.id})

    def test_get_admin_can_edit_own_comment_ok(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = self.__make_admin_comment(feedback_set=testfeedbackset, user=testuser)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id})

    def test_post_ok(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = self.__make_admin_comment(feedback_set=testfeedbackset, user=testuser)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'text': 'Test edited'
                }
            })
        db_comment = group_models.GroupComment.objects.get(id=groupcomment.id)
        messagesmock.add.assert_called_once_with(messages.SUCCESS, 'Comment updated!', '')
        self.assertEqual(db_comment.text, 'Test edited')
        self.assertEqual(group_models.GroupCommentEditHistory.objects.count(), 1)

    def test_post_initial_empty_comment_can_be_edited(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = mommy.make('devilry_group.GroupComment',
                                  user=testuser,
                                  user_role=group_models.GroupComment.USER_ROLE_ADMIN,
                                  published_datetime=timezone.now(),
                                  feedback_set=testfeedbackset)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'text': 'edited'
                }
            })
        db_comment = group_models.GroupComment.objects.get(id=groupcomment.id)
        edit_history = group_models.GroupCommentEditHistory.objects.get()
        self.assertEqual(group_models.GroupCommentEditHistory.objects.count(), 1)
        self.assertEquals('edited', db_comment.text)
        self.assertEqual('', edit_history.pre_edit_text)
        self.assertEqual('edited', edit_history.post_edit_text)
        messagesmock.add.assert_called_once_with(messages.SUCCESS, 'Comment updated!', '')

    def test_post_messages_text_do_not_differ(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = self.__make_admin_comment(feedback_set=testfeedbackset, user=testuser)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'text': 'Test'
                }
            })
        db_comment = group_models.GroupComment.objects.get(id=groupcomment.id)
        messagesmock.add.assert_called_once_with(messages.SUCCESS, 'No changes, comment not updated', '')
        self.assertEqual(group_models.GroupCommentEditHistory.objects.count(), 0)
        self.assertEqual(db_comment.text, 'Test')
