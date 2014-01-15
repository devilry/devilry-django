from django.core.exceptions import ValidationError
from datetime import timedelta
from django.test import TestCase

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.datebuilder import DateTimeBuilder
from ..models import Deadline
from ..testhelper import TestHelper



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
        self.okVerdict = {"grade": "C", "points": 85, "is_passing_grade": True}

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