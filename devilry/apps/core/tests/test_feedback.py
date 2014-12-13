from datetime import datetime, timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.corebuilder import DeliveryBuilder
from devilry.apps.core.models import StaticFeedback
from devilry.apps.core.testhelper import TestHelper

class TestStaticFeedback(TestCase):

    def setUp(self):
        DeliveryBuilder.set_memory_deliverystore()
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        self.testuser = UserBuilder('testuser').user

    def test_save_groupclose(self):
        # Setup
        groupbuilder = self.assignment1builder.add_group()
        delivery = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1).delivery
        feedback = StaticFeedback(
            delivery=delivery,
            points=10,
            grade='A',
            saved_by=self.testuser,
            is_passing_grade=True
        )

        # Test
        self.assertTrue(groupbuilder.group.is_open)
        feedback.save()
        groupbuilder.reload_from_db()
        self.assertFalse(groupbuilder.group.is_open)

    def test_save_groupclose_False(self):
        # Setup
        groupbuilder = self.assignment1builder.add_group()
        delivery = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1).delivery
        feedback = StaticFeedback(
            delivery=delivery,
            points=10,
            grade='A',
            saved_by=self.testuser,
            is_passing_grade=True
        )

        # Test
        self.assertTrue(groupbuilder.group.is_open)
        feedback.save(autoupdate_related_models=False)
        groupbuilder.reload_from_db()
        self.assertTrue(groupbuilder.group.is_open)


    def test_save_autoset_as_active_feedback_on_group(self):
        # Setup
        groupbuilder = self.assignment1builder.add_group()
        delivery = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1).delivery
        feedback = StaticFeedback(
            delivery=delivery,
            points=10,
            grade='A',
            saved_by=self.testuser,
            is_passing_grade=True
        )

        # Test
        self.assertIsNone(groupbuilder.group.feedback)
        feedback.save()
        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.feedback, feedback)

    def test_save_autoset_as_active_feedback_on_group_False(self):
        # Setup
        groupbuilder = self.assignment1builder.add_group()
        delivery = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1).delivery
        feedback = StaticFeedback(
            delivery=delivery,
            points=10,
            grade='A',
            saved_by=self.testuser,
            is_passing_grade=True
        )

        # Test
        self.assertIsNone(groupbuilder.group.feedback)
        feedback.save(autoupdate_related_models=False)
        groupbuilder.reload_from_db()
        self.assertIsNone(groupbuilder.group.feedback)


    def test_save_autoset_as_last_feedback_on_delivery(self):
        # Setup
        deliverybuilder = self.assignment1builder.add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        feedback = StaticFeedback(
            delivery=deliverybuilder.delivery,
            points=10,
            grade='A',
            saved_by=self.testuser,
            is_passing_grade=True
        )

        # Test
        self.assertIsNone(deliverybuilder.delivery.last_feedback)
        feedback.save()
        deliverybuilder.reload_from_db()
        self.assertEquals(deliverybuilder.delivery.last_feedback, feedback)

    def test_save_autoset_as_last_feedback_on_delivery_False(self):
        # Setup
        deliverybuilder = self.assignment1builder.add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        feedback = StaticFeedback(
            delivery=deliverybuilder.delivery,
            points=10,
            grade='A',
            saved_by=self.testuser,
            is_passing_grade=True
        )

        # Test
        self.assertIsNone(deliverybuilder.delivery.last_feedback)
        feedback.save(autoupdate_related_models=False)
        deliverybuilder.reload_from_db()
        self.assertIsNone(deliverybuilder.delivery.last_feedback)

    def test_from_points(self):
        self.assignment1builder.update(
            points_to_grade_mapper='raw-points',
            passing_grade_min_points=4,
            max_points=10)
        deliverybuilder = self.assignment1builder.add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        feedback = StaticFeedback.from_points(
            assignment=self.assignment1builder.assignment,
            points=5)
        self.assertEquals(feedback.grade, '5/10')
        self.assertEquals(feedback.points, 5)
        self.assertTrue(feedback.is_passing_grade)

    def test_clean_over_max_points(self):
        self.assignment1builder.update(
            points_to_grade_mapper='raw-points',
            passing_grade_min_points=4,
            max_points=19)
        deliverybuilder = self.assignment1builder.add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        with self.assertRaisesRegexp(ValidationError,
                '.*You are not allowed to give more than 19 points on this assignment.*'):
            feedback = StaticFeedback.from_points(
                assignment=self.assignment1builder.assignment,
                points=20)


