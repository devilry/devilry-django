import unittest
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone
from ievv_opensource.ievv_batchframework.models import BatchOperation
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.apps.core.models import Delivery
from devilry.apps.core.models import deliverytypes, Assignment, RelatedStudent
from devilry.apps.core.models.assignment_group import GroupPopNotCandiateError
from devilry.apps.core.models.assignment_group import GroupPopToFewCandiatesError
from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_group.models import FeedbackSet
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder


class TestAssignmentGroup(TestCase):
    """
    Test AssignmentGroup using the next generation less coupled testing frameworks.
    """
    def test_anonymous_displayname_empty(self):
        testgroup = mommy.make('core.AssignmentGroup')
        self.assertEquals(
            u'no students in group'.format(testgroup.id),
            testgroup.get_anonymous_displayname())

    def test_anonymous_displayname(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='test')
        self.assertEquals(
            u'test'.format(testgroup.id),
            testgroup.get_anonymous_displayname())

    def test_short_displayname_empty(self):
        testgroup = mommy.make('core.AssignmentGroup')
        self.assertEquals(
            u'group#{} - no students in group'.format(testgroup.id),
            testgroup.short_displayname)

    def test_short_displayname_empty_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertEquals(
            u'no students in group'.format(testgroup.id),
            testgroup.short_displayname)

    def test_short_displayname_students(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='studenta')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='studentb')
        self.assertEquals({'studenta', 'studentb'}, set(testgroup.short_displayname.split(', ')))

    def test_short_displayname_anonymous_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='aa')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='bb',)
        self.assertEquals({'aa', 'bb'}, set(testgroup.short_displayname.split(', ')))

    def test_short_displayname_named(self):
        testgroup = mommy.make('core.AssignmentGroup', name='My group')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='ignored')
        self.assertEquals('My group', testgroup.short_displayname)

    def test_short_displayname_named_empty(self):
        testgroup = mommy.make('core.AssignmentGroup', name='My group')
        self.assertEquals(
            u'group#{} - no students in group'.format(testgroup.id),
            testgroup.short_displayname)

    def test_long_displayname_empty(self):
        testgroup = mommy.make('core.AssignmentGroup')
        self.assertEquals(
            u'group#{} - no students in group'.format(testgroup.id),
            testgroup.long_displayname)

    def test_long_displayname_empty_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertEquals(
            u'no students in group',
            testgroup.long_displayname)

    def test_long_displayname_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__fullname=u'Student \u00E5')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='studentb')
        self.assertEquals({u'Student \u00E5', u'studentb'}, set(testgroup.long_displayname.split(u', ')))

    def test_long_displayname_anonymous_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='aa')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='bb',)
        self.assertEquals({'aa', 'bb'}, set(testgroup.long_displayname.split(', ')))

    def test_long_displayname_named(self):
        testgroup = mommy.make('core.AssignmentGroup', name='My group')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__fullname=u'Student \u00E5')
        self.assertEquals(u'My group (Student \u00E5)', testgroup.long_displayname)

    def test_long_displayname_named_empty(self):
        testgroup = mommy.make('core.AssignmentGroup', name='My group')
        self.assertEquals(
            u'My group (group#{} - no students in group)'.format(testgroup.id),
            testgroup.long_displayname)

    def test_close_groups(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1builder = assignmentbuilder.add_group()
        group2builder = assignmentbuilder.add_group()
        group3builder = assignmentbuilder.add_group()
        for groupbuilder in (group1builder, group2builder, group3builder):
            self.assertTrue(groupbuilder.group.is_open)
            self.assertEquals(groupbuilder.group.delivery_status, 'no-deadlines')
        AssignmentGroup.objects.filter(id__in=(group1builder.group.id, group2builder.group.id))\
            .close_groups()
        group1builder.reload_from_db()
        group2builder.reload_from_db()
        group3builder.reload_from_db()
        self.assertFalse(group1builder.group.is_open)
        self.assertFalse(group2builder.group.is_open)
        self.assertTrue(group3builder.group.is_open)
        self.assertEquals(group1builder.group.delivery_status, 'closed-without-feedback')
        self.assertEquals(group2builder.group.delivery_status, 'closed-without-feedback')
        self.assertEquals(group3builder.group.delivery_status, 'no-deadlines')

    def test_close_groups_queryset_vs_manual(self):
        # Checks that AssignmentGroup.objects.close_groups() works the same as closing and calling save()
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1builder = assignmentbuilder.add_group()
        group2builder = assignmentbuilder.add_group()
        AssignmentGroup.objects.filter(id=group1builder.group.id).close_groups()
        group2builder.group.is_open = False
        group2builder.group.save()
        group1builder.reload_from_db()
        group2builder.reload_from_db()
        self.assertFalse(group1builder.group.is_open)
        self.assertFalse(group2builder.group.is_open)
        self.assertEquals(group1builder.group.delivery_status, 'closed-without-feedback')
        self.assertEquals(group2builder.group.delivery_status, 'closed-without-feedback')

    def test_add_nonelectronic_delivery(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1builder = assignmentbuilder.add_group()
        group1builder.add_deadline_in_x_weeks(weeks=1)
        AssignmentGroup.objects.filter(id=group1builder.group.id).add_nonelectronic_delivery()
        group1builder.reload_from_db()

        last_delivery = Delivery.objects.get(deadline__assignment_group=group1builder.group)
        self.assertEquals(last_delivery.delivery_type, deliverytypes.NON_ELECTRONIC)
        self.assertTrue(last_delivery.successful)

    def test_should_ask_if_examiner_want_to_give_another_chance_nonelectronic(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', delivery_types=deliverytypes.NON_ELECTRONIC)\
            .add_group().group
        self.assertFalse(group.should_ask_if_examiner_want_to_give_another_chance)

    def test_should_ask_if_examiner_want_to_give_another_chance_closed_without_feedback(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', delivery_types=deliverytypes.ELECTRONIC)\
            .add_group()
        self.assertFalse(groupbuilder.group.should_ask_if_examiner_want_to_give_another_chance)
        groupbuilder.update(is_open=False)
        self.assertTrue(groupbuilder.group.should_ask_if_examiner_want_to_give_another_chance)

    def test_should_ask_if_examiner_want_to_give_another_chance_failed_grade(self):
        testuser = UserBuilder('testuser').user
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', delivery_types=deliverytypes.ELECTRONIC)
        group1builder = assignmentbuilder.add_group()
        group2builder = assignmentbuilder.add_group()
        group1builder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_passed_feedback(saved_by=testuser)
        group2builder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_failed_feedback(saved_by=testuser)

        self.assertFalse(group1builder.group.should_ask_if_examiner_want_to_give_another_chance)
        self.assertTrue(group2builder.group.should_ask_if_examiner_want_to_give_another_chance)

    def test_not_missing_expected_delivery_nonelectronic(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', delivery_types=deliverytypes.NON_ELECTRONIC)\
            .add_group().group
        self.assertFalse(group.missing_expected_delivery)

    def test_not_missing_expected_delivery_not_waiting_for_feedback(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group().group
        self.assertFalse(group.missing_expected_delivery)

    def test_missing_expected_delivery_no_deliveries(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.assertTrue(groupbuilder.group.missing_expected_delivery)

    def test_missing_expected_delivery_delivery_not_on_last_deadline(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        groupbuilder.add_deadline_x_weeks_ago(weeks=2).add_delivery()
        groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.assertTrue(groupbuilder.group.missing_expected_delivery)

    def test_not_missing_expected_delivery_delivery_on_last_deadline(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        groupbuilder.add_deadline_x_weeks_ago(weeks=2)
        groupbuilder.add_deadline_x_weeks_ago(weeks=1).add_delivery()
        self.assertFalse(groupbuilder.group.missing_expected_delivery)

    def test_annotate_with_last_deadline_datetime(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')

        group1builder = assignmentbuilder.add_group()
        group1builder.add_deadline_in_x_weeks(weeks=10)
        group1builder.add_deadline_in_x_weeks(weeks=2)
        group1_last_deadline = group1builder.add_deadline_in_x_weeks(weeks=20).deadline
        group1builder.add_deadline_x_weeks_ago(weeks=2)

        group2builder = assignmentbuilder.add_group()
        group2builder.add_deadline_in_x_weeks(weeks=30)

        annotated_group1 = AssignmentGroup.objects.filter()\
            .annotate_with_last_deadline_datetime().first()
        self.assertEqual(annotated_group1.last_deadline_datetime, group1_last_deadline.deadline)

    def test_annotate_with_last_deadline_pk(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')

        group1builder = assignmentbuilder.add_group()
        group1builder.add_deadline_in_x_weeks(weeks=10)
        group1builder.add_deadline_in_x_weeks(weeks=2)
        group1_last_deadline = group1builder.add_deadline_in_x_weeks(weeks=20).deadline
        group1builder.add_deadline_x_weeks_ago(weeks=2)

        group2builder = assignmentbuilder.add_group()
        group2builder.add_deadline_in_x_weeks(weeks=30)

        annotated_group1 = AssignmentGroup.objects.filter()\
            .annotate_with_last_deadline_pk().first()
        self.assertEqual(annotated_group1.last_deadline_pk, group1_last_deadline.id)

    def test_annotate_with_last_deadline_datetime_no_deadlines(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        group = AssignmentGroup.objects.filter(id=groupbuilder.group.id)\
            .annotate_with_last_deadline_datetime().first()
        self.assertEqual(group.last_deadline_datetime, None)

    def test_annotate_with_last_delivery_time_of_delivery(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')

        groupbuilder1 = assignmentbuilder.add_group(name='A')
        group1deadlinebuilder = groupbuilder1.add_deadline_in_x_weeks(weeks=1)
        group1deadlinebuilder.add_delivery_x_hours_before_deadline(hours=10)
        group1last_delivery = group1deadlinebuilder.add_delivery_x_hours_before_deadline(hours=2).delivery
        group1deadlinebuilder.add_delivery_x_hours_before_deadline(hours=3)

        groupbuilder2 = assignmentbuilder.add_group(name='B')
        group2deadlinebuilder = groupbuilder2.add_deadline_in_x_weeks(weeks=1)
        group2deadlinebuilder.add_delivery_x_hours_before_deadline(hours=10)
        group2last_delivery = group2deadlinebuilder.add_delivery_x_hours_before_deadline(hours=1).delivery

        group1, group2 = AssignmentGroup.objects.order_by('name')\
            .annotate_with_last_delivery_time_of_delivery()
        self.assertEqual(group1.last_delivery_time_of_delivery, group1last_delivery.time_of_delivery)
        self.assertEqual(group2.last_delivery_time_of_delivery, group2last_delivery.time_of_delivery)

    def test_annotate_with_last_delivery_time_of_delivery_no_deliveries(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        group = AssignmentGroup.objects.filter(id=groupbuilder.group.id)\
            .annotate_with_last_delivery_time_of_delivery().first()
        self.assertEqual(group.last_delivery_time_of_delivery, None)

    def test_annotate_with_last_delivery_id(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')

        groupbuilder1 = assignmentbuilder.add_group(name='A')
        group1deadlinebuilder = groupbuilder1.add_deadline_in_x_weeks(weeks=1)
        group1deadlinebuilder.add_delivery_x_hours_before_deadline(hours=10)
        group1last_delivery = group1deadlinebuilder.add_delivery_x_hours_before_deadline(hours=2).delivery
        group1deadlinebuilder.add_delivery_x_hours_before_deadline(hours=3)

        groupbuilder2 = assignmentbuilder.add_group(name='B')
        group2deadlinebuilder = groupbuilder2.add_deadline_in_x_weeks(weeks=1)
        group2deadlinebuilder.add_delivery_x_hours_before_deadline(hours=10)
        group2last_delivery = group2deadlinebuilder.add_delivery_x_hours_before_deadline(hours=1).delivery

        group1, group2 = AssignmentGroup.objects.order_by('name')\
            .annotate_with_last_delivery_id()
        self.assertEqual(group1.last_delivery_id, group1last_delivery.id)
        self.assertEqual(group2.last_delivery_id, group2last_delivery.id)

    def test_annotate_with_last_delivery_id_no_deliveries(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        group = AssignmentGroup.objects.filter(id=groupbuilder.group.id)\
            .annotate_with_last_delivery_id().first()
        self.assertEqual(group.last_delivery_id, None)

    def test_exclude_groups_with_deliveries_all_groups_has_deliveries(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        deadlinebuilder = groupbuilder.add_deadline_in_x_weeks(weeks=1)
        deadlinebuilder.add_delivery_x_hours_before_deadline(hours=10)
        groups = AssignmentGroup.objects.filter(id=groupbuilder.group.id)\
            .exclude_groups_with_deliveries()
        self.assertEqual(groups.count(), 0)

    def test_exclude_groups_with_deliveries(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        groups = AssignmentGroup.objects.filter(id=groupbuilder.group.id)\
            .exclude_groups_with_deliveries()
        self.assertEqual(groups.count(), 1)

    def test_annotate_with_number_of_deliveries(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        deadline1builder = groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        deadline2builder = groupbuilder.add_deadline_in_x_weeks(weeks=1)

        deadline1builder.add_delivery_x_hours_before_deadline(hours=10)
        deadline1builder.add_delivery_x_hours_before_deadline(hours=3)
        deadline2builder.add_delivery_x_hours_before_deadline(hours=2)
        group = AssignmentGroup.objects.filter(id=groupbuilder.group.id)\
            .annotate_with_number_of_deliveries().first()
        self.assertEqual(group.number_of_deliveries, 3)

    def test_annotate_with_number_of_deliveries_no_deliveries(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        group = AssignmentGroup.objects.filter(id=groupbuilder.group.id)\
            .annotate_with_number_of_deliveries().first()
        self.assertEqual(group.number_of_deliveries, 0)

    def test_filter_can_add_deliveries_before_hard_deadline(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            deadline_handling=Assignment.DEADLINEHANDLING_HARD)\
            .add_group()
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.assertEquals(AssignmentGroup.objects.filter_can_add_deliveries().count(), 1)

    def test_filter_can_add_deliveries_after_hard_deadline(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            deadline_handling=Assignment.DEADLINEHANDLING_HARD)\
            .add_group()
        groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.assertEquals(AssignmentGroup.objects.filter_can_add_deliveries().count(), 0)

    def test_filter_can_add_deliveries_not_on_nonelectronic(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            delivery_types=deliverytypes.NON_ELECTRONIC)\
            .add_group()
        groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.assertEquals(AssignmentGroup.objects.filter_can_add_deliveries().count(), 0)

    def test_filter_can_add_deliveries_before_soft_deadline(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            deadline_handling=Assignment.DEADLINEHANDLING_SOFT)\
            .add_group()
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.assertEquals(AssignmentGroup.objects.filter_can_add_deliveries().count(), 1)
        self.assertEquals(
            AssignmentGroup.objects.filter_can_add_deliveries().first(),
            groupbuilder.group)

    def test_filter_can_add_deliveries_after_soft_deadline(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            deadline_handling=Assignment.DEADLINEHANDLING_SOFT)\
            .add_group()
        groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.assertEquals(AssignmentGroup.objects.filter_can_add_deliveries().count(), 1)

    def test_filter_can_add_deliveries_has_delivery(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        self.assertEquals(AssignmentGroup.objects.filter_can_add_deliveries().count(), 1)

    def test_filter_can_add_deliveries_not_on_corrected(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_passed_A_feedback(saved_by=UserBuilder('testexaminer').user)
        self.assertEquals(AssignmentGroup.objects.filter_can_add_deliveries().count(), 0)

    def test_delete_copied_from_does_not_delete_group(self):
        group1 = mommy.make('core.AssignmentGroup')
        group2 = mommy.make('core.AssignmentGroup', copied_from=group1)
        group1.delete()
        group2 = AssignmentGroup.objects.get(id=group2.id)
        self.assertIsNone(group2.copied_from)

    def test_bulk_create_groups_creates_group(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        AssignmentGroup.objects.bulk_create_groups(created_by_user=testuser,
                                                   assignment=testassignment,
                                                   relatedstudents=[relatedstudent])
        self.assertEqual(1, AssignmentGroup.objects.count())

    def test_bulk_create_groups_returns_created_groups(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        created_groups_queryset = AssignmentGroup.objects.bulk_create_groups(
                created_by_user=testuser,
                assignment=testassignment,
                relatedstudents=[relatedstudent])
        self.assertEqual(1, created_groups_queryset.count())
        self.assertEqual(list(created_groups_queryset), [AssignmentGroup.objects.first()])

    def test_bulk_create_groups_creates_batchoperation_for_group(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        AssignmentGroup.objects.bulk_create_groups(created_by_user=testuser,
                                                   assignment=testassignment,
                                                   relatedstudents=[relatedstudent])
        self.assertEqual(1, BatchOperation.objects.count())
        created_group = AssignmentGroup.objects.first()
        created_batchoperation = BatchOperation.objects.first()
        self.assertEqual(created_batchoperation, created_group.batchoperation)

    def test_bulk_create_groups_creates_candidate(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        AssignmentGroup.objects.bulk_create_groups(created_by_user=testuser,
                                                   assignment=testassignment,
                                                   relatedstudents=[relatedstudent])
        created_group = AssignmentGroup.objects.first()
        self.assertEqual(1, created_group.candidates.count())
        created_candidate = Candidate.objects.first()
        self.assertEqual(relatedstudent, created_candidate.relatedstudent)

    def test_bulk_create_groups_creates_feedbackset(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        AssignmentGroup.objects.bulk_create_groups(created_by_user=testuser,
                                                   assignment=testassignment,
                                                   relatedstudents=[relatedstudent])
        created_group = AssignmentGroup.objects.first()
        self.assertEqual(1, created_group.feedbackset_set.count())
        created_feedbackset = FeedbackSet.objects.first()
        self.assertEqual(testuser, created_feedbackset.created_by)
        self.assertIsNone(created_feedbackset.deadline_datetime)

    def test_bulk_create_groups_multiple(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent1 = mommy.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent2 = mommy.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent3 = mommy.make('core.RelatedStudent',
                                     period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        AssignmentGroup.objects.bulk_create_groups(
                created_by_user=testuser,
                assignment=testassignment,
                relatedstudents=[relatedstudent1, relatedstudent2, relatedstudent3])
        self.assertEqual(3, AssignmentGroup.objects.count())
        self.assertEqual(3, Candidate.objects.count())
        self.assertEqual(3, FeedbackSet.objects.count())
        self.assertEqual(1, BatchOperation.objects.count())

        created_candidates = list(Candidate.objects.all())
        self.assertEqual(
                3,
                len({created_candidates[0].assignment_group,
                     created_candidates[1].assignment_group,
                     created_candidates[2].assignment_group}))

        created_feedbacksets = list(FeedbackSet.objects.all())
        self.assertEqual(
                3,
                len({created_feedbacksets[0].group,
                     created_feedbacksets[1].group,
                     created_feedbacksets[2].group}))

    def test_bulk_create_groups_num_queries(self):
        # Trigger ContentType caching so we do not get an extra lookup in the
        # assertNumQueries() statement below.
        ContentType.objects.get_for_model(Assignment)

        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=20)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        relatedstudents = list(RelatedStudent.objects.select_related('user'))
        self.assertEqual(20, len(relatedstudents))
        with self.assertNumQueries(6):
            AssignmentGroup.objects.bulk_create_groups(
                created_by_user=testuser,
                assignment=testassignment,
                relatedstudents=relatedstudents)

    def test_filter_has_passing_grade(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        passingfeecbackset = mommy.make('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        is_last_in_group=None,
                                        group__parentnode=testassignment,
                                        grading_points=1)
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   grading_published_datetime=timezone.now(),
                   grading_points=0)
        self.assertEqual(
            [passingfeecbackset.group],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_unpublished_ignored(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   group__parentnode=testassignment,
                   grading_points=1)
        self.assertEqual(
            [],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_unpublished_ignored_but_has_older_published(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   is_last_in_group=None,
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   grading_points=1)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   group=testgroup,
                   grading_points=0)
        self.assertEqual(
            [testgroup],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_correct_feedbackset_ordering1(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   group=testgroup,
                   is_last_in_group=None,
                   grading_points=0)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   is_last_in_group=None,
                   grading_points=1)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=3),
                   group=testgroup,
                   is_last_in_group=None,
                   grading_points=0)
        self.assertEqual(
            [testgroup],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_correct_feedbackset_ordering2(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   group=testgroup,
                   is_last_in_group=None,
                   grading_points=1)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   is_last_in_group=None,
                   grading_points=0)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=3),
                   group=testgroup,
                   grading_points=1)
        self.assertEqual(
            [],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_not_within_assignment(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   grading_points=1)
        self.assertEqual(
            [],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_user_is_candidate(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.AssignmentGroup')
        group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=group,
                   relatedstudent__user=testuser)
        self.assertEqual(
            [group],
            list(AssignmentGroup.objects.filter_user_is_candidate(user=testuser)))

    def test_filter_user_is_examiner(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.AssignmentGroup')
        group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=group,
                   relatedexaminer__user=testuser)
        self.assertEqual(
            [group],
            list(AssignmentGroup.objects.filter_user_is_examiner(user=testuser)))

    def test_annotate_with_number_of_groupcomments_zero(self):
        mommy.make('core.AssignmentGroup')
        self.assertEqual(
            0,
            AssignmentGroup.objects.annotate_with_number_of_groupcomments()
            .first().number_of_groupcomments)

    def test_annotate_with_number_of_groupcomments_multiple(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__is_last_in_group=None)
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup)
        self.assertEqual(
            2,
            AssignmentGroup.objects.annotate_with_number_of_groupcomments()
            .first().number_of_groupcomments)

    def test_annotate_with_number_of_imageannotationcomments_zero(self):
        mommy.make('core.AssignmentGroup')
        self.assertEqual(
            0,
            AssignmentGroup.objects.annotate_with_number_of_imageannotationcomments()
            .first().number_of_imageannotationcomments)

    def test_annotate_with_number_of_imageannotationcomments_multiple(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set__group=testgroup,
                   feedback_set__is_last_in_group=None,)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set__group=testgroup)
        self.assertEqual(
            2,
            AssignmentGroup.objects.annotate_with_number_of_imageannotationcomments()
            .first().number_of_imageannotationcomments)

    def test_annotate_with_number_of_published_feedbacksets_zero(self):
        mommy.make('core.AssignmentGroup')
        self.assertEqual(
            0,
            AssignmentGroup.objects.annotate_with_number_of_published_feedbacksets()
            .first().number_of_published_feedbacksets)

    def test_annotate_with_number_of_published_feedbacksets_multiple_feedbacksets(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   is_last_in_group=None,
                   grading_published_datetime=timezone.now())
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   is_last_in_group=None,
                   grading_published_datetime=timezone.now())
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   is_last_in_group=None,
                   grading_published_datetime=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now())
        self.assertEqual(
            3,
            AssignmentGroup.objects.annotate_with_number_of_published_feedbacksets()
            .first().number_of_published_feedbacksets)

    def test_annotate_with_number_of_published_feedbacksets_multiple_groups(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup1,
                   is_last_in_group=None,
                   grading_published_datetime=timezone.now())
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup1,
                   is_last_in_group=None,
                   grading_published_datetime=timezone.now())
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup2,
                   is_last_in_group=None,
                   grading_published_datetime=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup2,
                   grading_published_datetime=timezone.now())
        queryset = AssignmentGroup.objects.annotate_with_number_of_published_feedbacksets()\
            .order_by('number_of_published_feedbacksets')
        self.assertEqual(testgroup2, queryset[0])
        self.assertEqual(1, queryset[0].number_of_published_feedbacksets)
        self.assertEqual(testgroup1, queryset[1])
        self.assertEqual(2, queryset[1].number_of_published_feedbacksets)

    def test_filter_with_published_feedback_or_comments(self):
        testgroup_with_published_feedback = mommy.make('core.AssignmentGroup')
        testgroup_with_unpublished_feedback = mommy.make('core.AssignmentGroup')
        testgroup_with_groupcomment = mommy.make('core.AssignmentGroup')
        testgroup_with_imageannotationcomment = mommy.make('core.AssignmentGroup')
        mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup_with_published_feedback,
                   is_last_in_group=None,
                   grading_published_datetime=timezone.now())
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup_with_unpublished_feedback,
                   is_last_in_group=None,
                   grading_published_datetime=None)
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup_with_groupcomment)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set__group=testgroup_with_imageannotationcomment)
        queryset = AssignmentGroup.objects.filter_with_published_feedback_or_comments()
        self.assertEqual(
            {testgroup_with_published_feedback,
             testgroup_with_groupcomment,
             testgroup_with_imageannotationcomment},
            set(queryset))


@unittest.skip('Must be updated for new FeedbackSet structure')
class TestAssignmentGroupSplit(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p1"],
                            assignments=['a1'])

    def _create_testdata(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1,student2,student3)'
                                    ':examiner(examiner1,examiner2,examiner3)')
        self.testhelper.sub_p1_a1.max_points = 100
        self.testhelper.sub_p1_a1.save()

        # Add d1 and deliveries
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(1)')
        self.testhelper.add_delivery("sub.p1.a1.g1", {"firsttry.py": "print first"},
                                     time_of_delivery=datetime(2002, 1, 1))
        delivery2 = self.testhelper.add_delivery("sub.p1.a1.g1", {"secondtry.py": "print second"},
                                                 time_of_delivery=-1)  # days after deadline
        self.testhelper.add_feedback(delivery=delivery2,
                                     verdict={'grade': 'F', 'points': 10, 'is_passing_grade': False},
                                     rendered_view='Bad',
                                     timestamp=datetime(2005, 1, 1))

        # Add d2 and deliveries
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d2:ends(4)')
        delivery3 = self.testhelper.add_delivery("sub.p1.a1.g1", {"thirdtry.py": "print third"},
                                                 time_of_delivery=-1)  # days after deadline
        self.testhelper.add_feedback(delivery=delivery3,
                                     verdict={'grade': 'C', 'points': 40, 'is_passing_grade': True},
                                     rendered_view='Better',
                                     timestamp=datetime(2010, 1, 1))

        # Set attributes and tags
        g1 = self.testhelper.sub_p1_a1_g1
        g1.name = 'Stuff'
        g1.is_open = True
        g1.save()
        g1.tags.create(tag='a')
        g1.tags.create(tag='b')

    def test_copy_all_except_candidates(self):
        self._create_testdata()
        g1 = self.testhelper.sub_p1_a1_g1
        g1copy = g1.copy_all_except_candidates()
        g1copy = self.testhelper.reload_from_db(g1copy)

        # Basics
        self.assertEquals(g1copy.name, 'Stuff')
        self.assertTrue(g1copy.is_open)
        self.assertEquals(g1copy.candidates.count(), 0)

        # Tags
        self.assertEquals(g1copy.tags.count(), 2)
        tags = [t.tag for t in g1copy.tags.all()]
        self.assertEquals(set(tags), {'a', 'b'})

        # Examiners
        self.assertEquals(g1copy.examiners.count(), 3)
        examiner_usernames = [e.user.shortname for e in g1copy.examiners.all()]
        examiner_usernames.sort()
        self.assertEquals(examiner_usernames, ['examiner1', 'examiner2', 'examiner3'])

        # Deliveries
        deliveries = Delivery.objects.filter(deadline__assignment_group=g1).order_by('time_of_delivery')
        copydeliveries = Delivery.objects.filter(deadline__assignment_group=g1copy).order_by('time_of_delivery')
        self.assertEquals(len(deliveries), len(copydeliveries))
        self.assertEquals(len(deliveries), 3)
        for delivery, deliverycopy in zip(deliveries, copydeliveries):
            self.assertEquals(delivery.delivery_type, deliverycopy.delivery_type)
            self.assertEquals(delivery.time_of_delivery, deliverycopy.time_of_delivery)
            self.assertEquals(delivery.number, deliverycopy.number)
            self.assertEquals(delivery.delivered_by, deliverycopy.delivered_by)
            self.assertEquals(delivery.deadline.deadline, deliverycopy.deadline.deadline)
            self.assertEquals(delivery.delivered_by, deliverycopy.delivered_by)
            self.assertEquals(delivery.alias_delivery, deliverycopy.alias_delivery)

        # Active feedback
        self.assertEquals(g1copy.feedback.grade, 'C')
        self.assertEquals(g1copy.feedback.save_timestamp, datetime(2010, 1, 1))
        self.assertEquals(g1copy.feedback.rendered_view, 'Better')
        self.assertEquals(g1copy.feedback.points, 40)

        self.assertEquals(
            Delivery.objects.filter(deadline__assignment_group=g1copy).first().filemetas.first().filename,
            'thirdtry.py')

    def test_pop_candidate(self):
        self._create_testdata()
        g1 = self.testhelper.sub_p1_a1_g1
        self.assertEquals(g1.candidates.count(), 3)  # We check this again after popping
        candidate = g1.candidates.order_by('student__username')[1]
        g1copy = g1.pop_candidate(candidate)

        self.assertEquals(g1copy.name, 'Stuff')  # Sanity test - the tests for copying are above
        self.assertEquals(g1copy.candidates.count(), 1)
        self.assertEquals(g1.candidates.count(), 2)
        self.assertEquals(candidate.student.shortname, 'student2')
        self.assertEquals(g1copy.candidates.all()[0], candidate)

    def test_pop_candidate_not_candidate(self):
        self._create_testdata()
        self.testhelper.add_to_path('uni;sub.p1.a2.other:candidate(student10)')
        g1 = self.testhelper.sub_p1_a1_g1
        other = self.testhelper.sub_p1_a2_other
        candidate = other.candidates.all()[0]
        with self.assertRaises(GroupPopNotCandiateError):
            g1.pop_candidate(candidate)

    def test_pop_candidate_to_few_candidates(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        g1 = self.testhelper.sub_p1_a1_g1
        candidate = g1.candidates.all()[0]
        with self.assertRaises(GroupPopToFewCandiatesError):
            g1.pop_candidate(candidate)

    def _create_mergetestdata(self):
        self._create_testdata()
        source = self.testhelper.sub_p1_a1_g1

        self.testhelper.add_to_path('uni;sub.p1.a1.target:candidate(dewey):examiner(donald)')

        # Add d1 and deliveries. d1 matches d1 in g1 (the source)
        self.testhelper.add_to_path('uni;sub.p1.a1.target.d1:ends(1)')
        self.testhelper.add_delivery("sub.p1.a1.target", {"a.py": "print a"},
                                     time_of_delivery=1)  # days after deadline

        # Add d2 and deliveries
        self.testhelper.add_to_path('uni;sub.p1.a1.target.d2:ends(11)')
        delivery = self.testhelper.add_delivery("sub.p1.a1.target", {"b.py": "print b"},
                                                time_of_delivery=-1)  # days after deadline

        # Create a delivery in g1 that is copy of one in target
        delivery.copy(self.testhelper.sub_p1_a1_g1_d2)

        # Double check the important values before the merge
        self.assertEquals(self.testhelper.sub_p1_a1_g1_d1.deadline,
                          self.testhelper.sub_p1_a1_target_d1.deadline)
        self.assertNotEquals(self.testhelper.sub_p1_a1_g1_d2.deadline,
                             self.testhelper.sub_p1_a1_target_d2.deadline)
        target = self.testhelper.sub_p1_a1_target
        self.assertEquals(source.deadlines.count(), 2)
        self.assertEquals(target.deadlines.count(), 2)
        self.assertEquals(self.testhelper.sub_p1_a1_g1_d1.deliveries.count(), 2)
        self.assertEquals(self.testhelper.sub_p1_a1_g1_d2.deliveries.count(), 2)
        self.assertEquals(self.testhelper.sub_p1_a1_target_d1.deliveries.count(), 1)
        self.assertEquals(self.testhelper.sub_p1_a1_target_d2.deliveries.count(), 1)
        return source, target

    def test_merge_into_sanity(self):
        source, target = self._create_mergetestdata()
        source.name = 'The source'
        source.is_open = False
        source.save()
        target.name = 'The target'
        source.is_open = True
        target.save()
        source.merge_into(target)

        # Source has been deleted?
        self.assertFalse(AssignmentGroup.objects.filter(id=source.id).exists())

        # Name or is_open unchanged?
        target = self.testhelper.reload_from_db(target)
        self.assertEquals(target.name, 'The target')
        self.assertEquals(target.is_open, True)

    def test_merge_into_last_delivery(self):
        source, target = self._create_mergetestdata()
        source.merge_into(target)
        target = self.testhelper.reload_from_db(target)
        self.assertEquals(
            Delivery.objects.filter(deadline__assignment_group=target).first().filemetas.first().filename,
            'b.py')

    def test_merge_into_candidates(self):
        source, target = self._create_mergetestdata()
        source.merge_into(target)
        self.assertEquals(target.examiners.count(), 4)
        self.assertEquals(set([e.user.shortname for e in target.examiners.all()]),
                          {'donald', 'examiner1', 'examiner2', 'examiner3'})

    def test_merge_into_examiners(self):
        source, target = self._create_mergetestdata()
        source.merge_into(target)
        self.assertEquals(target.candidates.count(), 4)
        self.assertEquals(set([e.student.shortname for e in target.candidates.all()]),
                          {'dewey', 'student1', 'student2', 'student3'})

    def test_merge_into_deadlines(self):
        source, target = self._create_mergetestdata()
        deadline1 = self.testhelper.sub_p1_a1_g1_d1.deadline
        deadline2 = self.testhelper.sub_p1_a1_g1_d2.deadline
        deadline3 = self.testhelper.sub_p1_a1_target_d2.deadline

        # A control delivery that we use to make sure timestamps are not messed with
        control_delivery = self.testhelper.sub_p1_a1_g1_d1.deliveries.order_by('time_of_delivery')[0]
        control_delivery_id = control_delivery.id
        self.assertEquals(control_delivery.time_of_delivery, datetime(2002, 1, 1))

        source.merge_into(target)
        deadlines = target.deadlines.order_by('deadline')
        self.assertEquals(len(deadlines), 3)
        self.assertEquals(deadlines[0].deadline, deadline1)
        self.assertEquals(deadlines[1].deadline, deadline2)
        self.assertEquals(deadlines[2].deadline, deadline3)

        self.assertEquals(deadlines[0].deliveries.count(), 3)  # d1 from both have been merged
        self.assertEquals(deadlines[1].deliveries.count(), 1)  # g1(source) d2
        self.assertEquals(deadlines[2].deliveries.count(), 1)  # target d2

        control_delivery = Delivery.objects.get(deadline__assignment_group=target,
                                                id=control_delivery_id)
        self.assertEquals(control_delivery.time_of_delivery, datetime(2002, 1, 1))

    def test_merge_into_active_feedback(self):
        source, target = self._create_mergetestdata()
        source.merge_into(target)
        self.assertEquals(target.feedback.grade, 'C')
        self.assertEquals(target.feedback.save_timestamp, datetime(2010, 1, 1))
        self.assertEquals(target.feedback.rendered_view, 'Better')
        self.assertEquals(target.feedback.points, 40)

    def test_merge_into_active_feedback_target(self):
        source, target = self._create_mergetestdata()

        # Create the feedack that should become "active feedback" after the merge
        delivery = self.testhelper.add_delivery(target, {"good.py": "print good"},
                                                time_of_delivery=2)  # days after deadline
        self.testhelper.add_feedback(delivery=delivery,
                                     verdict={'grade': 'A', 'points': 100, 'is_passing_grade': True},
                                     rendered_view='Good',
                                     timestamp=datetime(2011, 1, 1))

        source.merge_into(target)
        self.assertEquals(target.feedback.grade, 'A')
        self.assertEquals(target.feedback.save_timestamp, datetime(2011, 1, 1))
        self.assertEquals(target.feedback.rendered_view, 'Good')
        self.assertEquals(target.feedback.points, 100)

    def test_merge_into_delivery_numbers(self):
        source, target = self._create_mergetestdata()

        def get_deliveries_ordered_by_timestamp(group):
            return Delivery.objects.filter(deadline__assignment_group=group).order_by('time_of_delivery')
        for delivery in get_deliveries_ordered_by_timestamp(source):
            delivery.number = 0
            delivery.save()

        source.merge_into(target)
        deliveries = get_deliveries_ordered_by_timestamp(target)
        self.assertEquals(deliveries[0].number, 1)
        self.assertEquals(deliveries[1].number, 2)
        self.assertEquals(deliveries[2].number, 3)

    def test_merge_into_delivery_numbers_unsuccessful(self):
        source, target = self._create_mergetestdata()

        # Make all deliveries unsuccessful with number=0
        def get_deliveries_ordered_by_timestamp(group):
            return Delivery.objects.filter(deadline__assignment_group=group).order_by('time_of_delivery')

        def set_all_unsuccessful(group):
            for unsuccessful_delivery in get_deliveries_ordered_by_timestamp(group):
                unsuccessful_delivery.number = 0
                unsuccessful_delivery.successful = False
                unsuccessful_delivery.save()

        set_all_unsuccessful(source)
        set_all_unsuccessful(target)

        # Make a single delivery successful, and set its timestamp so it is the oldest
        deliveries = get_deliveries_ordered_by_timestamp(source)
        delivery = deliveries[0]
        delivery.number = 10
        delivery.successful = True
        delivery.time_of_delivery = datetime(2001, 1, 1)
        delivery.save()

        source.merge_into(target)
        deliveries = get_deliveries_ordered_by_timestamp(target)
        self.assertEquals(deliveries[0].time_of_delivery, datetime(2001, 1, 1))
        self.assertEquals(deliveries[0].number, 1)
        self.assertEquals(deliveries[1].number, 0)
        self.assertEquals(deliveries[2].number, 0)
        self.assertEquals(deliveries[3].number, 0)

    def test_merge_with_copy_of_in_both(self):
        for groupname in 'source', 'target':
            self.testhelper.add(
                nodes="uni",
                subjects=["sub"],
                periods=["p1"],
                assignments=['a1'],
                assignmentgroups=['{groupname}:candidate(student1):examiner(examiner1)'.format(groupname=groupname)],
                deadlines=['d1:ends(1)'])
            self.testhelper.add_delivery("sub.p1.a1.{groupname}".format(groupname=groupname),
                                         {'a.txt': "a"},
                                         time_of_delivery=datetime(2002, 1, 1))
        source = self.testhelper.sub_p1_a1_source
        target = self.testhelper.sub_p1_a1_target

        # Copy the delivery from source into target, and vica versa
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=source).count(), 1)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=target).count(), 1)
        sourcedeadline = source.deadlines.all()[0]
        targetdeadine = target.deadlines.all()[0]
        sourcedeadline.deliveries.all()[0].copy(targetdeadine)
        targetdeadine.deliveries.all()[0].copy(sourcedeadline)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=source).count(), 2)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=target).count(), 2)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=source,
                                                  copy_of__deadline__assignment_group=target).count(), 1)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=target,
                                                  copy_of__deadline__assignment_group=source).count(), 1)

        # Merge and make sure we do not get any duplicates
        # - We should only end up with 2 deliveries, since 2 of the deliveries are copies
        source.merge_into(target)
        deliveries = Delivery.objects.filter(deadline__assignment_group=target)
        self.assertEquals(len(deliveries), 2)
        self.assertEquals(deliveries[0].copy_of, None)
        self.assertEquals(deliveries[1].copy_of, None)

    def test_merge_with_copy_of_in_other(self):
        for groupname in 'source', 'target', 'other':
            self.testhelper.add(
                nodes="uni",
                subjects=["sub"],
                periods=["p1"],
                assignments=['a1'],
                assignmentgroups=['{groupname}:candidate(student1):examiner(examiner1)'.format(groupname=groupname)],
                deadlines=['d1:ends(1)'])
            self.testhelper.add_delivery("sub.p1.a1.{groupname}".format(groupname=groupname),
                                         {'a.txt': "a"},
                                         time_of_delivery=datetime(2002, 1, 1))
        source = self.testhelper.sub_p1_a1_source
        target = self.testhelper.sub_p1_a1_target
        other = self.testhelper.sub_p1_a1_other

        # Copy the delivery from source into target, and vica versa
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=source).count(), 1)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=target).count(), 1)
        for group in source, target:
            deadline = group.deadlines.all()[0]
            other.deadlines.all()[0].deliveries.all()[0].copy(deadline)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=source).count(), 2)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=target).count(), 2)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=source,
                                                  copy_of__deadline__assignment_group=target).count(), 0)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=target,
                                                  copy_of__deadline__assignment_group=source).count(), 0)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=source,
                                                  copy_of__deadline__assignment_group=other).count(), 1)
        self.assertEquals(Delivery.objects.filter(deadline__assignment_group=target,
                                                  copy_of__deadline__assignment_group=other).count(), 1)

        # Merge and make sure we do not get any duplicates
        # - We should only end up with 3 deliveries, one from source, one from
        #   target, and one copy from other (both have the same copy from
        #   other, so we should not get any duplicates)
        source.merge_into(target)
        deliveries = Delivery.objects.filter(deadline__assignment_group=target)
        self.assertEquals(deliveries.filter(copy_of__isnull=True).count(), 2)
        self.assertEquals(deliveries.filter(copy_of__isnull=False).count(), 1)
        self.assertEquals(len(deliveries), 3)

    def test_merge_many_groups(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.a:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.b:candidate(student2):examiner(examiner2)')
        self.testhelper.add_to_path('uni;sub.p1.a1.c:candidate(student1,student3):examiner(examiner1,examiner3)')
        for groupname in 'a', 'b', 'c':
            self.testhelper.add(nodes="uni",
                                subjects=["sub"],
                                periods=["p1"],
                                assignments=['a1'],
                                assignmentgroups=[groupname],
                                deadlines=['d1:ends(1)'])
            self.testhelper.add_delivery("sub.p1.a1.{groupname}".format(**vars()),
                                         {groupname: groupname},
                                         time_of_delivery=datetime(2002, 1, 1))
        a = self.testhelper.sub_p1_a1_a
        b = self.testhelper.sub_p1_a1_b
        c = self.testhelper.sub_p1_a1_c

        AssignmentGroup.merge_many_groups([a, b], c)
        self.assertFalse(AssignmentGroup.objects.filter(id=a.id).exists())
        self.assertFalse(AssignmentGroup.objects.filter(id=b.id).exists())
        self.assertTrue(AssignmentGroup.objects.filter(id=c.id).exists())
        c = self.testhelper.reload_from_db(self.testhelper.sub_p1_a1_c)
        candidates = [cand.student.shortname for cand in c.candidates.all()]
        self.assertEquals(len(candidates), 3)
        self.assertEquals(set(candidates), {'student1', 'student2', 'student3'})

        examiners = [cand.user.shortname for cand in c.examiners.all()]
        self.assertEquals(len(examiners), 3)
        self.assertEquals(set(examiners), {'examiner1', 'examiner2', 'examiner3'})

        deadlines = c.deadlines.all()
        self.assertEquals(len(deadlines), 1)
        deliveries = deadlines[0].deliveries.all()
        self.assertEquals(len(deliveries), 3)


class TestAssignmentGroupStatus(TestCase):
    def setUp(self):
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        self.group1builder = self.assignmentbuilder.add_group()

    def test_no_deadlines(self):
        self.assertEquals(self.group1builder.group.delivery_status, 'no-deadlines')
        self.assertEquals(self.group1builder.group.get_status(), 'no-deadlines')

    def test_waiting_for_deliveries(self):
        self.group1builder.add_deadline_in_x_weeks(weeks=1)
        self.assertEquals(self.group1builder.group.delivery_status, 'waiting-for-something')
        self.assertEquals(self.group1builder.group.get_status(), 'waiting-for-deliveries')

    def test_waiting_for_feedback(self):
        self.group1builder.add_deadline_x_weeks_ago(weeks=1)
        self.assertEquals(self.group1builder.group.get_status(), 'waiting-for-feedback')

    def test_corrected(self):
        self.group1builder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_passed_feedback(saved_by=UserBuilder('testuser').user)
        self.assertEquals(self.group1builder.group.delivery_status, 'corrected')
        self.assertEquals(self.group1builder.group.get_status(), 'corrected')

    def test_closed_without_feedback(self):
        self.group1builder.update(is_open=False)
        self.assertEquals(self.group1builder.group.delivery_status, 'closed-without-feedback')
        self.assertEquals(self.group1builder.group.get_status(), 'closed-without-feedback')

    def test_non_electronic_always_waiting_for_feedback_before_deadline(self):
        self.assignmentbuilder.update(
            delivery_types=deliverytypes.NON_ELECTRONIC
        )
        self.group1builder.add_deadline_in_x_weeks(weeks=1)
        self.group1builder.reload_from_db()
        self.assertEquals(self.group1builder.group.get_status(), 'waiting-for-feedback')

    def test_non_electronic_always_waiting_for_feedback_after_deadline(self):
        self.assignmentbuilder.update(
            delivery_types=deliverytypes.NON_ELECTRONIC
        )
        self.group1builder.add_deadline_x_weeks_ago(weeks=1)
        self.group1builder.reload_from_db()
        self.assertEquals(self.group1builder.group.get_status(), 'waiting-for-feedback')


class TestAssignmentGroupManager(TestCase):
    def test_filter_waiting_for_deliveries(self):
        examiner1 = UserBuilder('examiner1').user
        week1 = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment('week1')
        group1builder = week1.add_group().add_examiners(examiner1)
        group2builder = week1.add_group().add_examiners(examiner1)
        group1builder.add_deadline_in_x_weeks(weeks=1)
        group2builder.add_deadline_x_weeks_ago(weeks=1)
        qry = AssignmentGroup.objects.filter_waiting_for_deliveries()
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], group1builder.group)

    def test_filter_waiting_for_deliveries_nonelectronic(self):
        examiner1 = UserBuilder('examiner1').user
        week1 = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment(
            'week1',
            delivery_types=deliverytypes.NON_ELECTRONIC)
        group1builder = week1.add_group().add_examiners(examiner1)
        group2builder = week1.add_group().add_examiners(examiner1)
        group1builder.add_deadline_in_x_weeks(weeks=1)
        group2builder.add_deadline_x_weeks_ago(weeks=1)
        qry = AssignmentGroup.objects.filter_waiting_for_deliveries()
        self.assertEquals(qry.count(), 0)

    def test_filter_waiting_for_feedback(self):
        examiner1 = UserBuilder('examiner1').user
        week1 = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment('week1')
        group1builder = week1.add_group().add_examiners(examiner1)
        group2builder = week1.add_group().add_examiners(examiner1)
        group1builder.add_deadline_in_x_weeks(weeks=1)
        group2builder.add_deadline_x_weeks_ago(weeks=1)
        qry = AssignmentGroup.objects.filter_waiting_for_feedback()
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], group2builder.group)

    def test_filter_waiting_for_feedback_nonelectronic(self):
        examiner1 = UserBuilder('examiner1').user
        week1 = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment(
            'week1',
            delivery_types=deliverytypes.NON_ELECTRONIC)
        group1builder = week1.add_group().add_examiners(examiner1)
        group2builder = week1.add_group().add_examiners(examiner1)
        group1builder.add_deadline_in_x_weeks(weeks=1)
        group2builder.add_deadline_x_weeks_ago(weeks=1)
        qry = AssignmentGroup.objects.filter_waiting_for_feedback()
        self.assertEquals(qry.count(), 2)

    def test_filter_waiting_for_feedback_nesting(self):
        examiner1 = UserBuilder('examiner1').user
        week1 = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment('week1')
        group1builder = week1.add_group().add_examiners(examiner1)
        group2builder = week1.add_group().add_examiners(examiner1)
        group3builder = week1.add_group()

        group1builder.add_deadline_x_weeks_ago(weeks=1)
        group2builder.add_deadline_in_x_weeks(weeks=1)
        group3builder.add_deadline_x_weeks_ago(weeks=1)

        self.assertEquals(AssignmentGroup.objects.filter_waiting_for_feedback().count(), 2)
        self.assertEquals(AssignmentGroup.objects.filter_examiner_has_access(examiner1).count(), 2)
        qry = AssignmentGroup.objects.filter_examiner_has_access(examiner1).filter_waiting_for_feedback()
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], group1builder.group)

    def test_filter_is_published(self):
        periodbuilder = SubjectBuilder.quickadd_ducku_duck1010()\
            .add_period('period1',
                        start_time=DateTimeBuilder.now().minus(days=60),
                        end_time=DateTimeBuilder.now().plus(days=60))
        group1 = periodbuilder.add_assignment('assignment1',
                                              publishing_time=DateTimeBuilder.now().minus(days=30))\
            .add_group().group
        periodbuilder.add_assignment('assignment2',
                                     publishing_time=DateTimeBuilder.now().plus(days=10))\
            .add_group()
        periodbuilder.add_assignment('assignment3',
                                     publishing_time=DateTimeBuilder.now().plus(days=50))\
            .add_group()
        qry = AssignmentGroup.objects.filter_is_published()
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], group1)

    def test_filter_student_has_access(self):
        student1 = UserBuilder('student1').user
        otherstudent = UserBuilder('otherstudent').user
        periodbuilder = SubjectBuilder.quickadd_ducku_duck1010()\
            .add_period('period1',
                        start_time=DateTimeBuilder.now().minus(days=60),
                        end_time=DateTimeBuilder.now().plus(days=60))
        group1 = periodbuilder.add_assignment('assignment1',
                                              publishing_time=DateTimeBuilder.now().minus(days=30))\
            .add_group(students=[student1]).group
        periodbuilder.add_assignment('assignment2',
                                     publishing_time=DateTimeBuilder.now().minus(days=10))\
            .add_group(students=[otherstudent])
        periodbuilder.add_assignment('assignment3',
                                     publishing_time=DateTimeBuilder.now().plus(days=50))\
            .add_group(students=[student1])
        qry = AssignmentGroup.objects.filter_student_has_access(student1)
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], group1)

    def test_filter_is_active(self):
        duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        currentgroupbuilder = duck1010builder.add_6month_active_period()\
            .add_assignment('week1').add_group()

        # Add inactive groups to make sure we get no false positives
        duck1010builder.add_6month_lastyear_period().add_assignment('week1').add_group()
        duck1010builder.add_6month_nextyear_period().add_assignment('week1').add_group()

        qry = AssignmentGroup.objects.filter_is_active()
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], currentgroupbuilder.group)

    def test_filter_examiner_has_access(self):
        examiner1 = UserBuilder('examiner1').user
        otherexaminer = UserBuilder('otherexaminer').user
        duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        activeassignmentbuilder = duck1010builder.add_6month_active_period().add_assignment('week1')
        currentgroupbuilder = activeassignmentbuilder.add_group().add_examiners(examiner1)

        # Add inactive groups and a group with another examiner to make sure we get no false positives
        duck1010builder.add_6month_lastyear_period().add_assignment('week1')\
            .add_group().add_examiners(examiner1)
        duck1010builder.add_6month_nextyear_period().add_assignment('week1')\
            .add_group().add_examiners(examiner1)
        activeassignmentbuilder.add_group().add_examiners(otherexaminer)

        qry = AssignmentGroup.objects.filter_examiner_has_access(examiner1)
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], currentgroupbuilder.group)


