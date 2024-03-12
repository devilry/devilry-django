import htmls

from django import test
from django.conf import settings
from django.core import mail
from django.utils import timezone
from cradmin_legacy.crinstance import reverse_cradmin_url

from model_bakery import baker

from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_email.comment_email.comment_email import send_student_comment_email, \
    send_examiner_comment_email
from devilry.devilry_message.models import Message, MessageReceiver
from devilry.devilry_account.models import PermissionGroup


class TestCommentEmail(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()


class TestCommentEmailForUsersMixin(object):
    def _make_examineruser_with_email(self, group, email):
        examiner = baker.make('core.Examiner', assignmentgroup=group,
                              relatedexaminer__period=group.parentnode.parentnode)
        baker.make('devilry_account.UserEmail', user=examiner.relatedexaminer.user, email=email)
        return examiner.relatedexaminer.user

    def _make_studentuser_with_email(self, group, email):
        student = baker.make('core.Candidate', assignment_group=group,
                             relatedstudent__period=group.parentnode.parentnode)
        baker.make('devilry_account.UserEmail', user=student.relatedstudent.user, email=email)
        return student.relatedstudent.user

    def _make_feedbackset(self):
        """
        Simple setup used for testing mail content.
        """
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        return test_feedbackset


class TestStudentCommentEmail(TestCommentEmailForUsersMixin, test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_send_student_comment_body(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
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
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        commentfile1 = baker.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile1.py',
                                  filesize=5600)
        commentfile2 = baker.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile2.py',
                                  filesize=3600)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
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
            file_meta_list = [
                elem.alltext_normalized for elem in htmls.S(outbox.message().as_string()).list(
                    '.devilry-email-comment-uploaded-file-meta'
                )
            ]
            self.assertIn('{} (5.5 KB)'.format(commentfile1.filename, commentfile1.filesize), file_meta_list)
            self.assertIn('{} (3.5 KB)'.format(commentfile2.filename, commentfile2.filesize), file_meta_list)

    def test_send_student_comment_after_deadline_email_everyone_except_comment_poster_subject(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
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
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
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
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
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
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=True)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[1].subject,
            '[Devilry] You added a new delivery/comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_student_comment_message_and_message_receivers(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        other_user = self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=True)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(MessageReceiver.objects.count(), 2)
        self.assertTrue(MessageReceiver.objects.filter(user=other_user).exists())
        self.assertTrue(MessageReceiver.objects.filter(user=comment_user).exists())
        self.assertEqual(Message.objects.filter(status='sent').count(), 2)
        self.assertEqual(MessageReceiver.objects.filter(status='sent').count(), 2)

    def test_examiner_comment_post_subject(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='examiner@example.com')
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_EXAMINER,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='examiner@example.com')
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
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='admin@example.com')
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_ADMIN,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='admin@example.com')
        send_student_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            from_student_poster=False)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] An admin added a new comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))


