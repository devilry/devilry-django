from datetime import datetime

from django import test
from django.conf import settings
from django.core import mail
from django.utils import timezone
from django.template import defaultfilters

from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_email.comment_email.comment_email import send_comment_email, send_student_comment_email, \
    send_examiner_comment_email, bulk_send_comment_email_to_students_and_examiners


class TestCommentEmail(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __make_groupcomment(self, comment_published_datetime=None, user=None):
        """
        Simple setup used for testing mail content.
        """
        if not user:
            user = mommy.make(settings.AUTH_USER_MODEL)
        if not comment_published_datetime:
            comment_published_datetime = timezone.now()
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        student = mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=user)
        mommy.make('devilry_account.UserEmail', user=student.relatedstudent.user, email='student@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                       published_datetime=comment_published_datetime)
        return test_groupcomment

    def test_send_comment_email_subject(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        test_groupcomment = self.__make_groupcomment(user=user)
        send_comment_email(
            group=test_groupcomment.feedback_set.group,
            published_datetime=test_groupcomment.published_datetime,
            user_list=[user],
            feedbackfeed_url='/')
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] New comment in group for {}'.format(test_groupcomment.feedback_set.group.parentnode.long_name))

    def test_send_comment_email_recipients(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        test_groupcomment = self.__make_groupcomment(user=user)
        send_comment_email(
            group=test_groupcomment.feedback_set.group,
            published_datetime=test_groupcomment.published_datetime,
            user_list=[user],
            feedbackfeed_url='/')
        self.assertEqual(mail.outbox[0].recipients(), ['student@example.com'])

    def test_send_comment_email_body_info_text(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        test_groupcomment = self.__make_groupcomment(comment_published_datetime=datetime.utcnow(), user=user)
        send_comment_email(
            group=test_groupcomment.feedback_set.group,
            published_datetime=test_groupcomment.published_datetime,
            user_list=[user],
            feedbackfeed_url='/')
        self.assertIn(
            'New comment added in {} on {}.'.format(
                test_groupcomment.feedback_set.group.parentnode.long_name,
                defaultfilters.date(test_groupcomment.published_datetime, 'DATETIME_FORMAT')),
            mail.outbox[0].body)

    def test_send_comment_email_body_link(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        test_groupcomment = self.__make_groupcomment(comment_published_datetime=datetime.utcnow(), user=user)
        feedbackfeed_url = 'http://www.example.com'
        send_comment_email(
            group=test_groupcomment.feedback_set.group,
            published_datetime=test_groupcomment.published_datetime,
            user_list=[user],
            feedbackfeed_url=feedbackfeed_url
        )
        self.assertIn(
            'Assignment link: <a href="{}">{}</a>'.format(feedbackfeed_url, feedbackfeed_url),
            mail.outbox[0].body)


class TestCommentEmailForUsersMixin(object):
    def _make_examineruser_with_email(self, group, email):
        examiner = mommy.make('core.Examiner', assignmentgroup=group)
        user_email = mommy.make('devilry_account.UserEmail', user=examiner.relatedexaminer.user, email=email)
        return user_email

    def _make_studentuser_with_email(self, group, email):
        student = mommy.make('core.Candidate', assignment_group=group)
        user_email = mommy.make('devilry_account.UserEmail', user=student.relatedstudent.user, email=email)
        return user_email

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

    def test_send_student_comment_email_body_link_to_student_feedbackfeed(self):
        test_feedbackset = self._make_feedbackset()
        self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                       user=mommy.make(settings.AUTH_USER_MODEL))
        send_student_comment_email(
            group_id=test_groupcomment.feedback_set.group.id,
            comment_user_id=test_groupcomment.user.id,
            published_datetime=test_groupcomment.published_datetime,
            domain_url_start='http://www.example.com/')
        feedbackfeed_url = 'http://www.example.com/devilry_group/student/{}/feedbackfeed/'.format(
            test_feedbackset.group_id
        )
        self.assertIn(
            'Assignment link: <a href="{}">{}</a>'.format(feedbackfeed_url, feedbackfeed_url),
            mail.outbox[0].body)

    def test_send_student_comment_email_recipients(self):
        test_feedbackset = self._make_feedbackset()
        student_email1 = self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')
        student_email2 = self._make_studentuser_with_email(group=test_feedbackset.group, email='student2@example.com')
        student_email3 = self._make_studentuser_with_email(group=test_feedbackset.group, email='student3@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                       user=mommy.make(settings.AUTH_USER_MODEL))
        send_student_comment_email(
            group_id=test_groupcomment.feedback_set.group.id,
            comment_user_id=test_groupcomment.user.id,
            published_datetime=test_groupcomment.published_datetime,
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox[0].recipients()), 3)
        self.assertIn(student_email1.email, mail.outbox[0].recipients())
        self.assertIn(student_email2.email, mail.outbox[0].recipients())
        self.assertIn(student_email3.email, mail.outbox[0].recipients())

    def test_send_student_comment_email_excludes_comment_user(self):
        test_feedbackset = self._make_feedbackset()
        student_email1 = self._make_studentuser_with_email(group=test_feedbackset.group, email='student1@example.com')
        student_email2 = self._make_studentuser_with_email(group=test_feedbackset.group, email='student2@example.com')
        student_email3 = self._make_studentuser_with_email(group=test_feedbackset.group, email='student3@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset, user=student_email1.user)
        send_student_comment_email(
            group_id=test_groupcomment.feedback_set.group.id,
            comment_user_id=test_groupcomment.user.id,
            published_datetime=test_groupcomment.published_datetime,
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox[0].recipients()), 2)
        self.assertNotIn(student_email1.email, mail.outbox[0].recipients())
        self.assertIn(student_email2.email, mail.outbox[0].recipients())
        self.assertIn(student_email3.email, mail.outbox[0].recipients())


class TestExaminerCommentEmail(TestCommentEmailForUsersMixin, test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_send_examiner_comment_email_body_link_to_examiner_feedbackfeed(self):
        test_feedbackset = self._make_feedbackset()
        self._make_examineruser_with_email(group=test_feedbackset.group, email='examiner1@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                       user=mommy.make(settings.AUTH_USER_MODEL))
        send_examiner_comment_email(
            group_id=test_groupcomment.feedback_set.group.id,
            comment_user_id=test_groupcomment.user.id,
            published_datetime=test_groupcomment.published_datetime,
            domain_url_start='http://www.example.com/')
        feedbackfeed_url = 'http://www.example.com/devilry_group/examiner/{}/feedbackfeed/'.format(
            test_feedbackset.group_id
        )
        self.assertIn(
            'Assignment link: <a href="{}">{}</a>'.format(feedbackfeed_url, feedbackfeed_url),
            mail.outbox[0].body)

    def test_send_examiner_comment_email_recipients(self):
        test_feedbackset = self._make_feedbackset()
        examiner_email1 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner1@example.com')
        examiner_email2 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner2@example.com')
        examiner_email3 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner3@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                       user=mommy.make(settings.AUTH_USER_MODEL))
        send_examiner_comment_email(
            group_id=test_groupcomment.feedback_set.group.id,
            comment_user_id=test_groupcomment.user.id,
            published_datetime=test_groupcomment.published_datetime,
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox[0].recipients()), 3)
        self.assertIn(examiner_email1.email, mail.outbox[0].recipients())
        self.assertIn(examiner_email2.email, mail.outbox[0].recipients())
        self.assertIn(examiner_email3.email, mail.outbox[0].recipients())

    def test_send_examiner_comment_email_excludes_comment_user(self):
        test_feedbackset = self._make_feedbackset()
        examiner_email1 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner1@example.com')
        examiner_email2 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner2@example.com')
        examiner_email3 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner3@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset, user=examiner_email1.user)
        send_examiner_comment_email(
            group_id=test_groupcomment.feedback_set.group.id,
            comment_user_id=test_groupcomment.user.id,
            published_datetime=test_groupcomment.published_datetime,
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox[0].recipients()), 2)
        self.assertNotIn(examiner_email1.email, mail.outbox[0].recipients())
        self.assertIn(examiner_email2.email, mail.outbox[0].recipients())
        self.assertIn(examiner_email3.email, mail.outbox[0].recipients())


class TestBulkSendCommentEmail(TestCommentEmailForUsersMixin, test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_send_email_to_examiner_and_students(self):
        test_feedbackset = self._make_feedbackset()
        examiner_email1 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner1@example.com')
        examiner_email2 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner2@example.com')
        student_email1 = self._make_studentuser_with_email(
            group=test_feedbackset.group, email='student1@example.com')
        student_email2 = self._make_studentuser_with_email(
            group=test_feedbackset.group, email='student2@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                       user=mommy.make(settings.AUTH_USER_MODEL))
        bulk_send_comment_email_to_students_and_examiners(
            group_id=test_groupcomment.feedback_set.group.id,
            comment_user_id=test_groupcomment.user.id,
            published_datetime=test_groupcomment.published_datetime,
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 2)
        recipient_list = []
        for email in mail.outbox[0].recipients():
            recipient_list.append(str(email))
        for email in mail.outbox[1].recipients():
            recipient_list.append(str(email))
        self.assertEqual(len(recipient_list), 4)
        self.assertIn(examiner_email1.email, recipient_list)
        self.assertIn(examiner_email2.email, recipient_list)
        self.assertIn(student_email1.email, recipient_list)
        self.assertIn(student_email2.email, recipient_list)

    def test_send_email_to_examiner_and_students_exclude_student_commenter(self):
        test_feedbackset = self._make_feedbackset()
        examiner_email1 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner1@example.com')
        examiner_email2 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner2@example.com')
        student_email1 = self._make_studentuser_with_email(
            group=test_feedbackset.group, email='student1@example.com')
        student_email2 = self._make_studentuser_with_email(
            group=test_feedbackset.group, email='student2@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset, user=student_email1.user)
        bulk_send_comment_email_to_students_and_examiners(
            group_id=test_groupcomment.feedback_set.group.id,
            comment_user_id=test_groupcomment.user.id,
            published_datetime=test_groupcomment.published_datetime,
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 2)
        recipient_list = []
        for email in mail.outbox[0].recipients():
            recipient_list.append(str(email))
        for email in mail.outbox[1].recipients():
            recipient_list.append(str(email))
        self.assertEqual(len(recipient_list), 3)
        self.assertNotIn(student_email1.email, recipient_list)
        self.assertIn(examiner_email1.email, recipient_list)
        self.assertIn(examiner_email2.email, recipient_list)
        self.assertIn(student_email2.email, recipient_list)

    def test_send_email_to_examiner_and_students_exclude_examiner_commenter(self):
        test_feedbackset = self._make_feedbackset()
        examiner_email1 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner1@example.com')
        examiner_email2 = self._make_examineruser_with_email(
            group=test_feedbackset.group, email='examiner2@example.com')
        student_email1 = self._make_studentuser_with_email(
            group=test_feedbackset.group, email='student1@example.com')
        student_email2 = self._make_studentuser_with_email(
            group=test_feedbackset.group, email='student2@example.com')
        test_groupcomment = mommy.make('devilry_group.GroupComment',
                                       feedback_set=test_feedbackset, user=examiner_email1.user)
        bulk_send_comment_email_to_students_and_examiners(
            group_id=test_groupcomment.feedback_set.group.id,
            comment_user_id=test_groupcomment.user.id,
            published_datetime=test_groupcomment.published_datetime,
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 2)
        recipient_list = []
        for email in mail.outbox[0].recipients():
            recipient_list.append(str(email))
        for email in mail.outbox[1].recipients():
            recipient_list.append(str(email))
        self.assertEqual(len(recipient_list), 3)
        self.assertNotIn(examiner_email1.email, recipient_list)
        self.assertIn(examiner_email2.email, recipient_list)
        self.assertIn(student_email1.email, recipient_list)
        self.assertIn(student_email2.email, recipient_list)
