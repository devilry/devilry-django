from django.test import TestCase
from django.contrib.auth.models import User

from ....simplified import PermissionDenied
from ...core import models
from ...core import pluginloader
from ..simplified import Subject, Period, Assignment, AssignmentGroup, Delivery, Feedback


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
        qrywrap = Subject.search(examiner0)
        self.assertEquals(len(qrywrap), len(subjects))
        self.assertEquals(qrywrap[0]['short_name'], subjects[0].short_name)

        # query
        qrywrap = Subject.search(examiner0, query="duck1")
        self.assertEquals(len(qrywrap), 2)
        qrywrap = Subject.search(examiner0, query="duck")
        self.assertEquals(len(qrywrap), len(subjects))
        qrywrap = Subject.search(examiner0, query="1100")
        self.assertEquals(len(qrywrap), 1)

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
        qrywrap = Period.search(examiner0)
        self.assertEquals(len(qrywrap), len(periods))
        self.assertEquals(qrywrap[0]['short_name'], periods[0].short_name)

        # query
        qrywrap = Period.search(examiner0, query="fall01")
        self.assertEquals(len(qrywrap), 2)
        qrywrap = Period.search(examiner0, query="duck1")
        self.assertEquals(len(qrywrap), 2)

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
        qrywrap = Assignment.search(examiner0)
        self.assertEquals(len(qrywrap), len(all_assignments))
        self.assertEquals(qrywrap[0]['short_name'], all_assignments[0].short_name)

        # query
        qrywrap = Assignment.search(examiner0, query="ek")
        self.assertEquals(len(qrywrap), 9)
        qrywrap = Assignment.search(examiner0, query="fall0")
        self.assertEquals(len(qrywrap), 5)
        qrywrap = Assignment.search(examiner0, query="1100")
        self.assertEquals(len(qrywrap), 4)

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
#TODO fix handling of anonymous assignments
    def setUp(self):
        super(TestSimplifiedExaminerAssignmentGroup, self).setUp()
        duck3580_fall01_week1_core = self.duck3580_core.periods.get(
                short_name='fall01').assignments.get(short_name='week1')
        self.group_core = duck3580_fall01_week1_core.assignmentgroups.all()[0]

    def test_search(self):
        assignment = models.Assignment.published_where_is_examiner(self.duck3580examiner)[0]

        qrywrap = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                orderby=["-id"], limit=2)
        self.assertEquals(assignment.assignmentgroups.order_by('-id')[0].id, qrywrap[0]['id'])
        self.assertTrue(qrywrap[0]['id'] > qrywrap[1]['id'])
        self.assertEquals(qrywrap.count(), 2)

        qrywrap = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                query="student0")
        self.assertEquals(qrywrap.count(), 1)
        qrywrap = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                query="thisisatest")
        self.assertEquals(qrywrap.count(), 0)

        g = AssignmentGroup.search(self.duck3580examiner, assignment=assignment)._insecure_django_qryset[0]
        g.name = "thisisatest"
        g.save()
        qrywrap = AssignmentGroup.search(self.duck3580examiner, assignment=assignment.id,
                query="thisisatest")
        self.assertEquals(qrywrap.count(), 1)

    def test_search_security(self):
        assignment = models.Assignment.published_where_is_examiner(self.duck3580examiner)[0]

        result = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                orderby=["-id"], limit=2)
        qrywrap = result
        self.assertEquals(result.resultfields, ('id', 'name'))
        self.assertEquals(result.searchfields, ['name',
                        'candidates__candidate_id', 
                        'parentnode__short_name', #assignment
                        'parentnode__long_name', #assignment
                        'parentnode__parentnode__short_name', #period
                        'parentnode__parentnode__long_name', #period
                        'parentnode__parentnode__parentnode__short_name', #subject 
                        'parentnode__parentnode__parentnode__long_name',
                        'candidates__student__username'])

        qrywrap = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                query="student0") #assignment is not anonymous so can search for username
        self.assertEquals(qrywrap.count(), 1)

        assignment.anonymous = True
        assignment.save()
        result = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id)
        self.assertEquals(result.searchfields, ('name', 
                        'candidates__candidate_id',
                        'parentnode__short_name', #assignment
                        'parentnode__long_name', #assignment
                        'parentnode__parentnode__short_name', #period
                        'parentnode__parentnode__long_name', #period
                        'parentnode__parentnode__parentnode__short_name', #subject 
                        'parentnode__parentnode__parentnode__long_name'))

        qrywrap = AssignmentGroup.search(self.duck3580examiner,
                assignment=assignment.id,
                query="student0") # Should not be able to search for username on anonymous
        self.assertEquals(qrywrap.count(), 0)

    def test_read(self):
        duck3580_group = AssignmentGroup.read(self.duck3580examiner, self.group_core.id)
        self.assertEquals(duck3580_group, dict(
                id = self.group_core.id,
                name = None))

        #read with fieldgroup assignment
        duck3580_group = AssignmentGroup.read(self.duck3580examiner, self.group_core.id,
                result_fieldgroups=['assignment'])
        self.assertEquals(duck3580_group, dict(
                id=self.group_core.id,
                name = None,
                parentnode__long_name=
                self.group_core.parentnode.long_name,
                parentnode__short_name=
                self.group_core.parentnode.short_name,
                parentnode__id=
                self.group_core.parentnode.id))

        #read with fieldgroup period
        duck3580_group = AssignmentGroup.read(self.duck3580examiner, self.group_core.id,
                result_fieldgroups=['period'])
        self.assertEquals(duck3580_group, dict(
                id=self.group_core.id,
                name = None,
                parentnode__parentnode__long_name=
                self.group_core.parentnode.parentnode.long_name,
                parentnode__parentnode__short_name=
                self.group_core.parentnode.parentnode.short_name,
                parentnode__parentnode__id=
                self.group_core.parentnode.parentnode.id))  

        #read with fieldgroup subject
        duck3580_group = AssignmentGroup.read(self.duck3580examiner, self.group_core.id,
                result_fieldgroups=['subject'])
        self.assertEquals(duck3580_group, dict(
                id=self.group_core.id,
                name = None,
                parentnode__parentnode__parentnode__long_name=
                self.group_core.parentnode.parentnode.parentnode.long_name,
                parentnode__parentnode__parentnode__short_name=
                self.group_core.parentnode.parentnode.parentnode.short_name,
                parentnode__parentnode__parentnode__id=
                self.group_core.parentnode.parentnode.parentnode.id))            

    def test_read_security(self):
        with self.assertRaises(PermissionDenied):
            group = AssignmentGroup.read(self.testexaminerNoPerm, self.group_core.id)
        with self.assertRaises(PermissionDenied):
            group = AssignmentGroup.read(self.duck1080examiner, self.group_core.id)
        with self.assertRaises(PermissionDenied):
            group = AssignmentGroup.read(self.superadmin, self.group_core.id)

        group = AssignmentGroup.read(self.duck3580examiner, self.group_core.id)
        #print group.keys()
        #TODO get help with this
