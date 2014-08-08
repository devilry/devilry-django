import re
from datetime import datetime
from django.test import TestCase

from devilry.simplified import PermissionDenied, FilterValidationError, InvalidNumberOfResults
from devilry.simplified.utils import modelinstance_to_dict, fix_expected_data_missing_database_fields

from devilry.apps.core import testhelper
from devilry.apps.core.models import RelatedStudent
from ..simplified import (SimplifiedDelivery, SimplifiedStaticFeedback, SimplifiedAssignment,
                          SimplifiedAssignmentGroup, SimplifiedPeriod, SimplifiedSubject,
                          SimplifiedFileMeta)


testhelper.TestHelper.set_memory_deliverystore()


class SimplifiedStudentTestBase(TestCase, testhelper.TestHelper):

    def setUp(self):
        self.maxDiff = None # Show entire diffs
        # create a base structure
        self.add(nodes='uni:admin(admin)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstsem:begins(-1):ends(6)', 'secondsem:begins(-1):ends(2)'],
                 assignments=['a1', 'a2'])

        # add firstStud to the first and secondsem assignments
        self.add_to_path('uni;inf101.firstsem.a1.g1:candidate(firstStud):examiner(examiner).d1')
        self.add_to_path('uni;inf101.firstsem.a2.g1:candidate(firstStud).d1')
        self.add_to_path('uni;inf110.secondsem.a1.g1:candidate(firstStud).d1')
        self.add_to_path('uni;inf110.secondsem.a2.g1:candidate(firstStud).d1')

        # secondStud began secondsem
        self.add_to_path('uni;inf101.secondsem.a1.g2:candidate(secondStud).d1')
        self.add_to_path('uni;inf101.secondsem.a2.g2:candidate(secondStud).d1')

        for period in (self.inf101_firstsem, self.inf101_secondsem,
                       self.inf110_firstsem, self.inf110_secondsem):
            RelatedStudent(user=self.firstStud, period=period).save()
        for period in (self.inf101_secondsem, self.inf110_secondsem):
            RelatedStudent(user=self.secondStud, period=period).save()


class TestSimplifiedNode(SimplifiedStudentTestBase):
    pass