class TestAssignmentGroupQuerySetExtraOrdering(TestCase):
    def test_extra_annotate_with_fullname_of_first_candidate_shortnameonly(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects.extra_annotate_with_fullname_of_first_candidate().first()
        self.assertEqual('usera', annotatedgroup.fullname_of_first_candidate)

    def test_extra_annotate_with_fullname_of_first_candidate_fullname(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   relatedstudent__user__fullname='User B',
                   assignment_group=testgroup)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   relatedstudent__user__fullname='User A',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects.extra_annotate_with_fullname_of_first_candidate().first()
        self.assertEqual('user ausera', annotatedgroup.fullname_of_first_candidate)

    def test_extra_annotate_with_fullname_of_first_candidate_multiple_groups(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects.extra_annotate_with_fullname_of_first_candidate()
        self.assertEqual('usera', queryset.get(id=testgroup1.id).fullname_of_first_candidate)
        self.assertEqual('userx', queryset.get(id=testgroup2.id).fullname_of_first_candidate)

    def test_extra_order_by_fullname_of_first_candidate_ascending_shortnames(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_fullname_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_fullname_of_first_candidate_descending_shortnames(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_fullname_of_first_candidate(descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_order_by_fullname_of_first_candidate_ascending_fullnames(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='user1',
                   relatedstudent__user__fullname='BUser1',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='buser2',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='user3',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='user4',
                   relatedstudent__user__fullname='AUser4',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_fullname_of_first_candidate())
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_order_by_fullname_of_first_candidate_descending_fullnames(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='user1',
                   relatedstudent__user__fullname='BUser1',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='buser2',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='user3',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='user4',
                   relatedstudent__user__fullname='AUser4',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_fullname_of_first_candidate(descending=True))
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate_anonymousid(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup)
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects\
            .extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate().first()
        self.assertEqual('anonymousa',
                         annotatedgroup.relatedstudents_anonymous_id_of_first_candidate)

    def test_extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate_candidateid(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   relatedstudent__candidate_id='candidatex',
                   assignment_group=testgroup)
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   relatedstudent__candidate_id='candidatey',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects\
            .extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate().first()
        self.assertEqual('candidatexanonymousb',
                         annotatedgroup.relatedstudents_anonymous_id_of_first_candidate)

    def test_extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate_multiple_groups(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects\
            .extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate()
        self.assertEqual('anonymousa',
                         queryset.get(id=testgroup1.id).relatedstudents_anonymous_id_of_first_candidate)
        self.assertEqual('anonymousx',
                         queryset.get(id=testgroup2.id).relatedstudents_anonymous_id_of_first_candidate)

    def test_extra_order_by_relatedstudents_anonymous_id_of_first_candidate_ascending_anonymousids(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_relatedstudents_anonymous_id_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_relatedstudents_anonymous_id_of_first_candidate_descending_anonymousids(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_relatedstudents_anonymous_id_of_first_candidate(
            descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_order_by_relatedstudents_anonymous_id_of_first_candidate_ascending_candidateids(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__candidate_id='a',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__candidate_id='b',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__candidate_id='c',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__candidate_id='d',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_relatedstudents_anonymous_id_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_relatedstudents_anonymous_id_of_first_candidate_descending_candidateids(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__candidate_id='a',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__candidate_id='b',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__candidate_id='c',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__candidate_id='d',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_relatedstudents_anonymous_id_of_first_candidate(
            descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_annotate_with_candidates_candidate_id_of_first_candidate(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   candidate_id='candidatex',
                   assignment_group=testgroup)
        mommy.make('core.Candidate',
                   candidate_id='candidatey',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects\
            .extra_annotate_with_candidates_candidate_id_of_first_candidate().first()
        self.assertEqual('candidatex',
                         annotatedgroup.candidates_candidate_id_of_first_candidate)

    def test_extra_annotate_with_candidates_candidate_id_of_first_candidate_multiple_groups(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   candidate_id='candidateb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   candidate_id='candidatea',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   candidate_id='candidatex',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   candidate_id='candidatey',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects\
            .extra_annotate_with_candidates_candidate_id_of_first_candidate()
        self.assertEqual('candidatea',
                         queryset.get(id=testgroup1.id).candidates_candidate_id_of_first_candidate)
        self.assertEqual('candidatex',
                         queryset.get(id=testgroup2.id).candidates_candidate_id_of_first_candidate)

    def test_extra_order_by_candidates_candidate_id_of_first_candidate_ascending(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   candidate_id='a',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   candidate_id='b',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   candidate_id='c',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   candidate_id='d',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_candidates_candidate_id_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_candidates_candidate_id_of_first_candidate_descending(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   candidate_id='a',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   candidate_id='b',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   candidate_id='c',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   candidate_id='d',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_candidates_candidate_id_of_first_candidate(
            descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_annotate_with_shortname_of_first_candidate(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects.extra_annotate_with_shortname_of_first_candidate().first()
        self.assertEqual('usera', annotatedgroup.shortname_of_first_candidate)

    def test_extra_annotate_with_shortname_of_first_candidate_multiple_groups(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects.extra_annotate_with_shortname_of_first_candidate()
        self.assertEqual('usera', queryset.get(id=testgroup1.id).shortname_of_first_candidate)
        self.assertEqual('userx', queryset.get(id=testgroup2.id).shortname_of_first_candidate)

    def test_extra_order_by_shortname_of_first_candidate_ascending(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_shortname_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_shortname_of_first_candidate_descending(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_shortname_of_first_candidate(descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_annotate_with_lastname_of_first_candidate(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='userb',
                   assignment_group=testgroup)
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='usera',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects.extra_annotate_with_lastname_of_first_candidate().first()
        self.assertEqual('usera', annotatedgroup.lastname_of_first_candidate)

    def test_extra_annotate_with_lastname_of_first_candidate_multiple_groups(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='userb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='usera',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='userx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='usery',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects.extra_annotate_with_lastname_of_first_candidate()
        self.assertEqual('usera', queryset.get(id=testgroup1.id).lastname_of_first_candidate)
        self.assertEqual('userx', queryset.get(id=testgroup2.id).lastname_of_first_candidate)

    def test_extra_order_by_lastname_of_first_candidate_ascending(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='userb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='usera',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='userx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_lastname_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_lastname_of_first_candidate_descending(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='userb',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='usera',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='userx',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   relatedstudent__user__lastname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_lastname_of_first_candidate(descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])


class TestAssignmentGroupQuerySetAnnotateWithIsWaitingForFeedback(TestCase):
    def test_annotate_with_is_waiting_for_feedback_false_feedback_published(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_feedback()
        self.assertFalse(queryset.first().is_waiting_for_feedback)

    def test_annotate_with_is_waiting_for_feedback_false_deadline_not_expired(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() + timedelta(days=2),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_feedback()
        self.assertFalse(queryset.first().is_waiting_for_feedback)

    def test_annotate_with_is_waiting_for_feedback_false_deadline_not_expired_first_try(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() + timedelta(days=2))
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_feedback()
        self.assertFalse(queryset.first().is_waiting_for_feedback)

    def test_annotate_with_is_waiting_for_feedback_true_deadline_expired(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_feedback()
        self.assertTrue(queryset.first().is_waiting_for_feedback)

    def test_annotate_with_is_waiting_for_feedback_true_deadline_expired_first_try(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() - timedelta(days=2))
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_feedback()
        self.assertTrue(queryset.first().is_waiting_for_feedback)

    def test_annotate_with_is_waiting_for_feedback_true_multiple_feedbacksets(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() - timedelta(days=2))
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_feedback()
        self.assertTrue(queryset.first().is_waiting_for_feedback)


class TestAssignmentGroupQuerySetAnnotateWithIsWaitingForDeliveries(TestCase):
    def test_annotate_with_is_waiting_for_deliveries_false_feedback_published(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_deliveries()
        self.assertFalse(queryset.first().is_waiting_for_deliveries)

    def test_annotate_with_is_waiting_for_deliveries_false_deadline_expired(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_deliveries()
        self.assertFalse(queryset.first().is_waiting_for_deliveries)

    def test_annotate_with_is_waiting_for_deliveries_false_deadline_expired_first_try(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() - timedelta(days=2))
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_deliveries()
        self.assertFalse(queryset.first().is_waiting_for_deliveries)

    def test_annotate_with_is_waiting_for_deliveries_true_deadline_not_expired(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() + timedelta(days=1),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_deliveries()
        self.assertTrue(queryset.first().is_waiting_for_deliveries)

    def test_annotate_with_is_waiting_for_deliveries_true_deadline_not_expired_first_try(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() + timedelta(days=2))
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_deliveries()
        self.assertTrue(queryset.first().is_waiting_for_deliveries)

    def test_annotate_with_is_waiting_for_deliveries_true_multiple_feedbacksets(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() - timedelta(days=2))
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() + timedelta(days=1),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_waiting_for_deliveries()
        self.assertTrue(queryset.first().is_waiting_for_deliveries)


class TestAssignmentGroupQuerySetAnnotateWithIsCorrected(TestCase):
    def test_annotate_with_is_corrected_false_feedback_not_published(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_corrected()
        self.assertFalse(queryset.first().is_corrected)

    def test_annotate_with_is_corrected_true_feedback_is_published(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now(),
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_corrected()
        self.assertTrue(queryset.first().is_corrected)

    def test_annotate_with_is_corrected_false_multiple_feedbacksets_last_is_not_published(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=3),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_corrected()
        self.assertFalse(queryset.first().is_corrected)

    def test_annotate_with_is_corrected_true_multiple_feedbacksets_last_is_published(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = AssignmentGroup.objects.all().annotate_with_is_corrected()
        self.assertTrue(queryset.first().is_corrected)


class TestAssignmentGroupQuerySetPermission(TestCase):
    def test_filter_user_is_admin_is_not_admin_on_anything(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.AssignmentGroup')
        self.assertFalse(AssignmentGroup.objects.filter_user_is_admin(user=testuser).exists())

    def test_filter_user_is_admin_superuser(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testgroup = mommy.make('core.AssignmentGroup')
        self.assertEqual(
            {testgroup},
            set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_ignore_assignments_where_not_in_group(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.AssignmentGroup')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testgroup.period)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testgroup.period)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_period(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_subject(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testsubject = mommy.make('core.Subject')
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode__parentnode=testsubject)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_distinct(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testsubject = mommy.make('core.Subject')
        testperiod = mommy.make('core.Period', parentnode=testsubject)
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        subjectpermissiongroup1 = mommy.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        subjectpermissiongroup2 = mommy.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        periodpermissiongroup1 = mommy.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod)
        periodpermissiongroup2 = mommy.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup1.permissiongroup)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup2.permissiongroup)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup1.permissiongroup)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup2.permissiongroup)
        self.assertEqual(
                {testgroup},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))