"""
        assignment = models.Assignment.published_where_is_examiner(self.duck3580examiner)[0]
        group = AssignmentGroup.read(self.duck3580examiner,assignment.id)
        print group
        assignment.anonymous = True
        assignment.save()
        group = AssignmentGroup.read(self.duck3580examiner,assignment.id)
        print group
"""
class TestSimplifiedExaminerDelivery(SimplifiedExaminerTestCase):
#TODO anonymous deliveries

    def setUp(self):
        super(TestSimplifiedExaminerDelivery, self).setUp()
        #assingment
        self.duck3580_fall01_week1_core = self.duck3580_core.periods.get(
                short_name='fall01').assignments.get(short_name='week1')
        #single delivery
        self.delivery_duck3580_core = self.duck3580_fall01_week1_core.assignmentgroups.all()[0].deliveries.all()[0] 

    def test_search(self):
        examiner0 =  User.objects.get(username="examiner0")
        #deliveries where examiner 0 is examiner
        deliveries = models.Delivery.published_where_is_examiner(examiner0)

        #search for all deliveries where examiner0 is examiner
        qrywrap = Delivery.search(examiner0)
        #number of deliveries
        self.assertEquals(len(qrywrap), len(deliveries))         
        #delivery number
        self.assertEquals(qrywrap[5]['number'], deliveries[5].number) 
        #compare deliveries
        self.assertEquals(qrywrap[2]['id'], deliveries[2].id) 

        #search period
        qrywrap = Delivery.search(examiner0, query="fall01")
        self.assertEquals(len(qrywrap), 9)
        #search subject
        qrywrap = Delivery.search(examiner0, query="1100")
        self.assertEquals(len(qrywrap), 7)
        #search period
        qrywrap = Delivery.search(examiner0, query="week4")
        self.assertEquals(len(qrywrap), 2)

    def test_search_security(self):
        #search by examiner with no permission returns no hits
        result = Delivery.search(self.testexaminerNoPerm)
        self.assertEquals(len(result), 0)

        #open search resturns only deliveries where the examiner is examiner
        result = Delivery.search(self.duck3580examiner)
        deliveries = models.Delivery.published_where_is_examiner(self.duck3580examiner)
        self.assertEquals(len(deliveries), len(result))

        #duck3580examiner searching for duck1100 returns no hits
        result = Delivery.search(self.duck3580examiner, query="duck1100")
        self.assertEquals(len(result), 0)

        #anonymous assignment
        self.duck3580_fall01_week1_core.anonymous = True
        self.duck3580_fall01_week1_core.save()
        result = Delivery.search(self.duck3580examiner, query=("fall01"), result_fieldgroups=["assignment"])

        #TODO fix handling of anonymous assignments
        #print len(result)
        #print result[1].assignment_group.parentnode.anonymous
        #print result[0]["assignment_group__parentnode__short_name"]
        #print result[0]["assignment_group__parentnode__anonymous"]
        #delivery = result[0]["delivered_by"]
        #print delivery
        #print result

    def test_read(self):
        duck3580_delivery = Delivery.read(self.duck3580examiner, self.delivery_duck3580_core.id)
        self.assertEquals(duck3580_delivery, dict(
            time_of_delivery = self.delivery_duck3580_core.time_of_delivery,
            number = self.delivery_duck3580_core.number,
            delivered_by = self.delivery_duck3580_core.delivered_by,
            id=self.delivery_duck3580_core.id))

        #read with fieldgroup subject
        duck3580_delivery = Delivery.read(self.duck3580examiner, self.delivery_duck3580_core.id,
                result_fieldgroups=['subject'])
        self.assertEquals(duck3580_delivery, dict(
            time_of_delivery=self.delivery_duck3580_core.time_of_delivery,
            number=self.delivery_duck3580_core.number,
            delivered_by=self.delivery_duck3580_core.delivered_by,
            id=self.delivery_duck3580_core.id,
            assignment_group__parentnode__parentnode__parentnode__long_name=
                self.delivery_duck3580_core.assignment_group.parentnode.parentnode.parentnode.long_name,
            assignment_group__parentnode__parentnode__parentnode__short_name=
                self.delivery_duck3580_core.assignment_group.parentnode.parentnode.parentnode.short_name,
            assignment_group__parentnode__parentnode__parentnode__id=
                self.delivery_duck3580_core.assignment_group.parentnode.parentnode.parentnode.id))

        #read with fieldgroup period
        duck3580_delivery = Delivery.read(self.duck3580examiner, self.delivery_duck3580_core.id,
                result_fieldgroups=['period'])
        self.assertEquals(duck3580_delivery, dict(
            time_of_delivery=self.delivery_duck3580_core.time_of_delivery,
            number=self.delivery_duck3580_core.number,
            delivered_by=self.delivery_duck3580_core.delivered_by,
            id=self.delivery_duck3580_core.id,
            assignment_group__parentnode__parentnode__long_name=
                self.delivery_duck3580_core.assignment_group.parentnode.parentnode.long_name,
            assignment_group__parentnode__parentnode__short_name=
                self.delivery_duck3580_core.assignment_group.parentnode.parentnode.short_name,
            assignment_group__parentnode__parentnode__id=
                self.delivery_duck3580_core.assignment_group.parentnode.parentnode.id))

        #read with fieldgroup assignment
        duck3580_delivery = Delivery.read(self.duck3580examiner, self.delivery_duck3580_core.id,
                result_fieldgroups=['assignment'])
        self.assertEquals(duck3580_delivery, dict(
            time_of_delivery=self.delivery_duck3580_core.time_of_delivery,
            number=self.delivery_duck3580_core.number,
            delivered_by=self.delivery_duck3580_core.delivered_by,
            id=self.delivery_duck3580_core.id,
            assignment_group__parentnode__long_name=
                self.delivery_duck3580_core.assignment_group.parentnode.long_name,
            assignment_group__parentnode__short_name=
                self.delivery_duck3580_core.assignment_group.parentnode.short_name,
            assignment_group__parentnode__id=
                self.delivery_duck3580_core.assignment_group.parentnode.id))
            
    def test_read_security(self):
        with self.assertRaises(PermissionDenied):
            delivery = Delivery.read(self.testexaminerNoPerm, self.delivery_duck3580_core.id)
        with self.assertRaises(PermissionDenied):
            delivery = Delivery.read(self.duck1080examiner, self.delivery_duck3580_core.id)
        with self.assertRaises(PermissionDenied):
            delivery = Delivery.read(self.superadmin, self.delivery_duck3580_core.id)

