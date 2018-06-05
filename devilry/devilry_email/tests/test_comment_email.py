from datetime import datetime

import htmls
from django.template import defaultfilters
from django import test
from django.conf import settings
from django.core import mail
from django.utils import timezone
from django.template import defaultfilters
from django_cradmin.crinstance import reverse_cradmin_url

from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_email.comment_email.comment_email import send_comment_email, send_student_comment_email, \
    send_examiner_comment_email, bulk_send_comment_email_to_students_and_examiners


class TestCommentEmail(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()


class TestCommentEmailForUsersMixin(object):
    def _make_examineruser_with_email(self, group, email):
        examiner = mommy.make('core.Examiner', assignmentgroup=group,
                              relatedexaminer__period=group.parentnode.parentnode)
        mommy.make('devilry_account.UserEmail', user=examiner.relatedexaminer.user, email=email)
        return examiner.relatedexaminer.user

    def _make_studentuser_with_email(self, group, email):
        student = mommy.make('core.Candidate', assignment_group=group,
                             relatedstudent__period=group.parentnode.parentnode)
        mommy.make('devilry_account.UserEmail', user=student.relatedstudent.user, email=email)
        return student.relatedstudent.user

    def _make_feedbackset(self):
        """
        Simple setup used for testing mail content.
        """
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        return test_feedbackset


class TestStudentCommentEmail(TestCommentEmailForUsersMixin, test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_assignment_fully_anonymous_student_can_not_see_examiner_name(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # The student that receives the email
        self._make_studentuser_with_email(group=testgroup, email='student@example.com')

        # Examiner that posted the comment
        examiner_user = self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       user=examiner_user,
                                       user_role=Comment.USER_ROLE_EXAMINER)

        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=True)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].recipients(), ['student@example.com'])
        self.assertNotIn('student@example.com', mail.outbox[0].message())
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one('.devilry_email_comment_added_by').alltext_normalized,
            'Added by: Automatic anonymous ID missing')

    def test_send_student_comment_body(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=True)

        self.assertEqual(len(mail.outbox), 2)
        for outbox in mail.outbox:
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_assignment').alltext_normalized,
                'Assignment: {}'.format(testassignment.long_name)
            )
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_added_by').alltext_normalized,
                'Added by: {}'.format('testuser@example.com')
            )
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_text').alltext_normalized,
                'This is a test'
            )
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_detail_text').alltext_normalized,
                'See the delivery feed for more details:'
            )
            url = reverse_cradmin_url(instanceid='devilry_group_student', appname='feedbackfeed', roleid=testgroup.id)
            link_url = 'http://www.example.com' + url
            self.assertEqual(
                link_url,
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_detail_url').alltext_normalized
            )

    def test_send_student_comment_body_comment_with_files(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        commentfile1 = mommy.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile1.py',
                                  filesize=5600)
        commentfile2 = mommy.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile2.py',
                                  filesize=3600)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=True)

        self.assertEqual(len(mail.outbox), 2)
        for outbox in mail.outbox:
            self.assertTrue(htmls.S(outbox.message().as_string()).exists('.devilry-email-comment-uploaded-files'))
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry-email-comment-uploaded-files > p')
                    .alltext_normalized,
                'Uploaded files:')
            file_meta_list = [elem.alltext_normalized for elem in htmls.S(outbox.message().as_string()).list('.devilry-email-comment-uploaded-file-meta')]
            self.assertIn('{} (5.5 KB)'.format(commentfile1.filename, commentfile1.filesize), file_meta_list)
            self.assertIn('{} (3.5 KB)'.format(commentfile2.filename, commentfile2.filesize), file_meta_list)

    def test_send_student_comment_after_deadline_email_everyone_except_comment_poster_subject(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=True)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] A student added a new comment AFTER THE DEADLINE for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_student_comment_before_deadline_email_everyone_except_comment_poster_subject(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=True)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] A student added a new delivery/comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_student_comment_after_deadline_email_to_comment_poster_subject(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=True)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[1].subject,
            '[Devilry] You added a new comment AFTER THE DEADLINE for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_student_comment_before_deadline_email_to_comment_poster_subject(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=True)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[1].subject,
            '[Devilry] You added a new delivery/comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_examiner_comment_post_subject(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='examiner@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_EXAMINER,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='examiner@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=False)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] An examiner added a new comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_admin_comment_post_subject(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='admin@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_ADMIN,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='admin@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=False)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] An admin added a new comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))


