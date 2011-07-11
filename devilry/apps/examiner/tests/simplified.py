# from django.test import TestCase
from django.contrib.auth.models import User

# from ....simplified import PermissionDenied
from ...core import models
# from ...core import pluginloader
# from ..simplified import SimplifiedSubject, SimplifiedPeriod, SimplifiedAssignment, SimplifiedAssignmentGroup, Delivery, Feedback
from django.test import TestCase

from ....simplified import PermissionDenied
from ....simplified.utils import modelinstance_to_dict

from ...core import testhelper
from ...core import pluginloader
from ..simplified import (  # SimplifiedDelivery,
    # SimplifiedStaticFeedback,
    SimplifiedAssignment,
    SimplifiedAssignmentGroup, SimplifiedPeriod, SimplifiedSubject,
    SimplifiedExaminerDeadline)

import re


pluginloader.autodiscover()


# class SimplifiedExaminerTestCase(TestCase):
#     fixtures = ["simplified/data.json"]

#     def setUp(self):
#         self.duck1100_core = models.Subject.objects.get(short_name='duck1100')
#         self.duck1080_core = models.Subject.objects.get(short_name='duck1080')
#         self.duck3580_core = models.Subject.objects.get(short_name='duck3580')

#         self.duck1100examiner = User(username='duck1100examiner')
#         self.duck1100examiner.save()
#         self.duck1100_core.periods.all()[0].assignments.all()[0].assignmentgroups.all()[0].examiners.add(self.duck1100examiner)

#         self.duck1080examiner = User(username='duck1080examiner')
#         self.duck1080examiner.save()
#         self.duck1080_core.periods.all()[0].assignments.all()[0].assignmentgroups.all()[0].examiners.add(self.duck1080examiner)

#         self.duck3580examiner = User(username='duck3580examiner')
#         self.duck3580examiner.save()
#         for group in self.duck3580_core.periods.all()[0].assignments.all()[0].assignmentgroups.all():
#             group.examiners.add(self.duck3580examiner)

#         self.testexaminerNoPerm = User(username='testuserNoPerm')
#         self.testexaminerNoPerm.save()
#         self.superadmin = User.objects.get(username='grandma')
#         self.assertTrue(self.superadmin.is_superuser)

class SimplifiedExaminerTestBase(TestCase, testhelper.TestHelper):

    def setUp(self):
        # create a base structure
        self.add(nodes='uni:admin(admin)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstSem', 'secondSem'],
                 assignments=['a1', 'a2'])

        # add firstStud to the first and secondSem assignments
        self.add_to_path('uni;inf101.firstSem.a1.g1:candidate(firstStud):examiner(firstExam)')
        self.add_to_path('uni;inf101.firstSem.a2.g1:candidate(firstStud):examiner(firstExam)')
        self.add_to_path('uni;inf110.secondSem.a1.g1:candidate(firstStud):examiner(firstExam)')
        self.add_to_path('uni;inf110.secondSem.a2.g1:candidate(firstStud):examiner(firstExam)')
        self.add_to_path('uni;inf110.secondSem.a3:anon(true).g1:candidate(firstStud):examiner(firstExam)')

        # secondStud began secondSem
        self.add_to_path('uni;inf101.secondSem.a1.g2:candidate(secondStud);examiner(secondExam)')
        self.add_to_path('uni;inf101.secondSem.a2.g2:candidate(secondStud):examiner(secondExam)')


