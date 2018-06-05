from django import test
from django.core import mail
from django.conf import settings

from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_email.feedback_email.feedback_email import bulk_feedback_mail


class TestBulkMailSending(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_send_to_single_feedbackset(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1', parentnode__parentnode__long_name='Subject 1')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=1)
        student = mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('devilry_account.UserEmail', user=student.relatedstudent.user, email='student@example.com')
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        bulk_feedback_mail(feedbackset_id_list=[test_feedbackset.id], domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[Devilry] Feedback for {}'.format(testassignment.long_name))
        self.assertEqual(mail.outbox[0].recipients(), ['student@example.com'])
        mail_content = mail.outbox[0].message().as_string()
        self.assertIn('Assignment: {}'.format(testassignment.long_name), mail_content)
        self.assertIn('Subject: {}'.format(testassignment.parentnode.parentnode.long_name), mail_content)
        self.assertIn('Result: passed', mail_content)

    def test_send_to_multiple_feedbacksets(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset1 = group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        test_feedbackset2 = group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        test_feedbackset3 = group_mommy.feedbackset_first_attempt_published(group=testgroup3)
        student1 = mommy.make('core.Candidate', assignment_group=testgroup1)
        student2 = mommy.make('core.Candidate', assignment_group=testgroup2)
        student3 = mommy.make('core.Candidate', assignment_group=testgroup3)
        mommy.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        mommy.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        mommy.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=user)
        bulk_feedback_mail(feedbackset_id_list=[test_feedbackset1.id, test_feedbackset2.id, test_feedbackset3.id],
                           domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 3)