class TestExaminerCommentEmail(TestCommentEmailForUsersMixin, test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_assignment_fully_anonymous_examiner_can_not_see_student_name(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # The student that posted the comment
        student_user = self._make_studentuser_with_email(group=testgroup, email='student@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       user=student_user,
                                       user_role=Comment.USER_ROLE_STUDENT)

        # The examiner that receives the email
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        self.assertNotIn('student@example.com', mail.outbox[0].message())
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one('.devilry_email_comment_added_by').alltext_normalized,
            'Added by: Automatic anonymous ID missing')

    def test_send_examiner_comment_body(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        for outbox in mail.outbox:
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_assignment').alltext_normalized,
                'Assignment: {}'.format(testassignment.long_name)
            )
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_added_by').alltext_normalized,
                'Added by: {}'.format('testuser@example.com')
            )
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_text').alltext_normalized,
                'This is a test'
            )
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_detail_text').alltext_normalized,
                'See the delivery feed for more details:'
            )
            url = reverse_cradmin_url(instanceid='devilry_group_examiner', appname='feedbackfeed',
                                      roleid=testgroup.id)
            link_url = 'http://www.example.com' + url
            self.assertEqual(
                link_url,
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_detail_url').alltext_normalized
            )

    def test_send_examiner_comment_body_comment_with_files(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another examiner in the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        commentfile1 = mommy.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile1.py',
                                  filesize=5600)
        commentfile2 = mommy.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile2.py',
                                  filesize=3600)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/')

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(htmls.S(mail.outbox[0].message().as_string()).exists('.devilry-email-comment-uploaded-files'))
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one('.devilry-email-comment-uploaded-files > p')
                .alltext_normalized,
            'Uploaded files:')
        file_meta_list = [elem.alltext_normalized for elem in htmls.S(mail.outbox[0].message().as_string()).list('.devilry-email-comment-uploaded-file-meta')]
        self.assertIn('{} (5.5 KB)'.format(commentfile1.filename, commentfile1.filesize), file_meta_list)
        self.assertIn('{} (3.5 KB)'.format(commentfile2.filename, commentfile2.filesize), file_meta_list)

    def test_send_examiner_comment_subject_from_student_after_deadline(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] A student added a new comment AFTER THE DEADLINE for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_examiner_comment_subject_from_student_before_deadline(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] A student added a new delivery/comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_examiner_comment_subject_from_student_another_examiner(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        mommy.make('core.Examiner', assignmentgroup=test_feedbackset.group, relatedexaminer__user=comment_user)
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_EXAMINER,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] An examiner added a new comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_examiner_comment_subject_from_admin(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_ADMIN,
                                       user=comment_user)
        mommy.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] An admin added a new comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))