class TestStaticFeedbackOld(TestCase, TestHelper):
    """
    WARNING: Old tests for StaticFeedback using TestHelper. We should
    NOT add new tests here, and the tests should be updated and
    moved to TestStaticFeedback if we update any of the tested 
    methods, or need to add more tests.
    """
    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=[
                          "period1:admin(teacher1):begins(-1):ends(5)",
                          "old_period:begins(-2):ends(1)"],
                 assignments=["assignment1"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                   "g2:candidate(student2):examiner(examiner2)"],
                 deadlines=['d1'])
        # file and verdict
        self.goodFile = {"good.py": "print awesome"}
        self.okVerdict = {"grade": "C", "points": 1, "is_passing_grade": True}

        self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        self.add_delivery("inf1100.old_period.assignment1.g1", self.goodFile)

    def test_where_is_candidate(self):
        self.assertEquals(StaticFeedback.where_is_candidate(self.student1).count(), 0)
        self.add_feedback(self.inf1100_period1_assignment1_g1_deliveries[0], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.where_is_candidate(self.student1).count(), 1)

    def test_published_where_is_candidate(self):
        self.add_feedback(self.inf1100_period1_assignment1_g1_deliveries[0], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, active=False).count(), 0)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, old=False).count(), 1)

        # Feedback on old period
        self.add_feedback(self.inf1100_old_period_assignment1_g1_deliveries[0], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1).count(), 2)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, active=False).count(), 1)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, old=False).count(), 1)

        # Set publishing time to future for period1.assignment1
        self.inf1100_period1_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_period1_assignment1.save()
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1).count(), 1)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, active=False).count(), 1)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, old=False).count(), 0)

    def test_where_is_examiner(self):
        self.assertEquals(StaticFeedback.where_is_examiner(self.examiner1).count(), 0)
        self.add_feedback(self.inf1100_period1_assignment1_g1_deliveries[0], verdict=self.okVerdict)
        self.add_feedback(self.inf1100_period1_assignment1_g1_deliveries[1], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.where_is_examiner(self.examiner1).count(), 2)

        # Create feedback on different assignmentgroup
        self.add_to_path('uio.ifi;inf1100.period1.assignment2.group1:candidate(student2):examiner(examiner1).d1')
        self.add_delivery("inf1100.period1.assignment2.group1", self.goodFile)
        self.add_feedback(self.inf1100_period1_assignment2_group1_deliveries[0], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.where_is_examiner(self.examiner1).count(), 3)

    def test_published_where_is_examiner(self):
        self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 0)
        self.add_feedback(self.inf1100_period1_assignment1_g2_deliveries[0], verdict=self.okVerdict)
        self.add_feedback(self.inf1100_period1_assignment1_g2_deliveries[1], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 2)

        # Add to old period
        self.add_delivery("inf1100.old_period.assignment1.g2", self.goodFile)
        self.add_delivery("inf1100.old_period.assignment1.g2", self.goodFile)
        self.add_feedback(self.inf1100_old_period_assignment1_g2_deliveries[0], verdict=self.okVerdict)
        self.add_feedback(self.inf1100_old_period_assignment1_g2_deliveries[1], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 4)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, active=False).count(), 2)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, old=False).count(), 2)

        # Create assignment2 with delivery and feedback for examiner2
        self.add_to_path('uio.ifi;inf1100.period1.assignment2.group1:candidate(student2):examiner(examiner2).d1')
        d = self.add_delivery("inf1100.period1.assignment2.group1", self.goodFile)
        self.add_feedback(d, verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 5)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, active=False).count(), 2)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, old=False).count(), 3)

        # Set publishing time to future for period1.assignment1
        self.inf1100_period1_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_period1_assignment1.save()
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 3)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, active=False).count(), 2)

        # Set publishing time to future old_period.assignment1
        self.inf1100_old_period_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_old_period_assignment1.save()
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 1)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, active=False).count(), 0)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, old=False).count(), 1)


