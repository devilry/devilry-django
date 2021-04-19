from datetime import datetime
from pprint import pprint

import htmls
from django import test
from django.core import mail
from django.utils import timezone
from django.template import defaultfilters

from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_email.deadline_email import deadline_email
from devilry.devilry_message.models import Message, MessageReceiver


class TestNewAttemptEmail(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __setup_feedback_set(self, new_deadline):
        """
        Simple setup used for testing mail content.
        """
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup, grading_points=1,
                                                                           deadline_datetime=new_deadline)
        student = baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('devilry_account.UserEmail', user=student.relatedstudent.user, email='student@example.com')
        return test_feedbackset

    def test_send_new_attempt_email_subject(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=timezone.now() + timezone.timedelta(days=10))
        deadline_email.bulk_send_new_attempt_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/'
        )
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] New attempt for {}'.format(test_feedbackset.group.parentnode.long_name))

    def test_send_new_attempt_email_recipients(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=timezone.now() + timezone.timedelta(days=10))
        deadline_email.bulk_send_new_attempt_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/'
        )
        self.assertEqual(mail.outbox[0].recipients(), ['student@example.com'])

    def test_send_new_attempt_email_body_text_with_deadline(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=datetime.utcnow())
        deadline_email.bulk_send_new_attempt_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_deadline_new_attempt_info_text').alltext_normalized,
            'You have been given a new attempt in {} with deadline {}'.format(
                test_feedbackset.group.parentnode.long_name,
                defaultfilters.date(test_feedbackset.deadline_datetime, 'DATETIME_FORMAT')))
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_deadline_new_attempt_detail_text').alltext_normalized,
            'See the delivery feed for more details:')

    def test_send_new_attempt_email_link(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=timezone.now() + timezone.timedelta(days=10))
        deadline_email.bulk_send_new_attempt_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/'
        )
        feedback_link = 'http://www.example.com/devilry_group/student/{}/feedbackfeed/'.format(
            test_feedbackset.group.id)
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_deadline_new_attempt_detail_url').alltext_normalized,
            feedback_link)

    def test_send_new_attempt_email_message_and_messagereceivers_created(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=timezone.now() + timezone.timedelta(days=10))
        deadline_email.bulk_send_new_attempt_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/'
        )
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(MessageReceiver.objects.count(), 1)


class TestNewAttemptBulkEmail(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_bulk_send_emails(self):
        new_deadline = datetime.utcnow()
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_fb1 = group_baker.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1, deadline_datetime=new_deadline)
        test_fb2 = group_baker.feedbackset_first_attempt_published(
            group=testgroup2, grading_points=1, deadline_datetime=new_deadline)
        test_fb3 = group_baker.feedbackset_first_attempt_published(
            group=testgroup3, grading_points=1, deadline_datetime=new_deadline)
        student1 = baker.make('core.Candidate', assignment_group=testgroup1)
        baker.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        student2 = baker.make('core.Candidate', assignment_group=testgroup2)
        baker.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        student3 = baker.make('core.Candidate', assignment_group=testgroup3)
        baker.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        deadline_email.bulk_send_new_attempt_email(
            assignment_id=testassignment.id,
            feedbackset_id_list=[test_fb1.id, test_fb2.id, test_fb3.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 3)

        recipient_list = []
        for mail_item in mail.outbox:
            self.assertEqual(len(mail_item.recipients()), 1)
            recipient_list.append(mail_item.recipients()[0])
        self.assertIn('student1@example.com', recipient_list)
        self.assertIn('student2@example.com', recipient_list)
        self.assertIn('student3@example.com', recipient_list)

    def test_bulk_send_emails_message_and_messagereceivers_created(self):
        new_deadline = datetime.utcnow()
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_fb1 = group_baker.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1, deadline_datetime=new_deadline)
        test_fb2 = group_baker.feedbackset_first_attempt_published(
            group=testgroup2, grading_points=1, deadline_datetime=new_deadline)
        test_fb3 = group_baker.feedbackset_first_attempt_published(
            group=testgroup3, grading_points=1, deadline_datetime=new_deadline)
        student1 = baker.make('core.Candidate', assignment_group=testgroup1)
        baker.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        student2 = baker.make('core.Candidate', assignment_group=testgroup2)
        baker.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        student3 = baker.make('core.Candidate', assignment_group=testgroup3)
        baker.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        deadline_email.bulk_send_new_attempt_email(
            assignment_id=testassignment.id,
            feedbackset_id_list=[test_fb1.id, test_fb2.id, test_fb3.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(MessageReceiver.objects.count(), 3)


class TestDeadlineMovedEmail(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __setup_feedback_set(self, new_deadline):
        """
        Simple setup used for testing mail content.
        """
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup, grading_points=1,
                                                                           deadline_datetime=new_deadline)
        student = baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('devilry_account.UserEmail', user=student.relatedstudent.user, email='student@example.com')
        return test_feedbackset

    def test_send_deadline_moved_email_subject(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=timezone.now() + timezone.timedelta(days=10))
        deadline_email.bulk_send_deadline_moved_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/'
        )
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] Deadline moved for {}'.format(test_feedbackset.group.parentnode.long_name))

    def test_deadline_moved_email_recipients(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=timezone.now() + timezone.timedelta(days=10))
        deadline_email.bulk_send_deadline_moved_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/'
        )
        self.assertEqual(mail.outbox[0].recipients(), ['student@example.com'])

    def test_deadline_moved_email_body_text_without_deadline(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=datetime.utcnow())
        deadline_email.bulk_send_deadline_moved_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_deadline_moved_info_text').alltext_normalized,
            'The deadline for {} has been moved.'.format(test_feedbackset.group.parentnode.long_name))
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_deadline_moved_to_info_text').alltext_normalized,
            'New deadline is {}'.format(defaultfilters.date(test_feedbackset.deadline_datetime, 'DATETIME_FORMAT')))
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_deadline_detail_text').alltext_normalized,
            'See the delivery feed for more details:')

    def test_deadline_moved_email_link(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=timezone.now() + timezone.timedelta(days=10))
        deadline_email.bulk_send_deadline_moved_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/'
        )
        feedback_link = 'http://www.example.com/devilry_group/student/{}/feedbackfeed/'.format(
            test_feedbackset.group.id)
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_deadline_detail_url').alltext_normalized,
            feedback_link)

    def test_deadline_moved_email_message_and_messagereceivers_created(self):
        test_feedbackset = self.__setup_feedback_set(new_deadline=timezone.now() + timezone.timedelta(days=10))
        deadline_email.bulk_send_deadline_moved_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/'
        )
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(MessageReceiver.objects.count(), 1)