# class TestBulkSendCommentEmail(TestCommentEmailForUsersMixin, test.TestCase):
#     def setUp(self):
#         AssignmentGroupDbCacheCustomSql().initialize()
#
#     def test_send_email_to_examiner_and_students(self):
#         test_feedbackset = self._make_feedbackset()
#         examiner_email1 = self._make_examineruser_with_email(
#             group=test_feedbackset.group, email='examiner1@example.com')
#         examiner_email2 = self._make_examineruser_with_email(
#             group=test_feedbackset.group, email='examiner2@example.com')
#         student_email1 = self._make_studentuser_with_email(
#             group=test_feedbackset.group, email='student1@example.com')
#         student_email2 = self._make_studentuser_with_email(
#             group=test_feedbackset.group, email='student2@example.com')
#         test_groupcomment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
#                                        user=mommy.make(settings.AUTH_USER_MODEL))
#         bulk_send_comment_email_to_students_and_examiners(
#             group_id=test_groupcomment.feedback_set.group.id,
#             comment_user_id=test_groupcomment.user.id,
#             published_datetime=test_groupcomment.published_datetime,
#             domain_url_start='http://www.example.com/')
#         self.assertEqual(len(mail.outbox), 2)
#         recipient_list = []
#         for email in mail.outbox[0].recipients():
#             recipient_list.append(str(email))
#         for email in mail.outbox[1].recipients():
#             recipient_list.append(str(email))
#         self.assertEqual(len(recipient_list), 4)
#         self.assertIn(examiner_email1.email, recipient_list)
#         self.assertIn(examiner_email2.email, recipient_list)
#         self.assertIn(student_email1.email, recipient_list)
#         self.assertIn(student_email2.email, recipient_list)
#
#     def test_send_email_to_examiner_and_students_exclude_student_commenter(self):
#         test_feedbackset = self._make_feedbackset()
#         examiner_email1 = self._make_examineruser_with_email(
#             group=test_feedbackset.group, email='examiner1@example.com')
#         examiner_email2 = self._make_examineruser_with_email(
#             group=test_feedbackset.group, email='examiner2@example.com')
#         student_email1 = self._make_studentuser_with_email(
#             group=test_feedbackset.group, email='student1@example.com')
#         student_email2 = self._make_studentuser_with_email(
#             group=test_feedbackset.group, email='student2@example.com')
#         test_groupcomment = mommy.make('devilry_group.GroupComment',
#                                        feedback_set=test_feedbackset, user=student_email1.user)
#         bulk_send_comment_email_to_students_and_examiners(
#             group_id=test_groupcomment.feedback_set.group.id,
#             comment_user_id=test_groupcomment.user.id,
#             published_datetime=test_groupcomment.published_datetime,
#             domain_url_start='http://www.example.com/')
#         self.assertEqual(len(mail.outbox), 2)
#         recipient_list = []
#         for email in mail.outbox[0].recipients():
#             recipient_list.append(str(email))
#         for email in mail.outbox[1].recipients():
#             recipient_list.append(str(email))
#         self.assertEqual(len(recipient_list), 3)
#         self.assertNotIn(student_email1.email, recipient_list)
#         self.assertIn(examiner_email1.email, recipient_list)
#         self.assertIn(examiner_email2.email, recipient_list)
#         self.assertIn(student_email2.email, recipient_list)
#
#     def test_send_email_to_examiner_and_students_exclude_examiner_commenter(self):
#         test_feedbackset = self._make_feedbackset()
#         examiner_email1 = self._make_examineruser_with_email(
#             group=test_feedbackset.group, email='examiner1@example.com')
#         examiner_email2 = self._make_examineruser_with_email(
#             group=test_feedbackset.group, email='examiner2@example.com')
#         student_email1 = self._make_studentuser_with_email(
#             group=test_feedbackset.group, email='student1@example.com')
#         student_email2 = self._make_studentuser_with_email(
#             group=test_feedbackset.group, email='student2@example.com')
#         test_groupcomment = mommy.make('devilry_group.GroupComment',
#                                        feedback_set=test_feedbackset, user=examiner_email1.user)
#         bulk_send_comment_email_to_students_and_examiners(
#             group_id=test_groupcomment.feedback_set.group.id,
#             comment_user_id=test_groupcomment.user.id,
#             published_datetime=test_groupcomment.published_datetime,
#             domain_url_start='http://www.example.com/')
#         self.assertEqual(len(mail.outbox), 2)
#         recipient_list = []
#         for email in mail.outbox[0].recipients():
#             recipient_list.append(str(email))
#         for email in mail.outbox[1].recipients():
#             recipient_list.append(str(email))
#         self.assertEqual(len(recipient_list), 3)
#         self.assertNotIn(examiner_email1.email, recipient_list)
#         self.assertIn(examiner_email2.email, recipient_list)
#         self.assertIn(student_email1.email, recipient_list)
#         self.assertIn(student_email2.email, recipient_list)
