import re

from django.contrib.auth.models import User
from django.test import TestCase

from ...core import models, testhelper
from ....simplified import PermissionDenied, FilterValidationError, InvalidNumberOfResults
from ....simplified.utils import modelinstance_to_dict, fix_expected_data_missing_database_fields
from ..simplified import (SimplifiedAssignment, SimplifiedAssignmentGroup, SimplifiedPeriod,
                          SimplifiedSubject, SimplifiedDeadline, SimplifiedStaticFeedback)

from datetime import timedelta

testhelper.TestHelper.set_memory_deliverystore()


class SimplifiedExaminerTestBase(TestCase, testhelper.TestHelper):

    def setUp(self):
        self.maxDiff = None # Show entire diffs
        # create a base structure
        self.add(nodes='uni:admin(admin)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstsem', 'secondsem'],
                 assignments=['a1', 'a2'])

        # add firstStud to the first and secondsem assignments
        self.add_to_path('uni;inf101.firstsem.a1.g1:candidate(firstStud):examiner(firstExam).d1')
        self.add_to_path('uni;inf101.firstsem.a2.g1:candidate(firstStud):examiner(firstExam).d1')
        self.add_to_path('uni;inf110.secondsem.a1.g1:candidate(firstStud):examiner(firstExam).d1')
        self.add_to_path('uni;inf110.secondsem.a2.g1:candidate(firstStud):examiner(firstExam).d1')
        self.add_to_path('uni;inf110.secondsem.a3:anon(true).g1:candidate(firstStud):examiner(firstExam).d1')

        # secondStud began secondsem
        self.add_to_path('uni;inf101.secondsem.a1.g2:candidate(secondStud);examiner(secondExam).d1')
        self.add_to_path('uni;inf101.secondsem.a2.g2:candidate(secondStud):examiner(secondExam).d1')