class TestDeadlineMovedBulkEmail(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_bulk_send_emails(self):
        new_deadline = datetime.utcnow()
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_fb1 = group_baker.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1, deadline_datetime=new_deadline)
        test_fb2 = group_baker.feedbackset_first_attempt_published(
            group=testgroup2, grading_points=1, deadline_datetime=new_deadline)
        test_fb3 = group_baker.feedbackset_first_attempt_published(
            group=testgroup3, grading_points=1, deadline_datetime=new_deadline)
        student1 = baker.make('core.Candidate', assignment_group=testgroup1)
        baker.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        student2 = baker.make('core.Candidate', assignment_group=testgroup2)
        baker.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        student3 = baker.make('core.Candidate', assignment_group=testgroup3)
        baker.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        deadline_email.bulk_send_deadline_moved_email(
            assignment_id=testassignment.id,
            feedbackset_id_list=[test_fb1.id, test_fb2.id, test_fb3.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 3)

        recipient_list = []
        for mail_item in mail.outbox:
            self.assertEqual(len(mail_item.recipients()), 1)
            recipient_list.append(mail_item.recipients()[0])
        self.assertIn('student1@example.com', recipient_list)
        self.assertIn('student2@example.com', recipient_list)
        self.assertIn('student3@example.com', recipient_list)

    def test_bulk_send_emails_message_and_messagereceivers_created(self):
        new_deadline = datetime.utcnow()
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 1')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_fb1 = group_baker.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1, deadline_datetime=new_deadline)
        test_fb2 = group_baker.feedbackset_first_attempt_published(
            group=testgroup2, grading_points=1, deadline_datetime=new_deadline)
        test_fb3 = group_baker.feedbackset_first_attempt_published(
            group=testgroup3, grading_points=1, deadline_datetime=new_deadline)
        student1 = baker.make('core.Candidate', assignment_group=testgroup1)
        baker.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        student2 = baker.make('core.Candidate', assignment_group=testgroup2)
        baker.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        student3 = baker.make('core.Candidate', assignment_group=testgroup3)
        baker.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        deadline_email.bulk_send_deadline_moved_email(
            assignment_id=testassignment.id,
            feedbackset_id_list=[test_fb1.id, test_fb2.id, test_fb3.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(len(mail.outbox), 3)

        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(MessageReceiver.objects.count(), 3)
