from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from ..models import Delivery
from ..testhelper import TestHelper

class TestDelivery(TestCase, TestHelper):
    def setUp(self):
        TestHelper.set_memory_deliverystore()

    def _create_testdata(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["period1:admin(teacher1):begins(-5):ends(10)"],
                 assignments=["assignment1:pub(60)"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                   "g2:candidate(student2):examiner(examiner2)",
                                   "g3:candidate(student3,student2):examiner(examiner1,examiner2,examiner3)",
                                   "g4:candidate(student4):examiner(examiner3)"],
                 deadlines=['d1:ends(1)'])
        self.goodFile = {"good.py": "print awesome"}
        self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        self.add_delivery("inf1100.period1.assignment1.g3", self.goodFile)

    def test_where_is_admin(self):
        self._create_testdata()
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(Delivery.where_is_admin(teacher1).count(), 3)
        delivery0 = self.inf1100_period1_assignment1_g1_d1.deliveries.all()[0]
        delivery0.successful = False
        delivery0.save()
        self.assertEquals(Delivery.where_is_admin(teacher1).count(), 2)

    def test_published_where_is_examiner(self):
        self._create_testdata()
        examiner1 = User.objects.get(username='examiner1')
        deliveries = Delivery.published_where_is_examiner(examiner1)
        self.assertEquals(deliveries.count(), 2)
        delivery0 = deliveries.all()[0]
        delivery0.successful = False
        delivery0.save()
        self.assertEquals(Delivery.published_where_is_examiner(examiner1).count(), 1)

    def test_delivery(self):
        self._create_testdata()
        assignmentgroup = self.inf1100_period1_assignment1_g3
        beforeadd = datetime.now().replace(microsecond=0, tzinfo=None)
        d = self.add_delivery("inf1100.period1.assignment1.g3", self.goodFile)
        afteradd = datetime.now().replace(microsecond=0, tzinfo=None)
        self.assertEquals(d.deadline.assignment_group, assignmentgroup)
        self.assertTrue(d.successful)
        self.assertEquals(d.number, 2)
        self.assertTrue(d.time_of_delivery >= beforeadd and d.time_of_delivery <=afteradd)

        # TODO find a graceful way to handle this error:
        d.number = 1
        self.assertRaises(IntegrityError, d.save())

    def test_delete_delivered_by_candidate(self):
        self._create_testdata()
        delivery = self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        delivery = Delivery.objects.get(id=delivery.id) # Re-get from DB just to be doubly sure we are using the same delivery below
        self.assertEquals(delivery.delivered_by.student, self.student2)
        group = self.inf1100_period1_assignment1_g2
        group.candidates.all()[0].delete()
        delivery = Delivery.objects.get(id=delivery.id) # Re-get from DB
        self.assertEquals(delivery.delivered_by, None)

    def test_delivery_numbering(self):
        self._create_testdata()
        deadline = self.inf1100_period1_assignment1_g1_d1
        self.assertEquals(deadline.deliveries.count(), 1)
        self.assertEquals(deadline.deliveries.all()[0].number, 1)
        d2 = Delivery(deadline=deadline,
                     delivered_by=deadline.assignment_group.candidates.all()[0])
        d2.save()
        d3 = Delivery(deadline=deadline,
                     delivered_by=deadline.assignment_group.candidates.all()[0])
        d3.save()
        self.assertEquals(d2.number, 0)
        self.assertEquals(d3.number, 0)
        d3.successful = True
        d3.save()
        self.assertEquals(d3.number, 2)
        d2.successful = True
        d2.save()
        self.assertEquals(d2.number, 3)

    def test_published_where_is_candidate(self):
        self._create_testdata()
        # Add 2 on g1
        d = self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        d = self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        # Add 3 on g2
        d = self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        d = self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        d = self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        # Add 2 on g3
        d = self.add_delivery("inf1100.period1.assignment1.g3", self.goodFile)
        d = self.add_delivery("inf1100.period1.assignment1.g3", self.goodFile)

        self.assertEquals(Delivery.published_where_is_candidate(self.student1).count(), 3)
        self.assertEquals(Delivery.published_where_is_candidate(self.student2).count(), 7)
        self.assertEquals(Delivery.published_where_is_candidate(self.student3).count(), 3)
        self.assertEquals(Delivery.published_where_is_candidate(self.student4).count(), 0)

        delivery = Delivery.published_where_is_candidate(self.student3)[0]
        delivery.successful = False
        delivery.save()
        self.assertEquals(Delivery.published_where_is_candidate(self.student3).count(), 2)


    def test_hard_deadline(self):
        self._create_testdata()
        self.add_to_path('uni.ifi;inf1100.period1.assignment0.g1:candidate(student1):examiner(examiner1).d0:ends(1)')

        # Soft deadlines work without any errors
        deadline = self.inf1100_period1_assignment0_g1_d0
        self.assertTrue(deadline.deadline < datetime.now())
        self.add_delivery("inf1100.period1.assignment0.g1", self.goodFile)

        # Hard deadlines
        assignment = self.inf1100_period1_assignment0
        assignment.deadline_handling = 1
        assignment.save()
        with self.assertRaises(ValidationError):
            self.add_delivery("inf1100.period1.assignment0.g1", self.goodFile)


    def test_override_autoset(self):
        self.add(nodes="uni",
                 subjects=["sub"],
                 periods=["p1"],
                 assignments=['a1'])
        self.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1).d1')
        d1 = self.sub_p1_a1_g1_d1

        time_of_delivery = datetime(2005, 1, 1, 0, 0, 0)
        delivery = Delivery(deadline=d1,
                            number=10,
                            successful=False,
                            time_of_delivery=time_of_delivery)
        delivery.full_clean()
        delivery.save(autoset_number=False,
                      autoset_time_of_delivery=False)
        self.assertEquals(delivery.number, 10)
        self.assertEquals(delivery.successful, False)
        self.assertEquals(delivery.time_of_delivery, time_of_delivery)


    def _create_copydata(self):
        self.add(nodes="uni",
                 subjects=["sub"],
                 periods=["p1"],
                 assignments=['a1'])
        self.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1).d1')

        # Create delivery for alias_delivery
        self.add_to_path('uni;sub.p_old.a1.g1:candidate(student1):examiner(examiner1).d1')
        old_delivery = self.add_delivery("sub.p_old.a1.g1", {"secondtry.py": "print second"})

        # Make a delivery without any of the default/generated values, so when
        # we check that they are copied, we get no generate stuff
        g1 = self.sub_p1_a1_g1
        d1 = self.sub_p1_a1_g1_d1
        time_of_delivery = datetime(2005, 1, 1, 0, 0, 0)
        delivery = Delivery(deadline=d1,
                            number=10,
                            successful=False,
                            delivery_type=1,
                            delivered_by=g1.candidates.all()[0],
                            alias_delivery=old_delivery,
                            time_of_delivery=time_of_delivery)
        delivery.full_clean()
        delivery.save(autoset_number=False,
                      autoset_time_of_delivery=False)
        delivery.add_file('test.txt', ['Hello', ' world'])
        return delivery, old_delivery


    def test_copy_own_attributes(self):
        delivery, old_delivery = self._create_copydata()
        self.add_to_path('uni;sub.p1.a1.g2:candidate(student2).d1')
        newdeadline = self.sub_p1_a1_g2_d1
        copy = delivery.copy(newdeadline)

        self.assertEquals(copy.deadline, newdeadline)
        self.assertEquals(copy.delivery_type, 1)
        self.assertEquals(copy.number, 10)
        self.assertEquals(copy.successful, False)
        self.assertEquals(copy.time_of_delivery, datetime(2005, 1, 1, 0, 0, 0))
        self.assertEquals(copy.delivered_by.student, self.student1)
        self.assertEquals(copy.alias_delivery, old_delivery)

        # Check copy_of and the virtual reverse relationship
        self.assertEquals(copy.copy_of, delivery)
        self.assertEquals(list(delivery.copies.all()),
                          [copy])

    def test_copy_filemetas(self):
        delivery, old_delivery = self._create_copydata()
        self.add_to_path('uni;sub.p1.a1.g2:candidate(student2).d1')
        newdeadline = self.sub_p1_a1_g2_d1
        copy = delivery.copy(newdeadline)

        self.assertEquals(delivery.filemetas.count(), 1)
        self.assertEquals(copy.filemetas.count(), 1)
        copied_filemeta = copy.filemetas.all()[0]
        self.assertEquals(copied_filemeta.get_all_data_as_string(),
                          'Hello world')


    def test_copy_feedbacks(self):
        delivery, old_delivery = self._create_copydata()
        self.add_feedback(delivery=delivery,
                          verdict={'grade': 'F', 'points':10, 'is_passing_grade':False},
                          rendered_view='This was bad',
                          timestamp=datetime(2005, 1, 1, 0, 0, 0))
        self.add_feedback(delivery=delivery,
                          verdict={'grade': 'C', 'points':40, 'is_passing_grade':True},
                          rendered_view='Better',
                          timestamp=datetime(2010, 1, 1, 0, 0, 0))

        self.add_to_path('uni;sub.p1.a1.g2:candidate(student2).d1')
        newdeadline = self.sub_p1_a1_g2_d1
        self.assertEquals(delivery.feedbacks.count(), 2)
        copy = delivery.copy(newdeadline)

        self.assertEquals(delivery.feedbacks.count(), 2)
        feedbacks = copy.feedbacks.order_by('save_timestamp')
        self.assertEquals(len(feedbacks), 2)
        self.assertEquals(feedbacks[0].grade, 'F')
        self.assertEquals(feedbacks[0].points, 10)
        self.assertEquals(feedbacks[0].is_passing_grade, False)
        self.assertEquals(feedbacks[0].save_timestamp, datetime(2005, 1, 1, 0, 0, 0))
        self.assertEquals(feedbacks[0].rendered_view, 'This was bad')

        self.assertEquals(feedbacks[1].grade, 'C')
        self.assertEquals(feedbacks[1].points, 40)
        self.assertEquals(feedbacks[1].is_passing_grade, True)
        self.assertEquals(feedbacks[1].save_timestamp, datetime(2010, 1, 1, 0, 0, 0))
        self.assertEquals(feedbacks[1].rendered_view, 'Better')