class TestSimplifiedExaminerSubject(SimplifiedExaminerTestBase):

    def setUp(self):
        super(TestSimplifiedExaminerSubject, self).setUp()

    def test_search(self):
        # do an empty search to get all subjects firstExam examines
        search_res = SimplifiedSubject.search(self.firstExam)
        expected_res = [modelinstance_to_dict(self.inf101, SimplifiedSubject.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110, SimplifiedSubject.Meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # do a search with query inf101
        search_res = SimplifiedSubject.search(self.firstExam, query='inf101')
        expected_res = modelinstance_to_dict(self.inf101, SimplifiedSubject.Meta.resultfields.aslist())

        self.assertEquals(search_res.count(), 1)
        self.assertEquals(search_res[0], expected_res)

        # do a search with partial query
        search_res = SimplifiedSubject.search(self.firstExam, query='inf10')
        expected_res = modelinstance_to_dict(self.inf101, SimplifiedSubject.Meta.resultfields.aslist())

        self.assertEquals(search_res.count(), 1)
        self.assertEquals(search_res[0], expected_res)

    def test_read(self):
        # read firstsem without extra fields
        read_res = SimplifiedSubject.read(self.firstExam, self.inf101.id)
        expected_res = modelinstance_to_dict(self.inf101, SimplifiedSubject.Meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):
        # check that an examiner can't read a subject he's not signed
        # up for
        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.read(self.admin, self.inf101.id)

        # add another student, to inf110, but not inf101
        self.add_to_path('uni;inf110.firstSem.a1.g3:candidate(thirdStud)')
        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.read(self.thirdStud, self.inf101.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.read(self.secondExam, self.inf110.id)

        # TODO: Examiner history?
        # self.add_to_path('uni;inf102.oldSem:begins(-10).a1.g2:candidate(fourthStud):examiner(thirdExam)')
        # print self.inf102_oldSem.end_time

        # with self.assertRaises(PermissionDenied):
        #     SimplifiedSubject.read(self.thirdExam, self.inf102.id)


class TestSimplifiedExaminerPeriod(SimplifiedExaminerTestBase):

    allExtras = SimplifiedPeriod.Meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedExaminerPeriod, self).setUp()

    def test_search(self):

        # search with no query and no extra fields
        search_res = SimplifiedPeriod.search(self.firstExam)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem, SimplifiedPeriod.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem, SimplifiedPeriod.Meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), 2)
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedPeriod.search(self.firstExam, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem, SimplifiedPeriod.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem, SimplifiedPeriod.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedPeriod.search(self.firstExam, query='inf101')
        expected_res = modelinstance_to_dict(self.inf101_firstSem, SimplifiedPeriod.Meta.resultfields.aslist())

        self.assertEquals(search_res.count(), 1)
        self.assertEquals(search_res[0], expected_res)

        # with query and extra fields
        search_res = SimplifiedPeriod.search(self.firstExam, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem, SimplifiedPeriod.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # read firstsem without extra fields
        read_res = SimplifiedPeriod.read(self.firstExam, self.inf101_firstSem.id)
        expected_res = modelinstance_to_dict(self.inf101_firstSem, SimplifiedPeriod.Meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # read firstSem with extras fields
        read_res = SimplifiedPeriod.read(self.firstExam, self.inf101_firstSem.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstSem, SimplifiedPeriod.Meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # check that reading a non-existing id gives permission denied
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.read(self.firstStud, -1)

        # that secondStud can't read a period he's not in
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.read(self.secondStud, self.inf101_firstSem.id)


class TestSimplifiedExaminerAssignment(SimplifiedExaminerTestBase):

    allExtras = SimplifiedAssignment.Meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedExaminerAssignment, self).setUp()

    def test_search(self):

        # search with no query and no extra fields
        search_res = SimplifiedAssignment.search(self.firstExam)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstSem_a2, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a1, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a2, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a3, SimplifiedAssignment.Meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedAssignment.search(self.firstExam, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstSem_a2,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a1,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a2,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a3,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedAssignment.search(self.firstExam, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a1, SimplifiedAssignment.Meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedAssignment.search(self.firstExam, query='inf110', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondSem_a1,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a2,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a3,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedAssignment.read(self.firstExam, self.inf101_firstSem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1,
                                             SimplifiedAssignment.Meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedAssignment.read(self.firstExam, self.inf101_firstSem_a1.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1,
                                             SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for inf110. Assert that
        # he can't do a read on inf101's id
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.secondStud, self.inf110_firstSem_a1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.admin, self.inf101_firstSem_a1.id)


class TestSimplifiedExaminerAssignmentGroup(SimplifiedExaminerTestBase):

    allExtras = SimplifiedAssignmentGroup.Meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedExaminerAssignmentGroup, self).setUp()

    def test_search(self):

        self.firstExam = User.objects.get(id=self.firstExam.id)

        # search with no query and no extra fields
        search_res = SimplifiedAssignmentGroup.search(self.firstExam, query='firstStud')
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1, SimplifiedAssignmentGroup.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1, SimplifiedAssignmentGroup.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1, SimplifiedAssignmentGroup.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1, SimplifiedAssignmentGroup.Meta.resultfields.aslist()),
                        ]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedAssignmentGroup.search(self.firstExam, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1,
                                              SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1,
                                              SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1,
                                              SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1,
                                              SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a3_g1,
                                              SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedAssignmentGroup.search(self.firstExam, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1, SimplifiedAssignmentGroup.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1, SimplifiedAssignmentGroup.Meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedAssignmentGroup.search(self.firstExam, query='inf110', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondSem_a1_g1,
                                              SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1,
                                              SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a3_g1,
                                              SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedAssignmentGroup.read(self.firstExam, self.inf101_firstSem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1_g1,
                                             SimplifiedAssignmentGroup.Meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedAssignmentGroup.read(self.firstExam, self.inf101_firstSem_a1.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1_g1,
                                             SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for firstSem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.secondStud, self.inf101_firstSem_a1_g1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.admin, self.inf101_firstSem_a1_g1.id)

class TestSimplifiedExaminerSimplifiedDeadline(SimplifiedExaminerTestBase):
    def set_up(self):
        super(TestSimplifiedExaminerAssignmentGroup, self).setUp()

        self.add_to_path('uni;inf101.firstSem.a1.g1.dl.ends(5)')

    def test_search(self):
        search_res = SimplifiedExaminerDeadline.search(self.firstExam)
        print search_res

    def test_search_security(self):
        #TODO - complete this
        pass

    def test_read(self):
        read_res = SimplifiedExaminerDeadline.read(self.firstExam)
        print read_res

    def test_read_security(self):
        #TODO - complete this
        pass

    def test_create(self):
        #TODO 
        pass

    def test_create_security(self):
        #TODO 
        pass

    def test_update(self):
        #TODO 
        pass

    def test_update_security(self):
        #TODO 
        pass
# class TestSimplifiedExaminerSimplifiedSubject(SimplifiedExaminerTestCase):

#     def test_search(self):
#         examiner0 = User.objects.get(username="examiner0")
#         subjects = models.Subject.published_where_is_examiner(examiner0).order_by("short_name")
#         qrywrap = SimplifiedSubject.search(examiner0)
#         self.assertEquals(len(qrywrap), len(subjects))
#         self.assertEquals(qrywrap[0]['short_name'], subjects[0].short_name)

#         # query
#         qrywrap = SimplifiedSubject.search(examiner0, query="duck1")
#         self.assertEquals(len(qrywrap), 2)
#         qrywrap = SimplifiedSubject.search(examiner0, query="duck")
#         self.assertEquals(len(qrywrap), len(subjects))
#         qrywrap = SimplifiedSubject.search(examiner0, query="1100")
#         self.assertEquals(len(qrywrap), 1)

#     def test_read(self):
#         duck1100 = SimplifiedSubject.read(self.duck1100examiner, self.duck1100_core.id)
#         self.assertEquals(duck1100, dict(
#                 short_name = 'duck1100',
#                 long_name = self.duck1100_core.long_name,
#                 id = self.duck1100_core.id))

#     def test_read_security(self):
#         with self.assertRaises(PermissionDenied):
#             duck1100 = SimplifiedSubject.read(self.testexaminerNoPerm, self.duck1100_core.id)
#         with self.assertRaises(PermissionDenied):
#             duck1100 = SimplifiedSubject.read(self.duck1080examiner, self.duck1100_core.id)
#         with self.assertRaises(PermissionDenied):
#             duck1100 = SimplifiedSubject.read(self.superadmin, self.duck1100_core.id)


# class TestSimplifiedExaminerSimplifiedPeriod(SimplifiedExaminerTestCase):
#     def setUp(self):
#         super(TestSimplifiedExaminerSimplifiedPeriod, self).setUp()
#         self.duck1100_spring01_core = self.duck1100_core.periods.get(short_name='spring01')

#     def test_search(self):
#         examiner0 = User.objects.get(username="examiner0")
#         periods = models.Period.published_where_is_examiner(examiner0).order_by("short_name")
#         qrywrap = SimplifiedPeriod.search(examiner0)
#         self.assertEquals(len(qrywrap), len(periods))
#         self.assertEquals(qrywrap[0]['short_name'], periods[0].short_name)

#         # query
#         qrywrap = SimplifiedPeriod.search(examiner0, query="fall01")
#         self.assertEquals(len(qrywrap), 2)
#         qrywrap = SimplifiedPeriod.search(examiner0, query="duck1")
#         self.assertEquals(len(qrywrap), 2)

#     def test_read(self):
#         duck1100_spring01 = SimplifiedPeriod.read(self.duck1100examiner, self.duck1100_spring01_core.id)
#         self.assertEquals(duck1100_spring01, dict(
#                 id = self.duck1100_spring01_core.id,
#                 short_name = 'spring01',
#                 long_name = self.duck1100_spring01_core.long_name,
#                 parentnode__id = self.duck1100_spring01_core.parentnode_id))

#         duck1100_spring01 = SimplifiedPeriod.read(self.duck1100examiner,
#                 self.duck1100_spring01_core.id,
#                 result_fieldgroups=['subject'])
#         self.assertEquals(duck1100_spring01, dict(
#                 id = self.duck1100_spring01_core.id,
#                 short_name = 'spring01',
#                 long_name = self.duck1100_spring01_core.long_name,
#                 parentnode__id = self.duck1100_spring01_core.parentnode_id,
#                 parentnode__short_name = self.duck1100_spring01_core.parentnode.short_name,
#                 parentnode__long_name = self.duck1100_spring01_core.parentnode.long_name))

#     def test_read_security(self):
#         with self.assertRaises(PermissionDenied):
#             duck1100_spring01 = SimplifiedPeriod.read(self.testexaminerNoPerm, self.duck1100_spring01_core.id)
#         with self.assertRaises(PermissionDenied):
#             duck1100_spring01 = SimplifiedPeriod.read(self.duck1080examiner, self.duck1100_spring01_core.id)
#         with self.assertRaises(PermissionDenied):
#             duck1100_spring01 = SimplifiedPeriod.read(self.superadmin, self.duck1100_spring01_core.id)


# class TestSimplifiedExaminerSimplifiedAssignment(SimplifiedExaminerTestCase):
#     def setUp(self):
#         super(TestSimplifiedExaminerSimplifiedAssignment, self).setUp()
#         self.duck1100_spring01_week1_core = self.duck1100_core.periods.get(
#                 short_name='spring01').assignments.get(short_name='week1')

#     def test_search(self):
#         examiner0 = User.objects.get(username="examiner0")
#         all_assignments = models.Assignment.objects.all().order_by("short_name")
#         qrywrap = SimplifiedAssignment.search(examiner0)
#         self.assertEquals(len(qrywrap), len(all_assignments))
#         self.assertEquals(qrywrap[0]['short_name'], all_assignments[0].short_name)

#         # query
#         qrywrap = SimplifiedAssignment.search(examiner0, query="ek")
#         self.assertEquals(len(qrywrap), 9)
#         qrywrap = SimplifiedAssignment.search(examiner0, query="fall0")
#         self.assertEquals(len(qrywrap), 5)
#         qrywrap = SimplifiedAssignment.search(examiner0, query="1100")
#         self.assertEquals(len(qrywrap), 4)

#     def test_read(self):
#         duck1100_spring01_week1 = SimplifiedAssignment.read(self.duck1100examiner,
#                 self.duck1100_spring01_week1_core.id)
#         self.assertEquals(duck1100_spring01_week1, dict(
#                 id = self.duck1100_spring01_week1_core.id,
#                 short_name = 'week1',
#                 long_name = self.duck1100_spring01_week1_core.long_name,
#                 parentnode__id=self.duck1100_spring01_week1_core.parentnode.id))

#         duck1100_spring01_week1 = SimplifiedAssignment.read(self.duck1100examiner,
#                 self.duck1100_spring01_week1_core.id,
#                 result_fieldgroups=['period'])
#         self.assertEquals(duck1100_spring01_week1, dict(
#                 id = self.duck1100_spring01_week1_core.id,
#                 short_name = 'week1',
#                 long_name = self.duck1100_spring01_week1_core.long_name,
#                 parentnode__id=self.duck1100_spring01_week1_core.parentnode.id,
#                 parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.short_name,
#                 parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.long_name,
#                 parentnode__parentnode__id=self.duck1100_spring01_week1_core.parentnode.parentnode_id))

#         duck1100_spring01_week1 = SimplifiedAssignment.read(self.duck1100examiner,
#                 self.duck1100_spring01_week1_core.id,
#                 result_fieldgroups=['period', 'subject'])
#         self.assertEquals(duck1100_spring01_week1, dict(
#                 id = self.duck1100_spring01_week1_core.id,
#                 short_name = 'week1',
#                 long_name = self.duck1100_spring01_week1_core.long_name,
#                 parentnode__id=self.duck1100_spring01_week1_core.parentnode.id,
#                 parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.short_name,
#                 parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.long_name,
#                 parentnode__parentnode__id=self.duck1100_spring01_week1_core.parentnode.parentnode_id,
#                 parentnode__parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.parentnode.short_name,
#                 parentnode__parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.parentnode.long_name))

#     def test_read_security(self):
#         with self.assertRaises(PermissionDenied):
#             duck1100_spring01_week1 = SimplifiedPeriod.read(self.testexaminerNoPerm, self.duck1100_spring01_week1_core.id)
#         with self.assertRaises(PermissionDenied):
#             duck1100_spring01_week1 = SimplifiedPeriod.read(self.duck1080examiner, self.duck1100_spring01_week1_core.id)
#         with self.assertRaises(PermissionDenied):
#             duck1100_spring01_week1 = SimplifiedPeriod.read(self.superadmin, self.duck1100_spring01_week1_core.id)



# class TestSimplifiedExaminerSimplifiedAssignmentGroup(SimplifiedExaminerTestCase):

#     def setUp(self):
#         super(TestSimplifiedExaminerSimplifiedAssignmentGroup, self).setUp()
#         duck3580_fall01_week1_core = self.duck3580_core.periods.get(
#                 short_name='fall01').assignments.get(short_name='week1')
#         self.group_core = duck3580_fall01_week1_core.assignmentgroups.all()[0]

#     def test_search(self):
#         assignment = models.Assignment.published_where_is_examiner(self.duck3580examiner)[0]

#         qrywrap = SimplifiedAssignmentGroup.search(self.duck3580examiner,
#                 assignment=assignment.id,
#                 orderby=["-id"], limit=2)
#         self.assertEquals(assignment.assignmentgroups.order_by('-id')[0].id, qrywrap[0]['id'])
#         self.assertTrue(qrywrap[0]['id'] > qrywrap[1]['id'])
#         self.assertEquals(qrywrap.count(), 2)

#         qrywrap = SimplifiedAssignmentGroup.search(self.duck3580examiner,
#                 assignment=assignment.id,
#                 query="student0")
#         self.assertEquals(qrywrap.count(), 1)
#         qrywrap = SimplifiedAssignmentGroup.search(self.duck3580examiner,
#                 assignment=assignment.id,
#                 query="thisisatest")
#         self.assertEquals(qrywrap.count(), 0)

#         g = SimplifiedAssignmentGroup.search(self.duck3580examiner, assignment=assignment)._insecure_django_qryset[0]
#         g.name = "thisisatest"
#         g.save()
#         qrywrap = SimplifiedAssignmentGroup.search(self.duck3580examiner, assignment=assignment.id,
#                 query="thisisatest")
#         self.assertEquals(qrywrap.count(), 1)

#     def test_search_security(self):
#         assignment = models.Assignment.published_where_is_examiner(self.duck3580examiner)[0]

#         result = SimplifiedAssignmentGroup.search(self.duck3580examiner,
#                 assignment=assignment.id,
#                 orderby=["-id"], limit=2)
#         qrywrap = result
#         self.assertEquals(result.resultfields, ('id', 'name'))
#         self.assertEquals(result.searchfields, ['name',
#             'candidates__candidate_id', 'candidates__student__username'])

#         assignment.anonymous = True
#         assignment.save()
#         result = SimplifiedAssignmentGroup.search(self.duck3580examiner,
#                 assignment=assignment.id)
#         self.assertEquals(result.searchfields, ('name', 'candidates__candidate_id'))

#         qrywrap = SimplifiedAssignmentGroup.search(self.duck3580examiner,
#                 assignment=assignment.id,
#                 query="student0") # Should not be able to search for username on anonymous
#         self.assertEquals(qrywrap.count(), 0)

#     def test_read(self):
#         #TODO add tests for read with fieldgroups
#         group = SimplifiedAssignmentGroup.read(self.duck3580examiner, self.group_core.id)
#         self.assertEquals(group, dict(
#                 id = self.group_core.id,
#                 name = None))

#     def test_read_security(self):
#         with self.assertRaises(PermissionDenied):
#             group = SimplifiedAssignmentGroup.read(self.testexaminerNoPerm, self.group_core.id)
#         with self.assertRaises(PermissionDenied):
#             group = SimplifiedAssignmentGroup.read(self.duck1080examiner, self.group_core.id)
#         with self.assertRaises(PermissionDenied):
#             group = SimplifiedAssignmentGroup.read(self.superadmin, self.group_core.id)

# class TestSimplifiedExaminerDelivery(SimplifiedExaminerTestCase):
# #TODO anonymous deliveries

#     def setUp(self):
#         super(TestSimplifiedExaminerDelivery, self).setUp()
#         duck3580_fall01_week1_core = self.duck3580_core.periods.get(
#                 short_name='fall01').assignments.get(short_name='week1') #assingment group
#         self.delivery_duck3580 = duck3580_fall01_week1_core.assignmentgroups.all()[0].deliveries.all()[0]#single delivery 

#     def test_search(self):
#         examiner0 =  User.objects.get(username="examiner0")
#         #deliveries where examiner 0 is examiner
#         deliveries = models.Delivery.published_where_is_examiner(examiner0)

#         #search for all deliveries where examiner0 is examiner
#         qrywrap = Delivery.search(examiner0)
#         self.assertEquals(len(qrywrap), len(deliveries)) #number of deliveries
#         self.assertEquals(qrywrap[5]['number'], deliveries[5].number) #delivery number
#         self.assertEquals(qrywrap[2]['id'], deliveries[2].id) #compare deliveries

#         #search period
#         qrywrap = Delivery.search(examiner0, query="fall01")
#         self.assertEquals(len(qrywrap), 9)
#         #search subject
#         qrywrap = Delivery.search(examiner0, query="1100")
#         self.assertEquals(len(qrywrap), 7)
#         #search period
#         qrywrap = Delivery.search(examiner0, query="week4")
#         self.assertEquals(len(qrywrap), 2)

#     def test_search_security(self):
#         #search by examiner with no permission returns no hits
#         result = Delivery.search(self.testexaminerNoPerm)
#         self.assertEquals(len(result), 0)

#         #open search resturns only deliveries where the examiner is examiner
#         result = Delivery.search(self.duck3580examiner)
#         deliveries = models.Delivery.published_where_is_examiner(self.duck3580examiner)
#         self.assertEquals(len(deliveries), len(result))

#         #duck3580examiner searching for duck1100 returns no hits
#         result = Delivery.search(self.duck3580examiner, query="duck1100")
#         self.assertEquals(len(result), 0)

#     def test_read(self):
#         duck3580_delivery = Delivery.read(self.duck3580examiner, self.delivery_duck3580.id)
#         self.assertEquals(duck3580_delivery, dict(
#             time_of_delivery = self.delivery_duck3580.time_of_delivery,
#             number = self.delivery_duck3580.number,
#             delivered_by = self.delivery_duck3580.delivered_by,
#             id=self.delivery_duck3580.id))

#         #read with fieldgroup subject
#         duck3580_delivery = Delivery.read(self.duck3580examiner, self.delivery_duck3580.id,
#                 result_fieldgroups=['subject'])
#         self.assertEquals(duck3580_delivery, dict(
#             time_of_delivery=self.delivery_duck3580.time_of_delivery,
#             number=self.delivery_duck3580.number,
#             delivered_by=self.delivery_duck3580.delivered_by,
#             id=self.delivery_duck3580.id,
#             assignment_group__parentnode__parentnode__parentnode__long_name=
#                 self.delivery_duck3580.assignment_group.parentnode.parentnode.parentnode.long_name,
#             assignment_group__parentnode__parentnode__parentnode__short_name=
#                 self.delivery_duck3580.assignment_group.parentnode.parentnode.parentnode.short_name,
#             assignment_group__parentnode__parentnode__parentnode__id=
#                 self.delivery_duck3580.assignment_group.parentnode.parentnode.parentnode.id))

#         #read with fieldgroup period
#         duck3580_delivery = Delivery.read(self.duck3580examiner, self.delivery_duck3580.id,
#                 result_fieldgroups=['period'])
#         self.assertEquals(duck3580_delivery, dict(
#             time_of_delivery=self.delivery_duck3580.time_of_delivery,
#             number=self.delivery_duck3580.number,
#             delivered_by=self.delivery_duck3580.delivered_by,
#             id=self.delivery_duck3580.id,
#             assignment_group__parentnode__parentnode__long_name=
#                 self.delivery_duck3580.assignment_group.parentnode.parentnode.long_name,
#             assignment_group__parentnode__parentnode__short_name=
#                 self.delivery_duck3580.assignment_group.parentnode.parentnode.short_name,
#             assignment_group__parentnode__parentnode__id=
#                 self.delivery_duck3580.assignment_group.parentnode.parentnode.id))

#         #read with fieldgroup assignment
#         duck3580_delivery = Delivery.read(self.duck3580examiner, self.delivery_duck3580.id,
#                 result_fieldgroups=['assignment'])
#         self.assertEquals(duck3580_delivery, dict(
#             time_of_delivery=self.delivery_duck3580.time_of_delivery,
#             number=self.delivery_duck3580.number,
#             delivered_by=self.delivery_duck3580.delivered_by,
#             id=self.delivery_duck3580.id,
#             assignment_group__parentnode__long_name=
#                 self.delivery_duck3580.assignment_group.parentnode.long_name,
#             assignment_group__parentnode__short_name=
#                 self.delivery_duck3580.assignment_group.parentnode.short_name,
#             assignment_group__parentnode__id=
#                 self.delivery_duck3580.assignment_group.parentnode.id))
            
#     def test_read_security(self):
#         with self.assertRaises(PermissionDenied):
#             delivery = Delivery.read(self.testexaminerNoPerm, self.delivery_duck3580.id)
#         with self.assertRaises(PermissionDenied):
#             delivery = Delivery.read(self.duck1080examiner, self.delivery_duck3580.id)
#         with self.assertRaises(PermissionDenied):
#             delivery = Delivery.read(self.superadmin, self.delivery_duck3580.id)

# class TestSimplifiedExaminerFeedback(SimplifiedExaminerTestCase):
# #TODO anonymous deliveries

#     def setUp(self):
#         super(TestSimplifiedExaminerFeedback, self).setUp()
#         self.duck1100_feedback_core = self.duck1100_core.periods.get(
#                 short_name='spring01').assignments.get(
#                 short_name='week1').assignmentgroups.all()[0].deliveries.all()[0].feedback

#     def test_read(self):
#         duck1100_feedback = Feedback.read(self.duck1100examiner, self.duck1100_feedback_core.id)
#         self.assertEquals(duck1100_feedback, dict(
#             delivery=self.duck1100_feedback_core.delivery,
#             text=self.duck1100_feedback_core.text,
#             format=self.duck1100_feedback_core.format,
#             id=self.duck1100_feedback_core.id))

#         #read with fieldgroup subject
#         duck1100_feedback = Feedback.read(self.duck1100examiner, self.duck1100_feedback_core.id,
#                 result_fieldgroups=['subject'])
#         self.assertEquals(duck1100_feedback, dict(
#             delivery=self.duck1100_feedback_core.delivery,
#             text=self.duck1100_feedback_core.text,
#             format=self.duck1100_feedback_core.format,
#             id=self.duck1100_feedback_core.id,
#             delivery__assignment_group__parentnode__parentnode__parentnode__long_name=
#                 self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.parentnode.long_name,
#             delivery__assignment_group__parentnode__parentnode__parentnode__short_name=
#                 self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.parentnode.short_name,
#             delivery__assignment_group__parentnode__parentnode__parentnode__id=
#                 self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.parentnode.id))

#         #read with fieldgroup period
#         duck1100_feedback = Feedback.read(self.duck1100examiner, self.duck1100_feedback_core.id,
#                 result_fieldgroups=['period'])
#         self.assertEquals(duck1100_feedback, dict(
#             delivery=self.duck1100_feedback_core.delivery,
#             text=self.duck1100_feedback_core.text,
#             format=self.duck1100_feedback_core.format,
#             id=self.duck1100_feedback_core.id,
#             delivery__assignment_group__parentnode__parentnode__long_name=
#                 self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.long_name,
#             delivery__assignment_group__parentnode__parentnode__short_name=
#                 self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.short_name,
#             delivery__assignment_group__parentnode__parentnode__id=
#                 self.duck1100_feedback_core.delivery.assignment_group.parentnode.parentnode.id))

#         #read with fieldgroup assignment
#         duck1100_feedback = Feedback.read(self.duck1100examiner, self.duck1100_feedback_core.id,
#                 result_fieldgroups=['assignment'])
#         self.assertEquals(duck1100_feedback, dict(
#             delivery=self.duck1100_feedback_core.delivery,
#             text=self.duck1100_feedback_core.text,
#             format=self.duck1100_feedback_core.format,
#             id=self.duck1100_feedback_core.id,
#             delivery__assignment_group__parentnode__long_name=
#                 self.duck1100_feedback_core.delivery.assignment_group.parentnode.long_name,
#             delivery__assignment_group__parentnode__short_name=
#                 self.duck1100_feedback_core.delivery.assignment_group.parentnode.short_name,
#             delivery__assignment_group__parentnode__id=
#                 self.duck1100_feedback_core.delivery.assignment_group.parentnode.id))

#     def test_read_security(self):
#         with self.assertRaises(PermissionDenied):
#             Feedback.read(self.testexaminerNoPerm, self.duck1100_feedback_core.id)
#         with self.assertRaises(PermissionDenied):
#             Feedback.read(self.duck3580examiner, self.duck1100_feedback_core.id)
#         with self.assertRaises(PermissionDenied):
#             Feedback.read(self.superadmin, self.duck1100_feedback_core.id) #TODO correct?

#     def test_search(self):
#         examiner0 = User.objects.get(username="examiner0")
#         #examiner0s feedbacks
#         feedbacks = models.Feedback.published_where_is_examiner(examiner0)

#         #seach for all feedbacks where examiner0 is examiner
#         qrywrap = Feedback.search(examiner0)
#         self.assertEquals(len(qrywrap), len(feedbacks))
#         self.assertEquals(qrywrap[1]['id'], feedbacks[1].id)

#         #search period
#         qrywrap = Feedback.search(examiner0, query="spring01")
#         self.assertEquals(len(qrywrap), 5)
#         #search subject
#         qrywrap = Feedback.search(examiner0, query="duck3580")
#         self.assertEquals(len(qrywrap), 4)
#         #search period
#         qrywrap = Feedback.search(examiner0, query="week3")
#         self.assertEquals(len(qrywrap), 2)

#     def test_search_security(self):
#         #search by examiner with no permission returns no hits
#         result = Feedback.search(self.testexaminerNoPerm)
#         self.assertEquals(len(result), 0)

#         #open search resturns only deliveries where the examiner is examiner
#         result = Feedback.search(self.duck3580examiner)
#         duck3580_feedbacks = models.Feedback.published_where_is_examiner(self.duck3580examiner)
#         self.assertEquals(len(duck3580_feedbacks), len(result))

#         #duck3580examiner searching for duck1100 returns no hits
#         result = Feedback.search(self.duck3580examiner, query="duck1100")
#         self.assertEquals(len(result), 0)

#     def test_create(self):
#         #TODO
#         pass

#     def test_ceate_security(self):
#         #TODO
#         pass
#     #TODO tests for delete and update also?