class TestExaminerNotAssignedCommentEmail(TestCommentEmailForUsersMixin, test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def _setup_period_admin(self, assignment, admin_user=None):
        permission_group = baker.make(
            'devilry_account.PermissionGroup',
            grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN
        )
        baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=assignment.period,
            permissiongroup=permission_group
        )
        if not admin_user:
            admin_user = baker.make(settings.AUTH_USER_MODEL)
            baker.make('devilry_account.UserEmail', user=admin_user, email='period_admin@example.com')
        baker.make(
            'devilry_account.PermissionGroupUser',
            permissiongroup=permission_group,
            user=admin_user
        )

    def _setup_subject_admin(self, assignment):
        permission_group = baker.make(
            'devilry_account.PermissionGroup',
            grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN
        )
        baker.make(
            'devilry_account.SubjectPermissionGroup',
            subject=assignment.subject,
            permissiongroup=permission_group
        )
        admin_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', user=admin_user, email='subject_admin@example.com')
        baker.make(
            'devilry_account.PermissionGroupUser',
            permissiongroup=permission_group,
            user=admin_user
        )

    def _setup_department_admin(self, assignment):
        permission_group = baker.make(
            'devilry_account.PermissionGroup',
            grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN
        )
        baker.make(
            'devilry_account.SubjectPermissionGroup',
            subject=assignment.subject,
            permissiongroup=permission_group
        )
        admin_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', user=admin_user, email='department_admin@example.com')
        baker.make(
            'devilry_account.PermissionGroupUser',
            permissiongroup=permission_group,
            user=admin_user
        )

    def _setup_period_and_subject_admins(self, assignment):
        self._setup_period_admin(assignment=assignment)
        self._setup_subject_admin(assignment=assignment)

    def test_does_not_send_email_to_department_admins_sanity(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Setup admins.
        self._setup_period_and_subject_admins(assignment=testassignment)
        self._setup_department_admin(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 2)

        self.assertNotEqual(mail.outbox[0].recipients()[0], ['department_admin@example.com'])
        self.assertNotEqual(mail.outbox[1].recipients()[0], ['department_admin@example.com'])
        self.assertIn(mail.outbox[0].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])
        self.assertIn(mail.outbox[1].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])

    def test_send_examiner_comment_no_examiner_subject_from_student_after_deadline(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._setup_period_and_subject_admins(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(mail.outbox[0].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])
        self.assertIn(mail.outbox[1].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] A student added a new comment AFTER THE DEADLINE for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_examiner_comment_no_examiner_subject_from_student_before_deadline(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        self._setup_period_and_subject_admins(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(mail.outbox[0].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])
        self.assertIn(mail.outbox[1].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] A student added a new delivery/comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_examiner_comment_no_examiner_message_and_message_receivers_created(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        admin_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', user=admin_user, email='adminuser@example.com')
        self._setup_period_admin(assignment=testassignment, admin_user=admin_user)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(MessageReceiver.objects.count(), 1)
        self.assertTrue(MessageReceiver.objects.filter(user=admin_user).exists())
        self.assertEqual(Message.objects.filter(status='sent').count(), 1)
        self.assertEqual(MessageReceiver.objects.filter(status='sent').count(), 1)

    def test_send_examiner_comment_single_examiner_as_examiner_comment_poster(self):
        # Test that no e-mail is sent if the comment-poster is the only examiner in the group.
        # This is because we exclude the comment-poster (examiners does not receive a receipt),
        # but since the comment-poster is also an examiner that means that the group has an
        # examiner and no e-mail should be sent to admins.
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        self._setup_period_and_subject_admins(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Examiner', assignmentgroup=test_feedbackset.group, relatedexaminer__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_EXAMINER,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Message.objects.count(), 0)

    def test_send_examiner_comment_single_examiner_as_period_admin_comment_poster(self):
        # Tests that e-mail is not sent to the examiner-user when they also a period-admin
        # and posts a comment as admin.
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        self._setup_period_and_subject_admins(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='examiner@example.com')
        baker.make('core.Examiner', assignmentgroup=test_feedbackset.group, relatedexaminer__user=comment_user)
        self._setup_period_admin(assignment=testassignment, admin_user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_ADMIN,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='examiner@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Message.objects.count(), 0)

    def test_send_examiner_no_examiner_admin_comment(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._setup_period_and_subject_admins(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_ADMIN,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(mail.outbox[0].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])
        self.assertIn(mail.outbox[1].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] An admin added a new comment for {}'.format(
                test_feedbackset.group.parentnode.long_name)
        )

    def test_send_examiner_no_examiner_admin_empty_comment_skipped(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._setup_period_and_subject_admins(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='',
                                       user_role=Comment.USER_ROLE_ADMIN,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 0)

    def test_send_examiner_comment_examiner_assigned_and_subject_admin(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        self._setup_subject_admin(assignment=testassignment)
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        for outbox in mail.outbox:
            self.assertFalse(htmls.S(outbox.message().as_string()).exists('.devilry_email_comment_no_examiner'))

    def test_send_examiner_comment_examiner_assigned_and_period_admin(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        self._setup_period_admin(assignment=testassignment)
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        for outbox in mail.outbox:
            self.assertFalse(htmls.S(outbox.message().as_string()).exists('.devilry_email_comment_no_examiner'))

    def test_send_examiner_comment_examiner_assigned_and_admins(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        self._setup_period_and_subject_admins(assignment=testassignment)
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        for outbox in mail.outbox:
            self.assertFalse(htmls.S(outbox.message().as_string()).exists('.devilry_email_comment_no_examiner'))

    def test_send_examiner_no_examiner_period_admin(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        self._setup_period_admin(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['period_admin@example.com'])
        for outbox in mail.outbox:
            self.assertTrue(htmls.S(outbox.message().as_string()).exists('.devilry_email_comment_no_examiner'))

    def test_send_examiner_no_examiner_subject_admin(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        self._setup_subject_admin(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['subject_admin@example.com'])
        for outbox in mail.outbox:
            self.assertTrue(htmls.S(outbox.message().as_string()).exists('.devilry_email_comment_no_examiner'))

    def test_send_examiner_comment_no_examiner_body(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        self._setup_period_and_subject_admins(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',)

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(mail.outbox[0].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])
        self.assertIn(mail.outbox[1].recipients()[0], ['period_admin@example.com', 'subject_admin@example.com'])
        for outbox in mail.outbox:
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_assignment').alltext_normalized,
                'Assignment: {}'.format(testassignment.long_name)
            )
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_no_examiner').alltext_normalized,
                'You are receiving this e-mail because no examiners are assigned to the project group.'
            )
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_text').alltext_normalized,
                'This is a test'
            )
            self.assertEqual(
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_detail_text').alltext_normalized,
                'See the delivery feed for more details:'
            )
            url = reverse_cradmin_url(instanceid='devilry_group_admin', appname='feedbackfeed',
                                      roleid=testgroup.id)
            link_url = 'http://www.example.com' + url
            self.assertEqual(
                link_url,
                htmls.S(outbox.message().as_string()).one('.devilry_email_comment_detail_url').alltext_normalized
            )

    def test_send_examiner_comment_body_comment_with_files(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        self._setup_period_admin(assignment=testassignment)

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        commentfile1 = baker.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile1.py',
                                  filesize=5600)
        commentfile2 = baker.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile2.py',
                                  filesize=3600)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/')

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(htmls.S(mail.outbox[0].message().as_string()).exists('.devilry-email-comment-uploaded-files'))
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one('.devilry-email-comment-uploaded-files > p')
                 .alltext_normalized,
            'Uploaded files:')
        file_meta_list = [
            elem.alltext_normalized for elem in htmls.S(mail.outbox[0].message().as_string()).list(
                '.devilry-email-comment-uploaded-file-meta'
            )
        ]
        self.assertIn('{} (5.5 KB)'.format(commentfile1.filename, commentfile1.filesize), file_meta_list)
        self.assertIn('{} (3.5 KB)'.format(commentfile2.filename, commentfile2.filesize), file_meta_list)


class TestExaminerCommentEmail(TestCommentEmailForUsersMixin, test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_send_examiner_empty_comment_before_deadline(self):
        first_deadline = timezone.now() + timezone.timedelta(days=1)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1', first_deadline=first_deadline)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)

        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        before_original_deadline = test_groupcomment.feedback_set.group.parentnode.first_deadline > timezone.now()
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            before_original_deadline=before_original_deadline)

        self.assertEqual(len(mail.outbox), 0)

    def test_send_examiner_empty_comment_after_deadline(self):
        first_deadline = timezone.now() - timezone.timedelta(days=1)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1', first_deadline=first_deadline)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)

        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        before_original_deadline = test_groupcomment.feedback_set.group.parentnode.first_deadline > timezone.now()
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/',
            before_original_deadline=before_original_deadline)

        self.assertEqual(len(mail.outbox), 1)

    def test_send_examiner_comment_body(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
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
            self.assertFalse(htmls.S(outbox.message().as_string()).exists('.devilry_email_comment_no_examiner'))
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
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another examiner in the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        commentfile1 = baker.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile1.py',
                                  filesize=5600)
        commentfile2 = baker.make('devilry_comment.CommentFile', comment=test_groupcomment, filename='testfile2.py',
                                  filesize=3600)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/')

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(htmls.S(mail.outbox[0].message().as_string()).exists('.devilry-email-comment-uploaded-files'))
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one('.devilry-email-comment-uploaded-files > p')
                 .alltext_normalized,
            'Uploaded files:')
        file_meta_list = [
            elem.alltext_normalized for elem in htmls.S(mail.outbox[0].message().as_string()).list(
                '.devilry-email-comment-uploaded-file-meta'
            )
        ]
        self.assertIn('{} (5.5 KB)'.format(commentfile1.filename, commentfile1.filesize), file_meta_list)
        self.assertIn('{} (3.5 KB)'.format(commentfile2.filename, commentfile2.filesize), file_meta_list)

    def test_send_examiner_comment_subject_from_student_after_deadline(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
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
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['examiner@example.com'])
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] A student added a new delivery/comment for {}'.format(
                test_feedbackset.group.parentnode.long_name))

    def test_send_examiner_comment_message_and_message_receivers_created(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        examiner_user = self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Candidate', assignment_group=test_feedbackset.group, relatedstudent__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_STUDENT,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
        send_examiner_comment_email(
            comment_id=test_groupcomment.id,
            domain_url_start='http://www.example.com/', )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(MessageReceiver.objects.count(), 1)
        self.assertTrue(MessageReceiver.objects.filter(user=examiner_user).exists())
        self.assertEqual(Message.objects.filter(status='sent').count(), 1)
        self.assertEqual(MessageReceiver.objects.filter(status='sent').count(), 1)

    def test_send_examiner_comment_subject_from_student_another_examiner(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        baker.make('core.Examiner', assignmentgroup=test_feedbackset.group, relatedexaminer__user=comment_user)
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_EXAMINER,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
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
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        # Another user on the group
        self._make_examineruser_with_email(group=testgroup, email='examiner@example.com')

        # The user that posted the comment
        comment_user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com')
        test_groupcomment = baker.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset,
                                       text='This is a test',
                                       user_role=Comment.USER_ROLE_ADMIN,
                                       user=comment_user)
        baker.make('devilry_account.UserEmail', user=comment_user, email='testuser@example.com')
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
#         test_groupcomment = baker.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
#                                        user=baker.make(settings.AUTH_USER_MODEL))
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
#         test_groupcomment = baker.make('devilry_group.GroupComment',
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
#         test_groupcomment = baker.make('devilry_group.GroupComment',
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
