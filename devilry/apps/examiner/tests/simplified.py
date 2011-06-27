from django.test import TestCase
from django.contrib.auth.models import User

from ....simplified import PermissionDenied
from ...core import models
from ...core import pluginloader
from ..simplified import Subject, Period, Assignment, AssignmentGroup, Delivery


pluginloader.autodiscover()


class SimplifiedExaminerTestCase(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.duck1100_core = models.Subject.objects.get(short_name='duck1100')
        self.duck1080_core = models.Subject.objects.get(short_name='duck1080')
        self.duck3580_core = models.Subject.objects.get(short_name='duck3580')

        self.duck1100examiner = User(username='duck1100examiner')
        self.duck1100examiner.save()
        self.duck1100_core.periods.all()[0].assignments.all()[0].assignmentgroups.all()[0].examiners.add(self.duck1100examiner)

        self.duck1080examiner = User(username='duck1080examiner')
        self.duck1080examiner.save()
        self.duck1080_core.periods.all()[0].assignments.all()[0].assignmentgroups.all()[0].examiners.add(self.duck1080examiner)

        self.duck3580examiner = User(username='duck3580examiner')
        self.duck3580examiner.save()
        for group in self.duck3580_core.periods.all()[0].assignments.all()[0].assignmentgroups.all():
            group.examiners.add(self.duck3580examiner)

        self.testexaminerNoPerm = User(username='testuserNoPerm')
        self.testexaminerNoPerm.save()
        self.superadmin = User.objects.get(username='grandma')
        self.assertTrue(self.superadmin.is_superuser)


class TestSimplifiedExaminerSubject(SimplifiedExaminerTestCase):

    def test_search(self):
        examiner0 = User.objects.get(username="examiner0")
        subjects = models.Subject.published_where_is_examiner(examiner0).order_by("short_name")
        qryset = Subject.search(examiner0).qryset
        self.assertEquals(len(qryset), len(subjects))
        self.assertEquals(qryset[0].short_name, subjects[0].short_name)

        # query
        qryset = Subject.search(examiner0, query="duck1").qryset
        self.assertEquals(len(qryset), 2)
        qryset = Subject.search(examiner0, query="duck").qryset
        self.assertEquals(len(qryset), len(subjects))
        qryset = Subject.search(examiner0, query="1100").qryset
        self.assertEquals(len(qryset), 1)

    def test_read(self):
        duck1100 = Subject.read(self.duck1100examiner, self.duck1100_core.id)
        self.assertEquals(duck1100, dict(
                short_name = 'duck1100',
                long_name = self.duck1100_core.long_name,
                id = self.duck1100_core.id))

    def test_read_security(self):
        with self.assertRaises(PermissionDenied):
            duck1100 = Subject.read(self.testexaminerNoPerm, self.duck1100_core.id)
        with self.assertRaises(PermissionDenied):
            duck1100 = Subject.read(self.duck1080examiner, self.duck1100_core.id)
        with self.assertRaises(PermissionDenied):
            duck1100 = Subject.read(self.superadmin, self.duck1100_core.id)


class TestSimplifiedExaminerPeriod(SimplifiedExaminerTestCase):
    def setUp(self):
        super(TestSimplifiedExaminerPeriod, self).setUp()
        self.duck1100_spring01_core = self.duck1100_core.periods.get(short_name='spring01')

    def test_search(self):
        examiner0 = User.objects.get(username="examiner0")
        periods = models.Period.published_where_is_examiner(examiner0).order_by("short_name")
        qryset = Period.search(examiner0).qryset
        self.assertEquals(len(qryset), len(periods))
        self.assertEquals(qryset[0].short_name, periods[0].short_name)

        # query
        qryset = Period.search(examiner0, query="fall01").qryset
        self.assertEquals(len(qryset), 2)
        qryset = Period.search(examiner0, query="duck1").qryset
        self.assertEquals(len(qryset), 2)

    def test_read(self):
        duck1100_spring01 = Period.read(self.duck1100examiner, self.duck1100_spring01_core.id)
        self.assertEquals(duck1100_spring01, dict(
                id = self.duck1100_spring01_core.id,
                short_name = 'spring01',
                long_name = self.duck1100_spring01_core.long_name,
                parentnode__id = self.duck1100_spring01_core.parentnode_id))

        duck1100_spring01 = Period.read(self.duck1100examiner,
                self.duck1100_spring01_core.id,
                result_fieldgroups=['subject'])
        self.assertEquals(duck1100_spring01, dict(
                id = self.duck1100_spring01_core.id,
                short_name = 'spring01',
                long_name = self.duck1100_spring01_core.long_name,
                parentnode__id = self.duck1100_spring01_core.parentnode_id,
                parentnode__short_name = self.duck1100_spring01_core.parentnode.short_name,
                parentnode__long_name = self.duck1100_spring01_core.parentnode.long_name))

    def test_read_security(self):
        with self.assertRaises(PermissionDenied):
            duck1100_spring01 = Period.read(self.testexaminerNoPerm, self.duck1100_spring01_core.id)
        with self.assertRaises(PermissionDenied):
            duck1100_spring01 = Period.read(self.duck1080examiner, self.duck1100_spring01_core.id)
        with self.assertRaises(PermissionDenied):
            duck1100_spring01 = Period.read(self.superadmin, self.duck1100_spring01_core.id)


class TestSimplifiedExaminerAssignment(SimplifiedExaminerTestCase):
    def setUp(self):
        super(TestSimplifiedExaminerAssignment, self).setUp()
        self.duck1100_spring01_week1_core = self.duck1100_core.periods.get(
                short_name='spring01').assignments.get(short_name='week1')

    def test_search(self):
        examiner0 = User.objects.get(username="examiner0")
        all_assignments = models.Assignment.objects.all().order_by("short_name")
        qryset = Assignment.search(examiner0).qryset
        self.assertEquals(len(qryset), len(all_assignments))
        self.assertEquals(qryset[0].short_name, all_assignments[0].short_name)

        # query
        qryset = Assignment.search(examiner0, query="ek").qryset
        self.assertEquals(len(qryset), 9)
        qryset = Assignment.search(examiner0, query="fall0").qryset
        self.assertEquals(len(qryset), 5)
        qryset = Assignment.search(examiner0, query="1100").qryset
        self.assertEquals(len(qryset), 4)

    def test_read(self):
        duck1100_spring01_week1 = Assignment.read(self.duck1100examiner,
                self.duck1100_spring01_week1_core.id)
        self.assertEquals(duck1100_spring01_week1, dict(
                id = self.duck1100_spring01_week1_core.id,
                short_name = 'week1',
                long_name = self.duck1100_spring01_week1_core.long_name,
                parentnode__id=self.duck1100_spring01_week1_core.parentnode.id))

        duck1100_spring01_week1 = Assignment.read(self.duck1100examiner,
                self.duck1100_spring01_week1_core.id,
                result_fieldgroups=['period'])
        self.assertEquals(duck1100_spring01_week1, dict(
                id = self.duck1100_spring01_week1_core.id,
                short_name = 'week1',
                long_name = self.duck1100_spring01_week1_core.long_name,
                parentnode__id=self.duck1100_spring01_week1_core.parentnode.id,
                parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.short_name,
                parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.long_name,
                parentnode__parentnode__id=self.duck1100_spring01_week1_core.parentnode.parentnode_id))

        duck1100_spring01_week1 = Assignment.read(self.duck1100examiner,
                self.duck1100_spring01_week1_core.id,
                result_fieldgroups=['period', 'subject'])
        self.assertEquals(duck1100_spring01_week1, dict(
                id = self.duck1100_spring01_week1_core.id,
                short_name = 'week1',
                long_name = self.duck1100_spring01_week1_core.long_name,
                parentnode__id=self.duck1100_spring01_week1_core.parentnode.id,
                parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.short_name,
                parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.long_name,
                parentnode__parentnode__id=self.duck1100_spring01_week1_core.parentnode.parentnode_id,
                parentnode__parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.parentnode.short_name,
                parentnode__parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.parentnode.long_name))

    def test_read_security(self):
        with self.assertRaises(PermissionDenied):
            duck1100_spring01_week1 = Period.read(self.testexaminerNoPerm, self.duck1100_spring01_week1_core.id)
        with self.assertRaises(PermissionDenied):
            duck1100_spring01_week1 = Period.read(self.duck1080examiner, self.duck1100_spring01_week1_core.id)
        with self.assertRaises(PermissionDenied):
            duck1100_spring01_week1 = Period.read(self.superadmin, self.duck1100_spring01_week1_core.id)



class TestSimplifiedExaminerAssignmentGroup(SimplifiedExaminerTestCase):

    def setUp(self):
        super(TestSimplifiedExaminerAssignmentGroup, self).setUp()
        duck3580_fall01_week1_core = self.duck3580_core.periods.get(
                short_name='fall01').assignments.get(short_name='week1')
        self.group_core = duck3580_fall01_week1_core.assignmentgroups.all()[0]
    def test_search(self):
        assignment = models.Assignment.published_where_is_examiner(self.duck3580examiner)[0]

        result = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                orderby=["-id"], limit=2)
        qryset = result.qryset
        self.assertEquals(assignment.id, qryset[0].parentnode.id)
        self.assertTrue(qryset[0].id > qryset[1].id)
        self.assertEquals(qryset.count(), 2)

        qryset = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                query="student0").qryset
        self.assertEquals(qryset.count(), 1)
        qryset = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                query="thisisatest").qryset
        self.assertEquals(qryset.count(), 0)

        g = AssignmentGroup.search(self.duck3580examiner, assignment=assignment).qryset[0]
        g.name = "thisisatest"
        g.save()
        qryset = AssignmentGroup.search(self.duck3580examiner, assignment=assignment.id,
                query="thisisatest").qryset
        self.assertEquals(qryset.count(), 1)

    def test_search_security(self):
        assignment = models.Assignment.published_where_is_examiner(self.duck3580examiner)[0]

        result = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                orderby=["-id"], limit=2)
        qryset = result.qryset
        self.assertEquals(result.resultfields, ['id', 'name'])
        self.assertEquals(result.searchfields, ['name',
            'candidates__candidate_id', 'candidates__student__username'])

        assignment.anonymous = True
        assignment.save()
        result = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id)
        self.assertEquals(result.searchfields, ['name', 'candidates__candidate_id'])

        qryset = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                query="student0").qryset # Should not be able to search for username on anonymous
        self.assertEquals(qryset.count(), 0)


    def test_read(self):
        group = AssignmentGroup.read(self.duck3580examiner, self.group_core.id)
        self.assertEquals(group, dict(
                id = self.group_core.id,
                name = None))

    def test_read_security(self):
        with self.assertRaises(PermissionDenied):
            group = AssignmentGroup.read(self.testexaminerNoPerm, self.group_core.id)
        with self.assertRaises(PermissionDenied):
            group = AssignmentGroup.read(self.duck1080examiner, self.group_core.id)
        with self.assertRaises(PermissionDenied):
            group = AssignmentGroup.read(self.superadmin, self.group_core.id)

