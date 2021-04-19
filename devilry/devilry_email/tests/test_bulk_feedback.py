from django import test
from django.core import mail
from django.conf import settings

from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_email.feedback_email.feedback_email import bulk_send_feedback_created_email
from devilry.devilry_message.models import Message, MessageReceiver


class TestBulkFeedbackMailSending(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_send_to_single_feedbackset(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1', parentnode__parentnode__long_name='Subject 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup, grading_points=1)
        student = baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('devilry_account.UserEmail', user=student.relatedstudent.user, email='student@example.com')
        user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        bulk_send_feedback_created_email(
            assignment_id=testassignment.id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[Devilry] Feedback for {}'.format(testassignment.long_name))
        self.assertEqual(mail.outbox[0].recipients(), ['student@example.com'])
        mail_content = mail.outbox[0].message().as_string()
        self.assertIn('Assignment: {}'.format(testassignment.long_name), mail_content)
        self.assertIn('Subject: {}'.format(testassignment.parentnode.parentnode.long_name), mail_content)
        self.assertIn('Result: passed', mail_content)

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(MessageReceiver.objects.count(), 1)
        message_receiver = MessageReceiver.objects.get()
        self.assertEqual(message_receiver.user, student.relatedstudent.user)

    def test_send_to_multiple_feedbacksets(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset1 = group_baker.feedbackset_first_attempt_published(group=testgroup1)
        test_feedbackset2 = group_baker.feedbackset_first_attempt_published(group=testgroup2)
        test_feedbackset3 = group_baker.feedbackset_first_attempt_published(group=testgroup3)
        student1 = baker.make('core.Candidate', assignment_group=testgroup1)
        student2 = baker.make('core.Candidate', assignment_group=testgroup2)
        student3 = baker.make('core.Candidate', assignment_group=testgroup3)
        baker.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        baker.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        baker.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=user)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=user)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=user)
        bulk_send_feedback_created_email(
            assignment_id=testassignment.id,
            feedbackset_id_list=[test_feedbackset1.id, test_feedbackset2.id, test_feedbackset3.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 3)

        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(MessageReceiver.objects.count(), 3)
        receiver_users = [receiver.user for receiver in MessageReceiver.objects.all()]
        self.assertIn(student1.relatedstudent.user, receiver_users)
        self.assertIn(student2.relatedstudent.user, receiver_users)
        self.assertIn(student3.relatedstudent.user, receiver_users)
