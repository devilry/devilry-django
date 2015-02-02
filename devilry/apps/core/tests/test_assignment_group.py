from datetime import datetime, timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder
from ..models import AssignmentGroup
from ..models import Candidate
from ..models.assignment_group import GroupPopNotCandiateError
from ..models.assignment_group import GroupPopToFewCandiatesError
from ..models import Delivery
from ..testhelper import TestHelper
from ..models.model_utils import EtagMismatchException
from devilry.apps.core.models import deliverytypes, Assignment


class TestAssignmentGroup(TestCase):
    """
    Test AssignmentGroup using the next generation less coupled testing frameworks.
    """
    def test_short_displayname_empty(self):
        group1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        self.assertEquals(group1builder.group.short_displayname, unicode(group1builder.group.id))

    def test_short_displayname_students(self):
        group1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group().add_students(
                UserBuilder('student1').user,
                UserBuilder('student2').user)
        self.assertEquals(group1builder.group.short_displayname, 'student1, student2')

    def test_short_displayname_anonymous_candidates(self):
        group1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', anonymous=True)\
            .add_group().add_candidates(
                Candidate(student=UserBuilder('student1').user, candidate_id="aa"),
                Candidate(student=UserBuilder('student2').user, candidate_id="bb"))
        self.assertEquals(group1builder.group.short_displayname, 'aa, bb')

    def test_short_displayname_named(self):
        group1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(name='My group')
        self.assertEquals(group1builder.group.short_displayname, 'My group')

    def test_long_displayname_empty(self):
        group1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        self.assertEquals(group1builder.group.long_displayname, unicode(group1builder.group.id))

    def test_long_displayname_students(self):
        group1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group().add_students(
                UserBuilder('student1', full_name=u'Student One \u00E5').user,
                UserBuilder('student2').user)
        self.assertEquals(group1builder.group.long_displayname, u'Student One \u00E5, student2')

    def test_long_displayname_anonymous_candidates(self):
        group1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', anonymous=True)\
            .add_group().add_candidates(
                Candidate(student=UserBuilder('student1').user, candidate_id="aa"),
                Candidate(student=UserBuilder('student2').user, candidate_id="bb"))
        self.assertEquals(group1builder.group.long_displayname, 'aa, bb')

    def test_long_displayname_named(self):
        group1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(name='My group').add_students(
                UserBuilder('student1', full_name=u'Student One \u00E5').user,
                UserBuilder('student2').user)
        self.assertEquals(group1builder.group.long_displayname, u'My group (Student One \u00E5, student2)')

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