class TestSimplifiedExaminerSubject(SimplifiedExaminerTestBase):

    def setUp(self):
        super(TestSimplifiedExaminerSubject, self).setUp()

    def test_search_filters(self):
        qrywrap = SimplifiedSubject.search(self.firstExam)
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedSubject.search(self.firstExam,
                                        filters=[dict(field='parentnode__short_name', comp='exact', value='uni')])
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedSubject.search(self.firstExam,
                                        filters=[dict(field='short_name', comp='exact', value='inf110')])
        self.assertEquals(len(qrywrap), 1)

        with self.assertRaises(FilterValidationError):
            SimplifiedSubject.search(self.firstExam,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='uni')])
        with self.assertRaises(FilterValidationError):
            SimplifiedSubject.search(self.firstExam,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='uni')])
        with self.assertRaises(FilterValidationError):
            SimplifiedSubject.search(self.firstExam,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='uni')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedSubject.search(self.firstExam, exact_number_of_results=2)
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedSubject.search(self.firstExam, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 2)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedSubject.search(self.firstExam, exact_number_of_results=1)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedSubject.search(self.firstExam, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedSubject.search(self.firstExam, exact_number_of_results=0)

    def test_search(self):
        # do an empty search to get all subjects firstExam examines
        search_res = SimplifiedSubject.search(self.firstExam)
        expected_res = [modelinstance_to_dict(self.inf101, SimplifiedSubject._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110, SimplifiedSubject._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # do a search with query inf101
        search_res = SimplifiedSubject.search(self.firstExam, query='inf101')
        expected_res = modelinstance_to_dict(self.inf101, SimplifiedSubject._meta.resultfields.aslist())

        self.assertEquals(search_res.count(), 1)
        self.assertEquals(search_res[0], expected_res)

        # do a search with partial query
        search_res = SimplifiedSubject.search(self.firstExam, query='inf10')
        expected_res = modelinstance_to_dict(self.inf101, SimplifiedSubject._meta.resultfields.aslist())

        self.assertEquals(search_res.count(), 1)
        self.assertEquals(search_res[0], expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedSubject.search(self.firstStud)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedSubject.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedSubject.search(self.secondExam, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_read(self):
        # read firstsem without extra fields
        read_res = SimplifiedSubject.read(self.firstExam, self.inf101.id)
        expected_res = modelinstance_to_dict(self.inf101, SimplifiedSubject._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):
        # check that an examiner can't read a subject he's not signed
        # up for
        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.read(self.admin, self.inf101.id)

        # add another student, to inf110, but not inf101
        self.add_to_path('uni;inf110.firstsem.a1.g3:candidate(thirdStud)')
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

    allExtras = SimplifiedPeriod._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedExaminerPeriod, self).setUp()

    def test_search(self):

        # search with no query and no extra fields
        search_res = SimplifiedPeriod.search(self.firstExam)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem, SimplifiedPeriod._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem, SimplifiedPeriod._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), 2)
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedPeriod.search(self.firstExam, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem, SimplifiedPeriod._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem, SimplifiedPeriod._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedPeriod.search(self.firstExam, query='inf101')
        expected_res = modelinstance_to_dict(self.inf101_firstsem, SimplifiedPeriod._meta.resultfields.aslist())

        self.assertEquals(search_res.count(), 1)
        self.assertEquals(search_res[0], expected_res)

        # with query and extra fields
        search_res = SimplifiedPeriod.search(self.firstExam, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem, SimplifiedPeriod._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedPeriod.search(self.firstStud)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedPeriod.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedPeriod.search(self.secondExam, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_search_filters(self):
        qrywrap = SimplifiedPeriod.search(self.firstExam)
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedPeriod.search(self.firstExam,
                                        filters=[dict(field='parentnode__short_name', comp='exact', value='inf110')])
        self.assertEquals(len(qrywrap), 1)

        with self.assertRaises(FilterValidationError):
            SimplifiedPeriod.search(self.firstExam,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedPeriod.search(self.firstExam,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedPeriod.search(self.firstExam,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='inf110')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedPeriod.search(self.firstExam, exact_number_of_results=2)
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedPeriod.search(self.firstExam, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 2)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedPeriod.search(self.firstExam, exact_number_of_results=1)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedPeriod.search(self.firstExam, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedPeriod.search(self.firstExam, exact_number_of_results=0)

    def test_read(self):

        # read firstsem without extra fields
        read_res = SimplifiedPeriod.read(self.firstExam, self.inf101_firstsem.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem, SimplifiedPeriod._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # read firstsem with extras fields
        read_res = SimplifiedPeriod.read(self.firstExam, self.inf101_firstsem.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem, SimplifiedPeriod._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # check that reading a non-existing id gives permission denied
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.read(self.firstStud, -1)

        # that secondStud can't read a period he's not in
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.read(self.secondStud, self.inf101_firstsem.id)


class TestSimplifiedExaminerAssignment(SimplifiedExaminerTestBase):

    allExtras = SimplifiedAssignment._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedExaminerAssignment, self).setUp()

    def test_search(self):

        # search with no query and no extra fields
        search_res = SimplifiedAssignment.search(self.firstExam)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstsem_a2, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a2, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a3, SimplifiedAssignment._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedAssignment.search(self.firstExam, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a3,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedAssignment.search(self.firstExam, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1, SimplifiedAssignment._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedAssignment.search(self.firstExam, query='inf110', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a3,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedAssignment.search(self.firstStud)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedAssignment.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedAssignment.search(self.secondExam, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_search_filters(self):
        qrywrap = SimplifiedAssignment.search(self.firstExam)
        self.assertEquals(len(qrywrap), 5)
        qrywrap = SimplifiedAssignment.search(self.firstExam,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='parentnode__short_name', comp='exact', value='firstsem')])
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedAssignment.search(self.firstExam,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='parentnode__short_name', comp='exact', value='firstsem'),
                                                       dict(field='parentnode__parentnode__short_name', comp='endswith', value='101')])
        self.assertEquals(len(qrywrap), 2)

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedAssignment.search(self.firstExam, exact_number_of_results=5)
        self.assertEquals(len(qrywrap), 5)
        qrywrap = SimplifiedAssignment.search(self.firstExam, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignment.search(self.firstExam, exact_number_of_results=6)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignment.search(self.firstExam, exact_number_of_results=4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignment.search(self.firstExam, exact_number_of_results=0)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedAssignment.read(self.firstExam, self.inf101_firstsem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1,
                                             SimplifiedAssignment._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedAssignment.read(self.firstExam, self.inf101_firstsem_a1.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1,
                                             SimplifiedAssignment._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for inf110. Assert that
        # he can't do a read on inf101's id
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.secondStud, self.inf110_firstsem_a1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.admin, self.inf101_firstsem_a1.id)


class TestSimplifiedExaminerAssignmentGroup(SimplifiedExaminerTestBase):

    allExtras = SimplifiedAssignmentGroup._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedExaminerAssignmentGroup, self).setUp()

    def test_search_filters(self):
        qrywrap = SimplifiedAssignment.search(self.firstExam)
        self.assertEquals(len(qrywrap), 5)
        qrywrap = SimplifiedAssignmentGroup.search(self.firstExam,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='parentnode__short_name', comp='exact', value='a1')])
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedAssignmentGroup.search(self.firstExam,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='parentnode__short_name', comp='exact', value='a2'),
                                                       dict(field='parentnode__parentnode__short_name', comp='endswith', value='sem'),
                                                       dict(field='parentnode__parentnode__parentnode__short_name', comp='endswith', value='101')])
        self.assertEquals(len(qrywrap), 1)
        qrywrap = SimplifiedAssignmentGroup.search(self.firstExam,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='parentnode__short_name', comp='exact', value='a2'),
                                                       dict(field='parentnode__parentnode__short_name', comp='endswith', value='sem'),
                                                       dict(field='parentnode__parentnode__parentnode__short_name', comp='startswith', value='inf1')])
        self.assertEquals(len(qrywrap), 2)

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedAssignmentGroup.search(self.firstExam, exact_number_of_results=5)
        self.assertEquals(len(qrywrap), 5)
        qrywrap = SimplifiedAssignmentGroup.search(self.firstExam, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.firstExam, exact_number_of_results=6)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.firstExam, exact_number_of_results=4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.firstExam, exact_number_of_results=0)

    def test_search(self):
        self.firstExam = User.objects.get(id=self.firstExam.id)
        # search with no query and no extra fields
        search_res = SimplifiedAssignmentGroup.search(self.firstExam, query='firstStud')
        test_groups = [ self.inf101_firstsem_a1_g1,
                        self.inf101_firstsem_a2_g1,
                        self.inf110_secondsem_a1_g1,
                        self.inf110_secondsem_a2_g1,]
        expected_res = map(lambda group: modelinstance_to_dict(group, SimplifiedAssignmentGroup._meta.resultfields.aslist()), 
                           test_groups)
        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res)

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])

        # search with no query and with extra fields
        search_res = SimplifiedAssignmentGroup.search(self.firstExam, result_fieldgroups=self.allExtras)
        test_groups = [self.inf101_firstsem_a1_g1,
                       self.inf101_firstsem_a2_g1,
                       self.inf110_secondsem_a1_g1,
                       self.inf110_secondsem_a2_g1,
                       self.inf110_secondsem_a3_g1,]
        expected_res = map(lambda group: modelinstance_to_dict(group, 
                                         SimplifiedAssignmentGroup._meta.resultfields.aslist(self.allExtras)),
                           test_groups)
        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res)
            
        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])

        # search with query
        search_res = SimplifiedAssignmentGroup.search(self.firstExam, query='a1')
        test_groups = [self.inf101_firstsem_a1_g1,
                       self.inf110_secondsem_a1_g1,]
        expected_res = map(lambda group: modelinstance_to_dict(group, 
                                         SimplifiedAssignmentGroup._meta.resultfields.aslist()),
                           test_groups)
        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res)
        
        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])
        
        # with query and extra fields
        search_res = SimplifiedAssignmentGroup.search(self.firstExam, query='inf110', result_fieldgroups=self.allExtras)
        test_groups = [self.inf110_secondsem_a1_g1,
                       self.inf110_secondsem_a2_g1,
                       self.inf110_secondsem_a3_g1,]
        expected_res = map(lambda group: modelinstance_to_dict(group, 
                                         SimplifiedAssignmentGroup._meta.resultfields.aslist(self.allExtras)),
                           test_groups)
        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res)
        
        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])

    def test_search_security_asstudent(self):
        search_res = SimplifiedAssignmentGroup.search(self.firstStud)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedAssignmentGroup.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedAssignmentGroup.search(self.secondExam, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedAssignmentGroup.read(self.firstExam, self.inf101_firstsem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1,
                                             SimplifiedAssignmentGroup._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedAssignmentGroup.read(self.firstExam, self.inf101_firstsem_a1.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1,
                                             SimplifiedAssignmentGroup._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for firstsem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.secondStud, self.inf101_firstsem_a1_g1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.admin, self.inf101_firstsem_a1_g1.id)


class TestSimplifiedExaminerDeadline(SimplifiedExaminerTestBase):

    allExtras = SimplifiedAssignmentGroup._meta.resultfields.additional_aslist()
    baseFields = SimplifiedAssignmentGroup._meta.resultfields.aslist()
    allFields = SimplifiedAssignmentGroup._meta.resultfields.aslist(allExtras)

    def set_up(self):
        super(TestSimplifiedExaminerDeadline, self).setUp()

    def test_search_filters(self):
        qrywrap = SimplifiedDeadline.search(self.firstExam)
        self.assertEquals(len(qrywrap), 5)
        qrywrap = SimplifiedDeadline.search(self.firstExam,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='assignment_group__parentnode__short_name', comp='exact', value='a1'),
                                                       dict(field='assignment_group__parentnode__parentnode__short_name', comp='endswith', value='sem'),
                                                       dict(field='assignment_group__parentnode__parentnode__parentnode__short_name', comp='endswith', value='101')])
        self.assertEquals(len(qrywrap), 1)

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedDeadline.search(self.firstExam, exact_number_of_results=5)
        self.assertEquals(len(qrywrap), 5)
        qrywrap = SimplifiedDeadline.search(self.firstExam, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedDeadline.search(self.firstExam, exact_number_of_results=6)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedDeadline.search(self.firstExam, exact_number_of_results=4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedDeadline.search(self.firstExam, exact_number_of_results=0)

    def test_search_all(self):
        search_res = SimplifiedDeadline.search(self.firstExam, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0],
                                              SimplifiedDeadline._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1.deadlines.all()[0],
                                              SimplifiedDeadline._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1.deadlines.all()[0],
                                              SimplifiedDeadline._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1.deadlines.all()[0],
                                              SimplifiedDeadline._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a3_g1.deadlines.all()[0],
                                              SimplifiedDeadline._meta.resultfields.aslist(self.allExtras))]
        for expected in expected_res: # Set annotated fields
            expected['number_of_deliveries'] = 0

        self.assertEquals(len(search_res), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_query(self):
        search_res = SimplifiedDeadline.search(self.firstExam, query='101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0],
                                              SimplifiedDeadline._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1.deadlines.all()[0],
                                              SimplifiedDeadline._meta.resultfields.aslist(self.allExtras))]
        for expected in expected_res: # Set annotated fields
            expected['number_of_deliveries'] = 0

        self.assertEquals(len(search_res), len(expected_res))

        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedDeadline.search(self.firstStud)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedDeadline.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedDeadline.search(self.secondExam, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_read_base(self):
        # do a read with no extra fields
        read_res = SimplifiedDeadline.read(self.firstExam, self.inf101_firstsem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0],
                                             SimplifiedDeadline._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

    def test_read_all(self):
        # do a read with all extras
        read_res = SimplifiedDeadline.read(self.firstExam, self.inf101_firstsem_a1.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0],
                                             SimplifiedDeadline._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):
        # We know secondStud hasn't signed up for firstsem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.read(self.secondStud, self.inf101_firstsem_a1_g1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.read(self.admin, self.inf101_firstsem_a1_g1.id)

    def test_create(self):
        kw = dict(text='test',
                  assignment_group=self.inf101_firstsem_a1_g1,
                  deadline=self.inf101_firstsem_a1.publishing_time + timedelta(days=12))
        created_pk = SimplifiedDeadline.create(self.firstExam, **kw)

        create_res = models.Deadline.objects.get(pk=created_pk)
        self.assertEquals(create_res.text, 'test')
        self.assertEquals(create_res.assignment_group,
                          self.inf101_firstsem_a1_g1)
        self.assertEquals(create_res.deadline,
                          self.inf101_firstsem_a1_g1.get_active_deadline().deadline)

    def test_create_security(self):
        kw = dict(text='test',
                  assignment_group=self.inf101_firstsem_a1_g1,
                  deadline=self.inf101_firstsem_a1_g1.deadlines.all()[0])
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.create(self.firstStud, **kw)

        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.create(self.admin, **kw)

    def test_delete(self):
        SimplifiedDeadline.delete(self.firstExam,
                                  self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

        with self.assertRaises(IndexError):  # TODO: this should probably be PermissionDenied, but atm it gets an IndexError..
            SimplifiedDeadline.delete(self.firstExam,
                                      self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

    def test_delete_as_student(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.delete(self.firstStud,
                                      self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

    def test_delete_wrong_assignment_group(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.delete(self.secondExam,
                                      self.inf101_firstsem_a1_g1.deadlines.all()[0].id)


class TestSimplifiedExaminerStaticFeedback(SimplifiedExaminerTestBase):

    allExtras = SimplifiedStaticFeedback._meta.resultfields.additional_aslist()
    baseFields = SimplifiedStaticFeedback._meta.resultfields.aslist()
    allFields = SimplifiedStaticFeedback._meta.resultfields.aslist(allExtras)


    def setUp(self):
        super(TestSimplifiedExaminerStaticFeedback, self).setUp()
        # we need to add some deliveries here! Use the admin of uni as
        # an examiner
        # add deliveries and feedbacks to every group that was
        # created. Default values are good enough
        for var in dir(self):
            # find any variable that ends with '_gN' where N is a
            # number
            if re.search('_g\d$', var):
                group = getattr(self, var)
                group.examiners.add(self.admin)
                self.add_delivery(group)
                self.add_feedback(group)

    def test_search_filters(self):
        qrywrap = SimplifiedStaticFeedback.search(self.firstExam)
        self.assertEquals(len(qrywrap), 5)
        qrywrap = SimplifiedStaticFeedback.search(self.firstExam,
                                              filters=[dict(field='delivery', comp='exact', value='1')])
        self.assertEquals(len(qrywrap), 1)

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedStaticFeedback.search(self.firstExam, exact_number_of_results=5)
        self.assertEquals(len(qrywrap), 5)
        qrywrap = SimplifiedStaticFeedback.search(self.firstExam, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedStaticFeedback.search(self.firstExam, exact_number_of_results=6)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedStaticFeedback.search(self.firstExam, exact_number_of_results=4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedStaticFeedback.search(self.firstExam, exact_number_of_results=0)

    def test_search(self):
        search_res = SimplifiedStaticFeedback.search(self.firstExam)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a3_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        ]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedStaticFeedback.search(self.firstStud)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        self.create_superuser('superadminuser')
        search_res = SimplifiedStaticFeedback.search(self.superadminuser)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedStaticFeedback.search(self.secondExam, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_read(self):
        read_res = SimplifiedStaticFeedback.read(self.firstExam, self.inf101_firstsem_a1_g1_feedbacks[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                             SimplifiedStaticFeedback._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):
        # try to read one of secondExam's feedbacks
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.firstExam, self.inf101_secondsem_a1_g2_feedbacks[0].id)

    def test_create(self):
        created_pk = SimplifiedStaticFeedback.create(self.firstExam,
                                                     delivery=self.inf101_firstsem_a2_g1_deliveries[0],
                                                     grade='B',
                                                     points=80,
                                                     is_passing_grade=True,
                                                     rendered_view='<html></html>')
        # TODO: test results