class TestSimplifiedSubject(SimplifiedStudentTestBase):

    def setUp(self):
        super(TestSimplifiedSubject, self).setUp()

    def test_search(self):
        # do an empty search to get all subjects firstStud
        search_res = SimplifiedSubject.search(self.firstStud)
        expected_res = [modelinstance_to_dict(self.inf101, SimplifiedSubject._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110, SimplifiedSubject._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), 2)
        for s in search_res:
            self.assertTrue(s in expected_res)

        # do a search with query inf101
        search_res = SimplifiedSubject.search(self.firstStud, query='inf101')
        expected_res = modelinstance_to_dict(self.inf101, SimplifiedSubject._meta.resultfields.aslist())

        self.assertEquals(search_res.count(), 1)
        self.assertEquals(search_res[0], expected_res)

    def test_search_security_asexam(self):
        search_res = SimplifiedSubject.search(self.examiner)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedSubject.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedSubject.search(self.secondStud, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_read(self):
        # read firstsem without extra fields
        read_res = SimplifiedSubject.read(self.firstStud, self.inf101.id)
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

    def test_filters(self):
        filters = [{'field': 'short_name', 'comp': 'exact', 'value': 'inf110'}]
        search_res = SimplifiedSubject.search(self.firstStud, filters=filters)
        expected_res = modelinstance_to_dict(self.inf110, SimplifiedSubject._meta.resultfields.aslist())
        self.assertEquals(search_res[0], expected_res)


class TestSimplifiedPeriod(SimplifiedStudentTestBase):

    allExtras = SimplifiedPeriod._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedPeriod, self).setUp()

    def test_search_noextras(self):

        # search with no query and no extra fields
        search_res = SimplifiedPeriod.search(self.secondStud)
        expected_res = [modelinstance_to_dict(self.inf101_secondsem, SimplifiedPeriod._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem, SimplifiedPeriod._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), 2)
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_allextras(self):
        # search with no query and with extra fields
        search_res = SimplifiedPeriod.search(self.secondStud, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_secondsem, SimplifiedPeriod._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem, SimplifiedPeriod._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), 2)
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_query(self):
        # search with query
        search_res = SimplifiedPeriod.search(self.secondStud, query='inf101')
        expected_res = modelinstance_to_dict(self.inf101_secondsem, SimplifiedPeriod._meta.resultfields.aslist())

        self.assertEquals(search_res.count(), 1)
        self.assertEquals(search_res[0], expected_res)

    def test_search_queryandextras(self):
        # with query and extra fields
        search_res = SimplifiedPeriod.search(self.secondStud, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_secondsem, SimplifiedPeriod._meta.resultfields.aslist(self.allExtras))

        self.assertEquals(search_res.count(), 1)
        self.assertEquals(search_res[0], expected_res)

    def test_search_security_asexam(self):
        search_res = SimplifiedPeriod.search(self.examiner)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedPeriod.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_notinone(self):
        search_res = SimplifiedPeriod.search(self.secondStud, query='inf110')
        self.assertEquals(len(search_res), 1)

    def test_search_filters(self):
        qrywrap = SimplifiedPeriod.search(self.firstStud)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedPeriod.search(self.firstStud,
                                        filters=[dict(field='parentnode__short_name', comp='exact', value='inf110')])
        self.assertEquals(len(qrywrap), 2)

        with self.assertRaises(FilterValidationError):
            SimplifiedPeriod.search(self.firstStud,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedPeriod.search(self.firstStud,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedPeriod.search(self.firstStud,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='inf110')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedPeriod.search(self.firstStud, exact_number_of_results=4)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedPeriod.search(self.firstStud, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedPeriod.search(self.firstStud, exact_number_of_results=1)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedPeriod.search(self.firstStud, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedPeriod.search(self.firstStud, exact_number_of_results=0)

    def test_read(self):

        # read firstsem without extra fields
        read_res = SimplifiedPeriod.read(self.firstStud, self.inf101_firstsem.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem, SimplifiedPeriod._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # read firstsem with extras fields
        read_res = SimplifiedPeriod.read(self.firstStud, self.inf101_firstsem.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem, SimplifiedPeriod._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # check that reading a non-existing id gives permission denied
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.read(self.firstStud, -1)

        # that secondStud can't read a period he's not in
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.read(self.secondStud, self.inf101_firstsem.id)


class TestSimplifiedAssignment(SimplifiedStudentTestBase):

    allExtras = SimplifiedAssignment._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedAssignment, self).setUp()

    def test_search_noextras(self):

        # search with no query and no extra fields
        search_res = SimplifiedAssignment.search(self.firstStud)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstsem_a2, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a2, SimplifiedAssignment._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_allextras(self):
        # search with no query and with extra fields
        search_res = SimplifiedAssignment.search(self.firstStud, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_query(self):
        # search with query
        search_res = SimplifiedAssignment.search(self.firstStud, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1, SimplifiedAssignment._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_queryandextras(self):
        # with query and extra fields
        search_res = SimplifiedAssignment.search(self.firstStud, query='inf110', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asexam(self):
        search_res = SimplifiedAssignment.search(self.examiner)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedAssignment.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedAssignment.search(self.secondStud, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_search_filters(self):
        qrywrap = SimplifiedAssignment.search(self.firstStud)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedAssignment.search(self.firstStud,
                                        filters=[dict(field='parentnode__parentnode__short_name', comp='exact', value='inf110')])
        self.assertEquals(len(qrywrap), 2)

        with self.assertRaises(FilterValidationError):
            SimplifiedAssignment.search(self.firstStud,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedAssignment.search(self.firstStud,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedAssignment.search(self.firstStud,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='inf110')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedAssignment.search(self.firstStud, exact_number_of_results=4)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedAssignment.search(self.firstStud, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignment.search(self.firstStud, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignment.search(self.firstStud, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignment.search(self.firstStud, exact_number_of_results=0)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedAssignment.read(self.firstStud, self.inf101_firstsem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1,
                                             SimplifiedAssignment._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedAssignment.read(self.firstStud, self.inf101_firstsem_a1.id, result_fieldgroups=self.allExtras)
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


class TestSimplifiedAssignmentGroup(SimplifiedStudentTestBase):

    allExtras = SimplifiedAssignmentGroup._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedAssignmentGroup, self).setUp()

    def test_search_noextras(self):
        # search with no query and no extra fields
        search_res = SimplifiedAssignmentGroup.search(self.firstStud)
        test_groups = [self.inf101_firstsem_a1_g1,
                       self.inf101_firstsem_a2_g1,
                       self.inf110_secondsem_a1_g1,
                       self.inf110_secondsem_a2_g1,]
        expected_res = map(lambda group: modelinstance_to_dict(group, 
                                         SimplifiedAssignmentGroup._meta.resultfields.aslist()),
                           test_groups)
        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res)
        
        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])

    def test_search_hard_deadlines(self):
        self.add_to_path('uni.ifi;inf101.firstsem.deadlineinpast.g1:candidate(harddeadlinestudent):examiner(harddeadlineexaminer).d0:ends(1)')
        self.add_to_path('uni.ifi;inf101.firstsem.deadlineinfuture.g1:candidate(harddeadlinestudent):examiner(harddeadlineexaminer).d0:ends(60)')
        old_deadline = self.inf101_firstsem_deadlineinpast_g1_d0
        future_deadline = self.inf101_firstsem_deadlineinfuture_g1_d0
        self.assertTrue(old_deadline.deadline < datetime.now())
        self.assertTrue(future_deadline.deadline > datetime.now())

        # Before we set hard deadlines
        search_res = SimplifiedAssignmentGroup.search(self.harddeadlinestudent)
        self.assertEquals(SimplifiedAssignmentGroup.search(self.harddeadlinestudent).count(), 2)

        # After setting hard deadlines
        deadlineinpast = self.inf101_firstsem_deadlineinpast
        deadlineinfuture = self.inf101_firstsem_deadlineinfuture
        for assignment in deadlineinpast, deadlineinfuture:
            assignment.deadline_handling = 1
            assignment.save()
        self.assertEquals(SimplifiedAssignmentGroup.search(self.harddeadlinestudent).count(), 1)


    def test_search_allextras(self):
        # search with no query and with extra fields
        search_res = SimplifiedAssignmentGroup.search(self.firstStud, result_fieldgroups=self.allExtras)
        test_groups = [self.inf101_firstsem_a1_g1,
                       self.inf101_firstsem_a2_g1,
                       self.inf110_secondsem_a1_g1,
                       self.inf110_secondsem_a2_g1,]
        expected_res = map(lambda group: modelinstance_to_dict(group, 
                                         SimplifiedAssignmentGroup._meta.resultfields.aslist(self.allExtras)),
                           test_groups)
        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res)
        
        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])

    def test_search_query(self):
        # search with query
        search_res = SimplifiedAssignmentGroup.search(self.firstStud, query='a1')
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

    def test_search_queryandextras(self):
        # with query and extra fields
        search_res = SimplifiedAssignmentGroup.search(self.firstStud, query='inf110', result_fieldgroups=self.allExtras)
        test_groups = [self.inf110_secondsem_a1_g1,
                       self.inf110_secondsem_a2_g1,]
        expected_res = map(lambda group: modelinstance_to_dict(group, 
                                         SimplifiedAssignmentGroup._meta.resultfields.aslist(self.allExtras)),
                           test_groups)
        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res)
        
        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])

    def test_search_security_asexam(self):
        search_res = SimplifiedAssignmentGroup.search(self.examiner)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedAssignmentGroup.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedAssignmentGroup.search(self.secondStud, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_search_filters(self):
        qrywrap = SimplifiedAssignmentGroup.search(self.firstStud)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedAssignmentGroup.search(self.firstStud,
                                        filters=[dict(field='parentnode__parentnode__parentnode__short_name', comp='exact', value='inf110')])
        self.assertEquals(len(qrywrap), 2)

        with self.assertRaises(FilterValidationError):
            SimplifiedAssignmentGroup.search(self.firstStud,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedAssignmentGroup.search(self.firstStud,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedAssignmentGroup.search(self.firstStud,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='inf110')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedAssignmentGroup.search(self.firstStud, exact_number_of_results=4)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedAssignmentGroup.search(self.firstStud, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.firstStud, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.firstStud, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.firstStud, exact_number_of_results=0)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedAssignmentGroup.read(self.firstStud, self.inf101_firstsem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1,
                                             SimplifiedAssignmentGroup._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedAssignmentGroup.read(self.firstStud, self.inf101_firstsem_a1.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1,
                                             SimplifiedAssignmentGroup._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for firstsem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.secondStud, self.inf101_firstsem_a1_g1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.admin, self.inf101_firstsem_a1_g1.id)


class TestSimplifiedDelivery(SimplifiedStudentTestBase):

    allExtras = SimplifiedDelivery._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedDelivery, self).setUp()

        # we need to add some deliveries here! Use the admin of uni as
        # an examiner
        # add deliveries and feedbacks to every group that was
        # created. Default values are good enough
        for var in dir(self):
            # find any variable that ends with '_gN' where N is a
            # number
            if re.search('_g\d$', var):
                group = getattr(self, var)
                if group.examiners.filter(user=self.admin).count() == 0:
                    group.examiners.create(user=self.admin)
                self.add_delivery(group)

    def test_search_noextras(self):
        # search with no query and no extra fields
        search_res = SimplifiedDelivery.search(self.firstStud)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_allextras(self):
        # search with no query and with extra fields
        search_res = SimplifiedDelivery.search(self.firstStud, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_query(self):
        # search with query
        search_res = SimplifiedDelivery.search(self.firstStud, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_queryandextras(self):
        # with query and extra fields
        search_res = SimplifiedDelivery.search(self.firstStud, query='inf110', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondsem_a1_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asexam(self):
        search_res = SimplifiedDelivery.search(self.examiner)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedDelivery.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedDelivery.search(self.secondStud, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_search_filters(self):
        qrywrap = SimplifiedDelivery.search(self.firstStud)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedDelivery.search(self.firstStud,
                                        filters=[dict(field='deadline__assignment_group__parentnode__parentnode__parentnode__short_name', comp='exact', value='inf110')])
        self.assertEquals(len(qrywrap), 2)

        with self.assertRaises(FilterValidationError):
            SimplifiedDelivery.search(self.firstStud,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedDelivery.search(self.firstStud,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedDelivery.search(self.firstStud,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='inf110')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedDelivery.search(self.firstStud, exact_number_of_results=4)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedDelivery.search(self.firstStud, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedDelivery.search(self.firstStud, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedDelivery.search(self.firstStud, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedDelivery.search(self.firstStud, exact_number_of_results=0)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedDelivery.read(self.firstStud, self.inf101_firstsem_a1_g1_deliveries[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0],
                                             SimplifiedDelivery._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedDelivery.read(self.firstStud, self.inf101_firstsem_a1_g1_deliveries[0].id,
                                           result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0],
                                             SimplifiedDelivery._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for firstsem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedDelivery.read(self.secondStud, self.inf101_firstsem_a1_g1_deliveries[0].id)

        with self.assertRaises(PermissionDenied):
            SimplifiedDelivery.read(self.admin, self.inf101_firstsem_a1_g1_deliveries[0].id)

    def test_filters(self):
        # filter for all deliveries done in an assignment called
        # 'a1'. There should be 2 results, one from inf101 and the
        # other from inf110
        filters = [{'field': 'deadline__assignment_group__parentnode__short_name', 'comp': 'iexact', 'value': 'a1'}]
        search_res = SimplifiedDelivery.search(self.firstStud, filters=filters)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_deliveries[0],
                                              SimplifiedDelivery._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)


class TestSimplifiedStaticFeedback(SimplifiedStudentTestBase):

    allExtras = SimplifiedStaticFeedback._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedStaticFeedback, self).setUp()

        # we need to add some deliveries here! Use the admin of uni as
        # an examiner
        # add deliveries and feedbacks to every group that was
        # created. Default values are good enough
        for var in dir(self):
            # find any variable that ends with '_gN' where N is a
            # number
            if re.search('_g\d$', var):
                group = getattr(self, var)
                if group.examiners.filter(user=self.admin).count() == 0:
                    group.examiners.create(user=self.admin)
                self.add_delivery(group)
                self.add_feedback(group)

    def test_search_noextras(self):
        # search with no query and no extra fields
        search_res = SimplifiedStaticFeedback.search(self.firstStud)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_allextras(self):
        # search with no query and with extra fields
        search_res = SimplifiedStaticFeedback.search(self.firstStud, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_query(self):
        # search with query
        search_res = SimplifiedStaticFeedback.search(self.firstStud, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_queryandextras(self):
        # with query and extra fields
        search_res = SimplifiedStaticFeedback.search(self.firstStud, query='inf110', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asexam(self):
        search_res = SimplifiedStaticFeedback.search(self.examiner)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedStaticFeedback.search(self.admin)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedStaticFeedback.search(self.secondStud, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_search_filters(self):
        qrywrap = SimplifiedStaticFeedback.search(self.firstStud)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedStaticFeedback.search(self.firstStud,
                                        filters=[dict(field='delivery', comp='exact', value='1')])
        self.assertEquals(len(qrywrap), 1)

        with self.assertRaises(FilterValidationError):
            SimplifiedStaticFeedback.search(self.firstStud,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedStaticFeedback.search(self.firstStud,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedStaticFeedback.search(self.firstStud,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='inf110')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedDelivery.search(self.firstStud, exact_number_of_results=4)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedDelivery.search(self.firstStud, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedStaticFeedback.search(self.firstStud, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedStaticFeedback.search(self.firstStud, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedStaticFeedback.search(self.firstStud, exact_number_of_results=0)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedStaticFeedback.read(self.firstStud, self.inf101_firstsem_a1_g1_deliveries[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                             SimplifiedStaticFeedback._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedStaticFeedback.read(self.firstStud, self.inf101_firstsem_a1_g1_feedbacks[0].id,
                                           result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                             SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for firstsem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.secondStud, self.inf101_firstsem_a1_g1_feedbacks[0].id)

        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.admin, self.inf101_firstsem_a1_g1_feedbacks[0].id)


class TestSimplifiedCandidateFileMeta(SimplifiedStudentTestBase):

    allExtras = SimplifiedFileMeta._meta.resultfields.additional_aslist()
    baseFields = SimplifiedFileMeta._meta.resultfields.aslist()
    allFields = SimplifiedFileMeta._meta.resultfields.aslist(allExtras)

    def setUp(self):
        super(TestSimplifiedCandidateFileMeta, self)
        # create a base structure
        self.add(nodes='uni:admin(admin1)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstsem', 'secondsem:admin(admin2)'],
                 assignments=['a1', 'a2'])

        # add firstStud to the first and secondsem assignments
        self.add_to_path('uni;inf101.firstsem.a1.g1:candidate(firstStud):examiner(exam1,exam3).d1')
        self.add_to_path('uni;inf101.firstsem.a2.g1:candidate(firstStud):examiner(exam1).d1')
        self.add_to_path('uni;inf110.secondsem.a1.g1:candidate(firstStud):examiner(exam2).d1')
        self.add_to_path('uni;inf110.secondsem.a2.g1:candidate(firstStud):examiner(exam2).d1')

        # secondStud began secondsem
        self.add_to_path('uni;inf101.secondsem.a1.g2:candidate(secondStud):examiner(exam1).d1')
        self.add_to_path('uni;inf101.secondsem.a2.g2:candidate(secondStud):examiner(exam1).d1')

        for var in dir(self):
            # find any variable that ends with '_gN' where N is a
            # number
            if re.search('_g\d$', var):
                group = getattr(self, var)
                if group.examiners.filter(user=self.exam1).count() == 0:
                    group.examiners.create(user=self.exam1)
                files = {'good.py': ['print ', 'awesome']}
                self.add_delivery(group, files)

    def test_search(self):
        # search with no query and no extra fields
        # should only have the deafault deadlines created when the
        # assignment group was created
        search_res = SimplifiedFileMeta.search(self.firstStud)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_deliveries[0].filemetas.all()[0], self.baseFields),
                        ]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedFileMeta.search(self.firstStud, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        ]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedFileMeta.search(self.firstStud, query='secondStud')
        expected_res = []

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedFileMeta.search(self.firstStud, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        ]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asexam(self):
        search_res = SimplifiedFileMeta.search(self.exam1)
        self.assertEquals(len(search_res), 0)

    def test_search_security_asadmin(self):
        search_res = SimplifiedFileMeta.search(self.admin1)
        self.assertEquals(len(search_res), 0)

    def test_search_security_wrongsubject(self):
        search_res = SimplifiedFileMeta.search(self.secondStud, query='inf110')
        self.assertEquals(len(search_res), 0)

    def test_search_filters(self):
        qrywrap = SimplifiedFileMeta.search(self.firstStud)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedFileMeta.search(self.firstStud,
                                        filters=[dict(field='delivery', comp='exact', value='1')])
        self.assertEquals(len(qrywrap), 1)

        with self.assertRaises(FilterValidationError):
            SimplifiedFileMeta.search(self.firstStud,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedFileMeta.search(self.firstStud,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedFileMeta.search(self.firstStud,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='inf110')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedFileMeta.search(self.firstStud, exact_number_of_results=4)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedFileMeta.search(self.firstStud, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedFileMeta.search(self.firstStud, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedFileMeta.search(self.firstStud, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedFileMeta.search(self.firstStud, exact_number_of_results=0)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedFileMeta.read(self.firstStud, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0],
                                             SimplifiedFileMeta._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedFileMeta.read(self.firstStud, self.inf101_firstsem_a1_g1.deadlines.all()[0].id,
                                           result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0],
                                             SimplifiedFileMeta._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for firstsem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedFileMeta.read(self.secondStud, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)

        # test that an admin in another subject cant read outside his
        # subjects
        self.add_to_path('uni;inf110:admin(inf110admin)')
        with self.assertRaises(PermissionDenied):
            SimplifiedFileMeta.read(self.inf110admin, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)