class TestAssignmentGroupCanDelete(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes="uni:admin(nodeadmin)",
                            subjects=["sub"],
                            periods=["p1"],
                            assignments=['a1:admin(a1admin)'],
                            assignmentgroups=['g1:candidate(student1):examiner(examiner1)'])
        self.g1 = self.testhelper.sub_p1_a1_g1

    def test_is_empty(self):
        self.assertTrue(self.g1.is_empty())

    def _add_delivery(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(1)')
        self.testhelper.add_delivery(self.g1,
                                     {"firsttry.py": "print first"},
                                     time_of_delivery=-1)

    def test_not_is_empty(self):
        self.assertTrue(self.g1.is_empty())
        self._add_delivery()
        self.assertFalse(self.g1.is_empty())

    def test_can_delete_superuser(self):
        superuser = self.testhelper.create_superuser('superuser')
        self.assertTrue(self.g1.can_delete(superuser))
        self._add_delivery()
        self.assertTrue(self.g1.can_delete(superuser))

    def test_can_delete_assignmentadmin(self):
        self.assertTrue(self.g1.can_delete(self.testhelper.a1admin))
        self._add_delivery()
        self.assertFalse(self.g1.can_delete(self.testhelper.a1admin))

    def test_can_delete_nodeadmin(self):
        self.assertTrue(self.g1.can_delete(self.testhelper.nodeadmin))
        self._add_delivery()
        self.assertFalse(self.g1.can_delete(self.testhelper.nodeadmin))

    def test_can_not_delete_nobody(self):
        nobody = self.testhelper.create_user('nobody')
        self.assertFalse(self.g1.can_delete(nobody))


class TestAssignmentGroupSplit(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p1"],
                            assignments=['a1'])

    def _create_testdata(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1,student2,student3):examiner(examiner1,examiner2,examiner3)')
        self.testhelper.sub_p1_a1.max_points = 100
        self.testhelper.sub_p1_a1.save()

        # Add d1 and deliveries
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(1)')
        self.testhelper.add_delivery("sub.p1.a1.g1", {"firsttry.py": "print first"},
                                     time_of_delivery=datetime(2002, 1, 1))
        delivery2 = self.testhelper.add_delivery("sub.p1.a1.g1", {"secondtry.py": "print second"},
                                                 time_of_delivery=-1) # days after deadline
        self.testhelper.add_feedback(delivery=delivery2,
                                     verdict={'grade': 'F', 'points':10, 'is_passing_grade':False},
                                     rendered_view='Bad',
                                     timestamp=datetime(2005, 1, 1))

        # Add d2 and deliveries
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d2:ends(4)')
        delivery3 = self.testhelper.add_delivery("sub.p1.a1.g1", {"thirdtry.py": "print third"},
                                                 time_of_delivery=-1) # days after deadline
        self.testhelper.add_feedback(delivery=delivery3,
                                     verdict={'grade': 'C', 'points':40, 'is_passing_grade':True},
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
        self.assertEquals(set(tags), set(['a', 'b']))

        # Examiners
        self.assertEquals(g1copy.examiners.count(), 3)
        examiner_usernames = [e.user.username for e in g1copy.examiners.all()]
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
        self.assertEquals(g1.candidates.count(), 3) # We check this again after popping
        candidate = g1.candidates.order_by('student__username')[1]
        g1copy = g1.pop_candidate(candidate)

        self.assertEquals(g1copy.name, 'Stuff') # Sanity test - the tests for copying are above
        self.assertEquals(g1copy.candidates.count(), 1)
        self.assertEquals(g1.candidates.count(), 2)
        self.assertEquals(candidate.student.username, 'student2')
        self.assertEquals(g1copy.candidates.all()[0], candidate)

    def test_pop_candidate_not_candidate(self):
        self._create_testdata()
        self.testhelper.add_to_path('uni;sub.p1.a2.other:candidate(student10)')
        g1 = self.testhelper.sub_p1_a1_g1
        other = self.testhelper.sub_p1_a2_other
        candidate = other.candidates.all()[0]
        with self.assertRaises(GroupPopNotCandiateError):
            g1copy = g1.pop_candidate(candidate)

    def test_pop_candidate_to_few_candidates(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        g1 = self.testhelper.sub_p1_a1_g1
        candidate = g1.candidates.all()[0]
        with self.assertRaises(GroupPopToFewCandiatesError):
            g1copy = g1.pop_candidate(candidate)

    def _create_mergetestdata(self):
        self._create_testdata()
        source = self.testhelper.sub_p1_a1_g1

        self.testhelper.add_to_path('uni;sub.p1.a1.target:candidate(dewey):examiner(donald)')

        # Add d1 and deliveries. d1 matches d1 in g1 (the source)
        self.testhelper.add_to_path('uni;sub.p1.a1.target.d1:ends(1)')
        self.testhelper.add_delivery("sub.p1.a1.target", {"a.py": "print a"},
                                     time_of_delivery=1) # days after deadline

        # Add d2 and deliveries
        self.testhelper.add_to_path('uni;sub.p1.a1.target.d2:ends(11)')
        delivery = self.testhelper.add_delivery("sub.p1.a1.target", {"b.py": "print b"},
                                                time_of_delivery=-1) # days after deadline

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
        self.assertEquals(self.testhelper.sub_p1_a1_g1_d2.deliveries.count(), 2) # The one from _create_testdata() and the one copied in above
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
        self.assertEquals(set([e.user.username for e in target.examiners.all()]),
                          set(['donald', 'examiner1', 'examiner2', 'examiner3']))

    def test_merge_into_examiners(self):
        source, target = self._create_mergetestdata()
        source.merge_into(target)
        self.assertEquals(target.candidates.count(), 4)
        self.assertEquals(set([e.student.username for e in target.candidates.all()]),
                          set(['dewey', 'student1', 'student2', 'student3']))

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

        self.assertEquals(deadlines[0].deliveries.count(), 3) # d1 from both have been merged
        self.assertEquals(deadlines[1].deliveries.count(), 1) # g1(source) d2
        self.assertEquals(deadlines[2].deliveries.count(), 1) # target d2

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
                                                time_of_delivery=2) # days after deadline
        self.testhelper.add_feedback(delivery=delivery,
                                     verdict={'grade': 'A', 'points':100, 'is_passing_grade':True},
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
                assignmentgroups=['{groupname}:candidate(student1):examiner(examiner1)'.format(**vars())],
                deadlines=['d1:ends(1)'])
            self.testhelper.add_delivery("sub.p1.a1.{groupname}".format(**vars()),
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
                assignmentgroups=['{groupname}:candidate(student1):examiner(examiner1)'.format(**vars())],
                deadlines=['d1:ends(1)'])
            self.testhelper.add_delivery("sub.p1.a1.{groupname}".format(**vars()),
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
        candidates = [cand.student.username for cand in c.candidates.all()]
        self.assertEquals(len(candidates), 3)
        self.assertEquals(set(candidates), set(['student1', 'student2', 'student3']))

        examiners = [cand.user.username for cand in c.examiners.all()]
        self.assertEquals(len(examiners), 3)
        self.assertEquals(set(examiners), set(['examiner1', 'examiner2', 'examiner3']))

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


class TestAssignmentGroupUserIds(TestCase):

    def setUp(self):
        self.testhelper = TestHelper()

    def test_get_all_admin_ids(self):
        self.testhelper.add(
            nodes='uni:admin(uniadm).inf:admin(infadm,infadm2)',
            subjects=['sub:admin(subadm,subadm2)'],
            periods=['p1:admin(p1adm)'],
            assignments=['a1:admin(a1adm,a1adm2)'],
            assignmentgroups=['g1:candidate(student1)']
        )

        admin_ids = self.testhelper.sub_p1_a1_g1.get_all_admin_ids()
        self.assertEquals(len(admin_ids), 8)
        self.assertEquals(
            admin_ids,
            {self.testhelper.uniadm.id, self.testhelper.infadm.id,
             self.testhelper.infadm2.id, self.testhelper.subadm.id,
             self.testhelper.subadm2.id, self.testhelper.p1adm.id,
             self.testhelper.a1adm.id, self.testhelper.a1adm2.id})


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
        week1 = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment('week1',
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
        week1 = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment('week1',
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

    def test_filter_is_examiner(self):
        examiner1 = UserBuilder('examiner1').user
        week1 = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment('week1')
        group1builder = week1.add_group().add_examiners(examiner1)

        # Add another group to make sure we do not get false positives
        week1.add_group().add_examiners(UserBuilder('examiner2').user)

        qry = AssignmentGroup.objects.filter_is_examiner(examiner1)
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

    def test_filter_is_candidate(self):
        student1 = UserBuilder('student1').user
        otherstudent = UserBuilder('otherstudent').user
        periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        group1 = periodbuilder.add_assignment('assignment1')\
            .add_group(students=[student1]).group
        periodbuilder.add_assignment('assignment2')\
            .add_group(students=[otherstudent])
        group3 = periodbuilder.add_assignment('assignment3')\
            .add_group(students=[student1]).group
        qry = AssignmentGroup.objects.filter_is_candidate(student1)
        self.assertEquals(qry.count(), 2)
        self.assertEquals(set(qry), set([group1, group3]))

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

        # make sure we are not getting false positives
        self.assertEquals(AssignmentGroup.objects.filter_is_examiner(examiner1).count(), 3)
        self.assertEquals(AssignmentGroup.objects.filter_is_examiner(otherexaminer).count(), 1)


class TestAssignmentGroupOld(TestCase, TestHelper):
    """
    Do NOT add new tests here, add them to TestAssignmentGroup.
    """

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["old:begins(-2):ends(1)", "looong:admin(teacher1):begins(-1):ends(10)"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                   "g2:candidate(student2):examiner(examiner2)",
                                   "g3:candidate(student3,student2):examiner(examiner1,examiner2,examiner3)"])
        self.add_to_path('uio.ifi;inf1100.old.oldassignment.group1:examiner(examiner3)')

    def test_assignment_property(self):
        self.assertEquals(self.inf1100_looong_assignment1_g1.assignment,
                self.inf1100_looong_assignment1)

    def test_period_property(self):
        self.assertEquals(self.inf1100_looong_assignment1_g1.period,
                self.inf1100_looong)

    def test_subject_property(self):
        self.assertEquals(self.inf1100_looong_assignment1_g1.subject,
                self.inf1100)

    def test_where_is_admin(self):
        self.assertEquals(6, AssignmentGroup.where_is_admin(self.teacher1).count())

    def test_where_is_candidate(self):
        self.assertEquals(8, AssignmentGroup.where_is_candidate(self.student2).count())
        self.assertEquals(4, AssignmentGroup.where_is_candidate(self.student1).count())

    def test_published_where_is_candidate(self):
        self.assertEquals(8, AssignmentGroup.published_where_is_candidate(self.student2).count())
        self.assertEquals(4, AssignmentGroup.published_where_is_candidate(self.student3).count())

    def test_active_where_is_candidate(self):
        self.assertEquals(4, AssignmentGroup.active_where_is_candidate(self.student2).count())
        # Set publishing time to future
        self.inf1100_looong_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_looong_assignment1.save()
        self.assertEquals(2, AssignmentGroup.active_where_is_candidate(self.student2).count())

    def test_old_where_is_candidate(self):
        self.assertEquals(2, AssignmentGroup.old_where_is_candidate(self.student1).count())
        self.inf1100_looong.end_time = datetime.now() - timedelta(10)
        self.inf1100_looong.save()
        self.assertEquals(4, AssignmentGroup.old_where_is_candidate(self.student1).count())

    def test_where_is_examiner(self):
        self.assertEquals(8, AssignmentGroup.where_is_examiner(self.examiner2).count())
        self.assertEquals(5, AssignmentGroup.where_is_examiner(self.examiner3).count())
        self.inf1100_looong_assignment1_g2.examiners.create(user=self.examiner3)
        self.assertEquals(6, AssignmentGroup.where_is_examiner(self.examiner3).count())

    def test_published_where_is_examiner(self):
        self.assertEquals(8, AssignmentGroup.published_where_is_examiner(self.examiner2).count())
        self.assertEquals(8, AssignmentGroup.published_where_is_examiner(self.examiner1).count())
        self.assertEquals(0, AssignmentGroup.published_where_is_examiner(self.examiner1,
                    old=False, active=False).count())
        self.assertEquals(4, AssignmentGroup.published_where_is_examiner(self.examiner1,
                    old=True, active=False).count())
        self.assertEquals(4, AssignmentGroup.published_where_is_examiner(self.examiner1,
                    old=False, active=True).count())

    def test_active_where_is_examiner(self):
        self.assertEquals(4, AssignmentGroup.active_where_is_examiner(self.examiner1).count())
        self.assertEquals(2, AssignmentGroup.active_where_is_examiner(self.examiner3).count())

    def test_old_where_is_examiner(self):
        self.assertEquals(4, AssignmentGroup.old_where_is_examiner(self.examiner1).count())
        self.assertEquals(3, AssignmentGroup.old_where_is_examiner(self.examiner3).count())

    def test_get_students(self):
        self.assertEquals('student1', self.inf1100_looong_assignment1_g1.get_students())
        self.assertEquals('student3, student2', self.inf1100_looong_assignment1_g3.get_students())

    def test_get_examiners(self):
        self.assertEquals('examiner1, examiner2, examiner3', self.inf1100_looong_assignment1_g3.get_examiners())

    def test_is_admin(self):
        self.assertFalse(self.inf1100_looong_assignment1_g3.is_admin(self.student1))
        self.assertFalse(self.inf1100_looong_assignment1_g3.is_admin(self.examiner1))
        self.assertTrue(self.inf1100_looong_assignment1_g3.is_admin(self.teacher1))
        self.assertTrue(self.inf1100_looong_assignment1_g3.is_admin(self.uioadmin))

    def test_is_examiner(self):
        self.assertTrue(self.inf1100_looong_assignment1_g1.is_examiner(self.examiner1))
        self.assertFalse(self.inf1100_looong_assignment1_g1.is_examiner(self.examiner2))

    def test_is_candidate(self):
        self.assertTrue(self.inf1100_looong_assignment1_g1.is_candidate(self.student1))
        self.assertFalse(self.inf1100_looong_assignment1_g1.is_candidate(self.student2))

    def test_clean_deadline_after_endtime(self):
        assignment_group = self.inf1100_looong_assignment1_g1
        assignment = assignment_group.parentnode
        assignment.parentnode.start_time = datetime(2010, 1, 1)
        assignment.parentnode.end_time = datetime(2011, 1, 1)
        assignment.publishing_time = datetime(2010, 1, 2)
        deadline = assignment_group.deadlines.create(deadline=datetime(2010, 5, 5), text=None)
        deadline.clean()
        deadline = assignment_group.deadlines.create(deadline=datetime(2012, 1, 1), text=None)
        self.assertRaises(ValidationError, deadline.clean)

    def test_clean_deadline_before_publishing_time(self):
        future3 = datetime.now() + timedelta(3)
        future6 = datetime.now() + timedelta(6)
        assignment_group = self.inf1100_looong_assignment1_g1
        oblig1 = assignment_group.parentnode
        oblig1.publishing_time = datetime.now()
        oblig1.parentnode.end_time = future6
        deadline = assignment_group.deadlines.create(deadline=future3, text=None)
        deadline.clean()
        oblig1.publishing_time = future6
        deadline = assignment_group.deadlines.create(deadline=future3, text=None)
        self.assertRaises(ValidationError, deadline.clean)

    def add_delivery(self, assignmentgroup, user):
        assignmentgroup.deliveries.create(delivered_by=user,
                                          successful=True)

    def test_etag_update(self):
        etag = datetime.now()
        obj = self.inf1100_looong_assignment1_g1
        obj.is_open = False
        self.assertRaises(EtagMismatchException, obj.etag_update, etag)
        try:
            obj.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            obj.etag_update(e.etag)
        obj2 = AssignmentGroup.objects.get(id=obj.id)
        self.assertFalse(obj2.is_open)