class TestSimplifiedExaminerFeedback(SimplifiedExaminerTestCase):
#TODO fix handling of anonymous assignments
    def setUp(self):
        super(TestSimplifiedExaminerFeedback, self).setUp()
        self.duck1100_feedback_core = self.duck1100_core.periods.get(
                short_name='spring01').assignments.get(
                short_name='week1').assignmentgroups.all()[0].deliveries.all()[0].feedback

    def test_read(self):
        duck1100_feedback = Feedback.read(self.duck1100examiner, self.duck1100_feedback_core.id)
        self.assertEquals(duck1100_feedback, dict(
            delivery=self.duck1100_feedback_core.delivery,
            text=self.duck1100_feedback_core.text,
            format=self.duck1100_feedback_core.format,
            id=self.duck1100_feedback_core.id))

        #read with fieldgroup subject
        duck1100_feedback = Feedback.read(self.duck1100examiner, self.duck1100_feedback_core.id,
                result_fieldgroups=['subject'])
        self.assertEquals(duck1100_feedback, dict(
            delivery=self.duck1100_feedback_core.delivery,
            text=self.duck1100_feedback_core.text,
            format=self.duck1100_feedback_core.format,
            id=self.duck1100_feedback_core.id,
            delivery__assignment_group__parentnode__parentnode__parentnode__long_name=
                self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.parentnode.long_name,
            delivery__assignment_group__parentnode__parentnode__parentnode__short_name=
                self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.parentnode.short_name,
            delivery__assignment_group__parentnode__parentnode__parentnode__id=
                self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.parentnode.id))

        #read with fieldgroup period
        duck1100_feedback = Feedback.read(self.duck1100examiner, self.duck1100_feedback_core.id,
                result_fieldgroups=['period'])
        self.assertEquals(duck1100_feedback, dict(
            delivery=self.duck1100_feedback_core.delivery,
            text=self.duck1100_feedback_core.text,
            format=self.duck1100_feedback_core.format,
            id=self.duck1100_feedback_core.id,
            delivery__assignment_group__parentnode__parentnode__long_name=
                self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.long_name,
            delivery__assignment_group__parentnode__parentnode__short_name=
                self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.short_name,
            delivery__assignment_group__parentnode__parentnode__id=
                self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.id))

        #read with fieldgroup assignment
        duck1100_feedback = Feedback.read(self.duck1100examiner, self.duck1100_feedback_core.id,
                result_fieldgroups=['assignment'])
        self.assertEquals(duck1100_feedback, dict(
            delivery=self.duck1100_feedback_core.delivery,
            text=self.duck1100_feedback_core.text,
            format=self.duck1100_feedback_core.format,
            id=self.duck1100_feedback_core.id,
            delivery__assignment_group__parentnode__long_name=
                self.duck1100_feedback_core.delivery.assignment_group.parentnode.long_name,
            delivery__assignment_group__parentnode__short_name=
                self.duck1100_feedback_core.delivery.assignment_group.parentnode.short_name,
            delivery__assignment_group__parentnode__id=
                self.duck1100_feedback_core.delivery.assignment_group.parentnode.id))

    def test_read_security(self):
        with self.assertRaises(PermissionDenied):
            Feedback.read(self.testexaminerNoPerm, self.duck1100_feedback_core.id)
        with self.assertRaises(PermissionDenied):
            Feedback.read(self.duck3580examiner, self.duck1100_feedback_core.id)
        with self.assertRaises(PermissionDenied):
            Feedback.read(self.superadmin, self.duck1100_feedback_core.id) #TODO correct?

    def test_search(self):
        examiner0 = User.objects.get(username="examiner0")
        #examiner0s feedbacks
        feedbacks = models.Feedback.published_where_is_examiner(examiner0)

        #seach for all feedbacks where examiner0 is examiner
        qrywrap = Feedback.search(examiner0)
        self.assertEquals(len(qrywrap), len(feedbacks))
        self.assertEquals(qrywrap[1]['id'], feedbacks[1].id)

        #search period
        qrywrap = Feedback.search(examiner0, query="spring01")
        self.assertEquals(len(qrywrap), 5)
        #search subject
        qrywrap = Feedback.search(examiner0, query="duck3580")
        self.assertEquals(len(qrywrap), 4)
        #search period
        qrywrap = Feedback.search(examiner0, query="week3")
        self.assertEquals(len(qrywrap), 2)

    def test_search_security(self):
        #search by examiner with no permission returns no hits
        result = Feedback.search(self.testexaminerNoPerm)
        self.assertEquals(len(result), 0)

        #open search resturns only deliveries where the examiner is examiner
        result = Feedback.search(self.duck3580examiner)
        duck3580_feedbacks = models.Feedback.published_where_is_examiner(self.duck3580examiner)
        self.assertEquals(len(duck3580_feedbacks), len(result))

        #duck3580examiner searching for duck1100 returns no hits
        result = Feedback.search(self.duck3580examiner, query="duck1100")
        self.assertEquals(len(result), 0)

    def test_create(self):
        #TODO
        pass

    def test_ceate_security(self):
        #TODO
        pass
    #TODO tests for delete and update also?