class TestSimplifiedExaminerDelivery(SimplifiedExaminerTestCase):

    def setUp(self):
        super(TestSimplifiedExaminerDelivery, self).setUp()
        duck3580_fall01_week1_core = self.duck3580_core.periods.get(
                short_name='fall01').assignments.get(short_name='week1') #assingment group
        self.delivery_duck3580 = duck3580_fall01_week1_core.assignmentgroups.all()[0].deliveries.all()[0] #single delivery
        
    def test_search(self):
        pass
    """
        deliveries = models.Delivery.published_where_is_examiner(self.duck3580examiner)[0]
        qryset = Delivery.search()
"""
    def test_search_security(self):
        pass

    def test_read(self):
        delivery = Delivery.read(self.duck3580examiner, self.delivery_duck3580.id)
        self.assertEquals(delivery, dict(
            time_of_delivery = self.delivery_duck3580.time_of_delivery,
            number = self.delivery_duck3580.number,
            delivered_by = self.delivery_duck3580.delivered_by))

    def test_read_security(self):
        with self.assertRaises(PermissionDenied):
            delivery = Delivery.read(self.testexaminerNoPerm, self.delivery_duck3580.id)
        with self.assertRaises(PermissionDenied):
            delivery = Delivery.read(self.duck1080examiner, self.delivery_duck3580.id)
        with self.assertRaises(PermissionDenied):
            delivery = Delivery.read(self.superadmin, self.delivery_duck3580.id)

