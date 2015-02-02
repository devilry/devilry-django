from django.core.exceptions import ValidationError
from django.test import TestCase

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder
from devilry.apps.core.models import Deadline, Delivery
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models.deadline import NewerDeadlineExistsError
from devilry.apps.core.models import deliverytypes
from devilry.apps.core.testhelper import TestHelper



class TestDeadline(TestCase):
    def test_create_deadline_opens_assignmentgroup(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        groupbuilder.update(is_open=False)
        groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=3))
        groupbuilder.reload_from_db()
        self.assertTrue(groupbuilder.group.is_open)

    def test_update_deadline_does_not_change_assignmentgroup_is_open(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        deadline = groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=3))
        groupbuilder.update(is_open=False)
        deadline.save()
        groupbuilder.reload_from_db()
        self.assertFalse(groupbuilder.group.is_open)

    def test_create_deadline_changes_assignmentgroup_delivery_status(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        self.assertEquals(groupbuilder.group.delivery_status, 'no-deadlines')
        groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=3))
        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.delivery_status, 'waiting-for-something')

    def test_set_last_deadline_on_group_single(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        self.assertIsNone(groupbuilder.group.last_deadline)
        deadline = groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=3))
        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.last_deadline, deadline)

    def test_set_last_deadline_on_group_newest(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        self.assertIsNone(groupbuilder.group.last_deadline)
        deadline2 = groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=10))
        deadline1 = groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=5))
        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.last_deadline, deadline2)

    def test_set_last_deadline_on_group_newest_even_when_edited(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        self.assertIsNone(groupbuilder.group.last_deadline)
        deadline2 = groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=10))
        deadline1 = groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=5))
        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.last_deadline, deadline2)
        deadline1.deadline = DateTimeBuilder.now().plus(days=20)
        deadline1.save()
        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.last_deadline, deadline1)

    def test_set_last_deadline_on_group_copy(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        self.assertIsNone(groupbuilder.group.last_deadline)
        deadline2 = Deadline(assignment_group=groupbuilder.group, deadline=DateTimeBuilder.now().plus(days=10))
        deadline1 = Deadline(assignment_group=groupbuilder.group, deadline=DateTimeBuilder.now().plus(days=5))
        # Copy cleans deadlines before save, so we have to do that for the assertEquals below to match
        for deadline in deadline1, deadline2:
            deadline.clean()
            deadline.save()
        groupbuilder.reload_from_db()
        groupcopy = groupbuilder.group.copy_all_except_candidates()
        self.assertEquals(groupcopy.last_deadline.deadline, deadline2.deadline)

    def test_set_last_deadline_on_group_merge(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1builder = assignmentbuilder.add_group()
        group2builder = assignmentbuilder.add_group()
        deadline2 = group2builder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=10))
        deadline3 = group1builder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=15))
        deadline1 = group1builder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=5))
        group2builder.group.merge_into(group1builder.group)
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline, deadline3)

    def test_set_last_deadline_on_group_merge_reverse_direction(self): # Direction of the merge should not matter
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1builder = assignmentbuilder.add_group()
        group2builder = assignmentbuilder.add_group()
        deadline2 = group2builder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=10))
        deadline3 = group1builder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=15))
        deadline1 = group1builder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=5))
        group1builder.group.merge_into(group2builder.group)
        group2builder.reload_from_db()
        self.assertEquals(group2builder.group.last_deadline, deadline3)


    def test_do_not_autocreate_delivery_if_electronic(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        deadline = groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=10))
        self.assertEquals(deadline.deliveries.count(), 0)

    def test_autocreate_delivery_if_nonelectronic(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                delivery_types=deliverytypes.NON_ELECTRONIC)\
            .add_group()
        deadline = groupbuilder.group.deadlines.create(deadline=DateTimeBuilder.now().plus(days=10))
        self.assertEquals(deadline.deliveries.count(), 1)
        self.assertTrue(deadline.deliveries.all()[0].successful)
        groupbuilder.reload_from_db()
        last_delivery = Delivery.objects.filter(deadline__assignment_group=groupbuilder.group).first()
        self.assertEquals(last_delivery, deadline.deliveries.all()[0])

    def test_autocreate_delivery_if_nonelectronic_false(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                delivery_types=deliverytypes.NON_ELECTRONIC)\
            .add_group()
        deadline = Deadline(
            assignment_group=groupbuilder.group,
            deadline=DateTimeBuilder.now().plus(days=10))
        deadline.save(autocreate_delivery_if_nonelectronic=False)
        self.assertEquals(deadline.deliveries.count(), 0)

    def test_smart_create_electronic(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1builder = assignmentbuilder.add_group()
        group2builder = assignmentbuilder.add_group()
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        result = Deadline.objects.smart_create(
            assignmentbuilder.assignment.assignmentgroups.all(),
            deadline_datetime=deadline_datetime,
            text='Hello world')
        self.assertIsNone(result)

        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.deadlines.count(), 1)
        created_deadline = group1builder.group.deadlines.all()[0]
        self.assertEquals(created_deadline.deadline, deadline_datetime)
        self.assertEquals(created_deadline.text, 'Hello world')
        self.assertEquals(group1builder.group.last_deadline, created_deadline)
        self.assertEquals(group1builder.group.last_deadline.deliveries.count(), 0)

        group2builder.reload_from_db()
        self.assertEquals(group2builder.group.deadlines.all()[0].deadline, deadline_datetime)
        self.assertEquals(group2builder.group.last_deadline, group2builder.group.deadlines.all()[0])

    def test_smart_create_no_text(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1builder = assignmentbuilder.add_group()
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        Deadline.objects.smart_create(
            assignmentbuilder.assignment.assignmentgroups.all(),
            deadline_datetime=deadline_datetime)
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline.deadline, deadline_datetime)
        self.assertEquals(group1builder.group.last_deadline.text, None)

    def test_smart_create_newer_exists(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1builder = assignmentbuilder.add_group()
        group1builder.add_deadline_in_x_weeks(weeks=2)
        self.assertEquals(group1builder.group.deadlines.count(), 1)
        with self.assertRaises(NewerDeadlineExistsError):
            Deadline.objects.smart_create(
                assignmentbuilder.assignment.assignmentgroups.all(),
                deadline_datetime=DateTimeBuilder.now().plus(days=1))
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.deadlines.count(), 1)

    def test_smart_create_non_electronic(self):
        assignment = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', delivery_types=deliverytypes.NON_ELECTRONIC).assignment
        group1 = AssignmentGroup(parentnode=assignment)
        group2 = AssignmentGroup(parentnode=assignment)
        for group in group1, group2:
            group.save(autocreate_first_deadline_for_nonelectronic=False)
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        result = Deadline.objects.smart_create(
            assignment.assignmentgroups.all(),
            deadline_datetime=deadline_datetime,
            text='Hello world')
        self.assertIsNone(result)
        self.assertEquals(group1.deadlines.count(), 1)

        group1 = AssignmentGroup.objects.get(id=group1.id) # Reload from db
        created_deadline = group1.deadlines.all()[0]
        self.assertEquals(created_deadline.deadline, deadline_datetime)
        self.assertEquals(created_deadline.text, 'Hello world')
        self.assertEquals(group1.last_deadline, created_deadline)
        self.assertEquals(group1.last_deadline.deliveries.count(), 1)
        group1_last_delivery = Delivery.objects.filter(deadline__assignment_group=group1).first()
        self.assertEquals(group1.last_deadline.deliveries.all()[0], group1_last_delivery)
        self.assertTrue(group1_last_delivery.successful)
        self.assertEquals(group1_last_delivery.number, 1)

        group2 = AssignmentGroup.objects.get(id=group2.id) # Reload from db
        self.assertEquals(group2.deadlines.all()[0].deadline, deadline_datetime)
        self.assertEquals(group2.last_deadline, group2.deadlines.all()[0])
        self.assertEquals(group2.last_deadline.deliveries.count(), 1)
        group2_last_delivery = Delivery.objects.filter(deadline__assignment_group=group2).first()
        self.assertEquals(group2.last_deadline.deliveries.all()[0], group2_last_delivery)
        self.assertTrue(group2_last_delivery.successful)
        self.assertEquals(group2_last_delivery.number, 1)

    def test_is_in_the_future_and_is_in_the_past(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group()
        past_deadline = groupbuilder.add_deadline_x_weeks_ago(weeks=2).deadline
        future_deadline = groupbuilder.add_deadline_in_x_weeks(weeks=2).deadline
        self.assertTrue(future_deadline.is_in_the_future())
        self.assertFalse(future_deadline.is_in_the_past())
        self.assertFalse(past_deadline.is_in_the_future())
        self.assertTrue(past_deadline.is_in_the_past())


class TestDeadlineOld(TestCase, TestHelper):
    """
    WARNING: Old tests for Deadline using TestHelper. We should
    NOT add new tests here, and the tests should be updated and
    moved to TestDeadline if we update any of the tested 
    methods, or need to add more tests.
    """
    def setUp(self):
        TestHelper.set_memory_deliverystore()
        self.goodFile = {"good.py": "print awesome"}
        self.okVerdict = {"grade": "C", "points": 1, "is_passing_grade": True}

    def test_publish_feedbacks_directly(self):
        self.add_to_path('uio.ifi;inf1100.period1.assignment1.group1:candidate(student1):examiner(examiner1).d1:ends(10)')
        self.delivery = self.add_delivery("inf1100.period1.assignment1.group1", self.goodFile)
        self.feedback = self.add_feedback(self.delivery, verdict=self.okVerdict)
        # ..._assignment1.examiners_publish_feedbacks_directly is True by default
        self.assertTrue(Deadline.objects.get(id=self.feedback.delivery.deadline.id).feedbacks_published)

    def test_dont_publish_feedbacks_directly(self):
        self.add_to_path('uio.ifi;inf1100.period1.assignment1.group1:candidate(student1):examiner(examiner1).d1:ends(10)')
        # Disable publish feedbacks directly before adding delivery and feedback
        self.inf1100_period1_assignment1.examiners_publish_feedbacks_directly = False
        self.inf1100_period1_assignment1.save()

        self.delivery = self.add_delivery("inf1100.period1.assignment1.group1", self.goodFile)
        self.feedback = self.add_feedback(self.delivery, verdict=self.okVerdict)
        self.assertFalse(Deadline.objects.get(id=self.feedback.delivery.deadline.id).feedbacks_published)

    def test_deadline_notunique(self):
        self.add_to_path('uni;sub.p1:begins(-2).a1.g1.d1:ends(5)')
        self.add_to_path('uni;sub.p1.a1.g2.d1:ends(5)')

        g1 = self.sub_p1_a1_g1
        d1 = self.sub_p1_a1_g1_d1
        g2_d1 = self.sub_p1_a1_g2_d1

        # Ensure that we are not checking outside the group (the tests below would fail if this fails)
        self.assertEquals(d1.deadline, g2_d1.deadline)

        # Will not fail because id matches in the validator
        d1.full_clean()

        d2 = Deadline(assignment_group=g1, deadline=d1.deadline)
        with self.assertRaises(ValidationError):
            d2.full_clean()

    def test_can_delete_superuser(self):
        self.add_to_path('uni;sub.p1:begins(-2).a1.g1:candidate(stud1).d1:ends(5)')
        self.add_delivery("sub.p1.a1.g1", self.goodFile)
        superuser = self.create_superuser('superuser')
        deadline = Deadline.objects.get(id=self.sub_p1_a1_g1_d1.id)
        self.assertTrue(deadline.can_delete(superuser))

    def test_can_delete_assignmentadmin(self):
        self.add_to_path('uni;sub.p1:begins(-2).a1:admin(a1admin).g1:candidate(stud1).d1:ends(5)')
        deadline = Deadline.objects.get(id=self.sub_p1_a1_g1_d1.id)
        self.assertTrue(deadline.can_delete(self.a1admin))
        self.add_delivery("sub.p1.a1.g1", self.goodFile)
        self.assertFalse(deadline.can_delete(self.a1admin))

    def test_can_delete_nodeadmin(self):
        self.add_to_path('uni:admin(uniadm);sub.p1:begins(-2).a1.g1:candidate(stud1).d1:ends(5)')
        deadline = Deadline.objects.get(id=self.sub_p1_a1_g1_d1.id)
        self.assertTrue(deadline.can_delete(self.uniadm))
        self.add_delivery("sub.p1.a1.g1", self.goodFile)
        self.assertFalse(deadline.can_delete(self.uniadm))

    def test_copy(self):
        self.add(nodes="uni",
                 subjects=["sub"],
                 periods=["p1"],
                 assignments=['a1'])
        self.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.add_to_path('uni;sub.p1.a1.g2:candidate(student2):examiner(examiner2)')

        # Add some deliveries deliveries
        self.add_to_path('uni;sub.p1.a1.g1.d1:ends(1)')
        self.add_delivery("sub.p1.a1.g1", {"firsttry.py": "print first"},
                          time_of_delivery=-2) # days after deadline
        self.add_delivery("sub.p1.a1.g1", {"secondtry.py": "print second"},
                          time_of_delivery=-1) # days after deadline

        d1 = self.sub_p1_a1_g1_d1
        d1.text = 'Test text'
        g2 = self.sub_p1_a1_g2
        self.assertEquals(g2.deadlines.all().count(), 0)
        d1copy = d1.copy(g2)
        self.assertEquals(g2.deadlines.all().count(), 1)
        self.assertEquals(d1copy.deadline, d1.deadline)
        self.assertEquals(d1copy.text, 'Test text')

        self.assertEquals(d1.deliveries.count(), d1copy.deliveries.count())
        self.assertEquals(d1copy.deliveries.count(), 2)
        for delivery, deliverycopy in zip(d1.deliveries.all(), d1copy.deliveries.all()):
            self.assertEquals(delivery.delivery_type, deliverycopy.delivery_type)
            self.assertEquals(delivery.time_of_delivery, deliverycopy.time_of_delivery)
            self.assertEquals(delivery.number, deliverycopy.number)
            self.assertEquals(delivery.delivered_by, deliverycopy.delivered_by)
            self.assertEquals(delivery.deadline.deadline, deliverycopy.deadline.deadline)
            self.assertEquals(delivery.delivered_by, deliverycopy.delivered_by)
            self.assertEquals(delivery.alias_delivery, deliverycopy.alias_delivery)

    def test_query_successful_deliveries(self):
        self.add_to_path('uni:admin(uniadm);sub.p1:begins(-2).a1.g1:candidate(stud1).d1:ends(5)')
        deadline = self.sub_p1_a1_g1_d1
        delivery1 = self.add_delivery("sub.p1.a1.g1", self.goodFile)
        delivery2 = self.add_delivery("sub.p1.a1.g1", self.goodFile)
        delivery2.successful = False
        delivery2.save()
        self.assertEquals(deadline.query_successful_deliveries().count(), 1)
        self.assertEquals(deadline.query_successful_deliveries()[0], delivery1)
