import htmls
from django import test
from django.core import mail
from django.utils import timezone
from django.template import defaultfilters

from datetime import datetime
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_email.feedback_email import feedback_email
from devilry.apps.core.models import Assignment
from devilry.devilry_message.models import Message


class TestFeedbackEmail(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __setup_feedback_set(self, deadline_datetime=None, grading_published_datetime=None):
        """
        Simple setup used for testing mail content.
        """
        if not deadline_datetime:
            deadline_datetime = timezone.now()
        if not grading_published_datetime:
            grading_published_datetime = timezone.now()
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
                                           long_name='Assignment 1', parentnode__parentnode__long_name='Subject 1')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_published(
            group=testgroup, deadline_datetime=deadline_datetime,
            grading_published_datetime=grading_published_datetime, grading_points=1)
        student = baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('devilry_account.UserEmail', user=student.relatedstudent.user, email='student@example.com')
        return test_feedbackset

    def test_send_feedback_email_subject(self):
        test_feedbackset = self.__setup_feedback_set()
        feedback_email.send_feedback_email(
            assignment=test_feedbackset.group.parentnode,
            feedback_sets=[test_feedbackset],
            domain_url_start='http://www.example.com/',
            feedback_type='feedback_created')
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] Feedback for {}'.format(test_feedbackset.group.parentnode.long_name))

    def test_send_feedback_email_recipients(self):
        test_feedbackset = self.__setup_feedback_set()
        feedback_email.send_feedback_email(
            assignment=test_feedbackset.group.parentnode,
            feedback_sets=[test_feedbackset],
            domain_url_start='http://www.example.com/',
            feedback_type='feedback_created')
        self.assertEqual(
            mail.outbox[0].recipients(),
            ['student@example.com'])

    def test_send_feedback_email_body_result(self):
        test_feedbackset = self.__setup_feedback_set()
        feedback_email.send_feedback_email(
            assignment=test_feedbackset.group.parentnode,
            feedback_sets=[test_feedbackset],
            domain_url_start='http://www.example.com/',
            feedback_type='feedback_created')
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_feedback_result').alltext_normalized,
            'Result: 1/1 ( passed )')

    def test_send_feedback_email_body_result_point_to_grade_mapper(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
                                           max_points=100,
                                           long_name='Assignment 1', parentnode__parentnode__long_name='Subject 1')
        point_to_grade_map = baker.make(
            'core.PointToGradeMap',
            assignment=testassignment)
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map,
                   minimum_points=0, maximum_points=19, grade='F')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map,
                   minimum_points=20, maximum_points=39, grade='E')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map,
                   minimum_points=40, maximum_points=59, grade='D')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map,
                   minimum_points=60, maximum_points=79, grade='C')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map,
                   minimum_points=80, maximum_points=89, grade='B')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map,
                   minimum_points=90, maximum_points=100, grade='A')
        test_feedbackset = group_baker.feedbackset_first_attempt_published(
            group__parentnode=testassignment, deadline_datetime=timezone.now(),
            grading_published_datetime=timezone.now(), grading_points=60)
        student = baker.make('core.Candidate', assignment_group=test_feedbackset.group)
        baker.make('devilry_account.UserEmail', user=student.relatedstudent.user, email='student@example.com')
        feedback_email.send_feedback_email(
            assignment=test_feedbackset.group.parentnode,
            feedback_sets=[test_feedbackset],
            domain_url_start='http://www.example.com/',
            feedback_type='feedback_created')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_feedback_result').alltext_normalized,
            'Result: C ( passed )')

    def test_send_feedback_email_body_corrected_datetime(self):
        test_feedbackset = self.__setup_feedback_set(grading_published_datetime=datetime.utcnow())
        feedback_email.send_feedback_email(
            assignment=test_feedbackset.group.parentnode,
            feedback_sets=[test_feedbackset],
            domain_url_start='http://www.example.com/',
            feedback_type='feedback_created')
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_feedback_corrected_datetime').alltext_normalized,
            'Corrected datetime: {}'.format(
                defaultfilters.date(test_feedbackset.grading_published_datetime, 'DATETIME_FORMAT')))

    def test_send_feedback_email_body_deadline_datetime(self):
        test_feedbackset = self.__setup_feedback_set(deadline_datetime=datetime.utcnow())
        feedback_email.send_feedback_email(
            assignment=test_feedbackset.group.parentnode,
            feedback_sets=[test_feedbackset],
            domain_url_start='http://www.example.com/',
            feedback_type='feedback_created')
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_feedback_deadline_datetime').alltext_normalized,
            'Deadline datetime: {}'.format(
                defaultfilters.date(test_feedbackset.deadline_datetime, 'DATETIME_FORMAT')))

    def test_send_feedback_email_body_assignment(self):
        test_feedbackset = self.__setup_feedback_set()
        feedback_email.send_feedback_email(
            assignment=test_feedbackset.group.parentnode,
            feedback_sets=[test_feedbackset],
            domain_url_start='http://www.example.com/',
            feedback_type='feedback_created')
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_feedback_assignment').alltext_normalized,
            'Assignment: {}'.format(test_feedbackset.group.parentnode.long_name))

    def test_send_feedback_email_body_subject(self):
        test_feedbackset = self.__setup_feedback_set()
        feedback_email.send_feedback_email(
            assignment=test_feedbackset.group.parentnode,
            feedback_sets=[test_feedbackset],
            domain_url_start='http://www.example.com/',
            feedback_type='feedback_created')
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_feedback_subject').alltext_normalized,
            'Subject: {}'.format(test_feedbackset.group.parentnode.parentnode.parentnode.long_name))

    def test_send_feedback_email_body_link(self):
        test_feedbackset = self.__setup_feedback_set()
        feedback_email.send_feedback_email(
            assignment=test_feedbackset.group.parentnode,
            feedback_sets=[test_feedbackset],
            domain_url_start='http://www.example.com/',
            feedback_type='feedback_created')
        feedback_link = 'http://www.example.com/devilry_group/student/{}/feedbackfeed/'.format(
            test_feedbackset.group.id)
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one('.devilry_email_feedback_detail_text').alltext_normalized,
            'See the delivery feed for more details:')
        self.assertEqual(
            htmls.S(mail.outbox[0].message().as_string()).one(
                '.devilry_email_feedback_detail_url').alltext_normalized,
            feedback_link)

    def test_send_feedback_edited_email_subject(self):
        test_feedbackset = self.__setup_feedback_set()
        feedback_email.bulk_send_feedback_edited_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] Feedback updated for {}'.format(test_feedbackset.group.parentnode.long_name))

    def test_send_feedback_created_email_subject(self):
        test_feedbackset = self.__setup_feedback_set()
        feedback_email.bulk_send_feedback_created_email(
            assignment_id=test_feedbackset.group.parentnode_id,
            feedbackset_id_list=[test_feedbackset.id],
            domain_url_start='http://www.example.com/')
        self.assertEqual(
            mail.outbox[0].subject,
            '[Devilry] Feedback for {}'.format(test_feedbackset.group.parentnode.long_name))
