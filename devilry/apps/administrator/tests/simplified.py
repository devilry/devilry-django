from datetime import timedelta
import re

from django.test import TestCase


from ....simplified import PermissionDenied, FilterValidationError, InvalidNumberOfResults
from ....simplified.utils import modelinstance_to_dict
from ...core import models, testhelper
from ..simplified import (SimplifiedNode, SimplifiedSubject, SimplifiedPeriod,
                          SimplifiedAssignment, SimplifiedAssignmentGroup,
                          SimplifiedDeadline, SimplifiedStaticFeedback,
                          SimplifiedFileMeta)


testhelper.TestHelper.set_memory_deliverystore()



class SimplifiedAdminTestBase(TestCase, testhelper.TestHelper):

    def setUp(self):
        self.create_superuser('superadminuser')

        # create a base structure
        self.add(nodes='uni:admin(admin1)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstsem', 'secondsem:admin(admin2)'],
                 assignments=['a1', 'a2'])

        # add firstStud to the first and secondsem assignments
        self.add_to_path('uni;inf101.firstsem.a1.g1:candidate(firstStud):examiner(exam1,exam3)')
        self.add_to_path('uni;inf101.firstsem.a2.g1:candidate(firstStud):examiner(exam1)')
        self.add_to_path('uni;inf110.secondsem.a1.g1:candidate(firstStud):examiner(exam2)')
        self.add_to_path('uni;inf110.secondsem.a2.g1:candidate(firstStud):examiner(exam2)')

        # secondStud began secondsem
        self.add_to_path('uni;inf101.secondsem.a1.g2:candidate(secondStud):examiner(exam1)')
        self.add_to_path('uni;inf101.secondsem.a2.g2:candidate(secondStud):examiner(exam1)')


class TestSimplifiedNode(SimplifiedAdminTestBase):
    def setUp(self):
        self.add(nodes='uni:admin(admin1).mat.inf')
        self.add(nodes='uni.fys')


    def test_search_filters(self):
        qrywrap = SimplifiedNode.search(self.admin1)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedNode.search(self.admin1,
                                        filters=[dict(field='parentnode__short_name', comp='exact', value='uni')])
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedNode.search(self.admin1,
                                        filters=[dict(field='parentnode__parentnode__short_name', comp='exact', value='uni')])
        self.assertEquals(len(qrywrap), 1)

        with self.assertRaises(FilterValidationError):
            SimplifiedNode.search(self.admin1,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='uni')])
        with self.assertRaises(FilterValidationError):
            SimplifiedNode.search(self.admin1,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='uni')])
        with self.assertRaises(FilterValidationError):
            SimplifiedNode.search(self.admin1,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='uni')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedNode.search(self.admin1, exact_number_of_results=4)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedNode.search(self.admin1, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedNode.search(self.admin1, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedNode.search(self.admin1, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedNode.search(self.admin1, exact_number_of_results=0)


class TestSimplifiedAssignment(SimplifiedAdminTestBase):

    def setUp(self):
        super(TestSimplifiedAssignment, self).setUp()

    def test_read_base(self):
        # do a read with no extra fields
        read_res = SimplifiedAssignment.read(self.admin1, self.inf101_firstsem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1,
                                             SimplifiedAssignment._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)


    def test_read_period(self):
        # do a read with all extras
        read_res = SimplifiedAssignment.read(self.admin1,
                self.inf101_firstsem_a1.id, result_fieldgroups='period')
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1,
                                             SimplifiedAssignment._meta.resultfields.aslist('period'))
        self.assertEquals(read_res, expected_res)

    def test_read_period_subject(self):
        read_res = SimplifiedAssignment.read(self.admin1,
                self.inf101_firstsem_a1.id, result_fieldgroups=['period',
                    'subject'])
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1,
                                             SimplifiedAssignment._meta.resultfields.aslist(['period',
                                                 'subject']))
        self.assertEquals(read_res, expected_res)

    def test_read_period_subject_pointfields(self):
        read_res = SimplifiedAssignment.read(self.admin1,
                self.inf101_firstsem_a1.id, result_fieldgroups=['period',
                    'subject', 'pointfields'])
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1,
                                             SimplifiedAssignment._meta.resultfields.aslist(['period',
                                                 'subject', 'pointfields']))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):
        self.add_to_path('uni;inf110.firstsem.a2.g1:candidate(testPerson)')

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.testPerson,
                    self.inf110_firstsem_a2.id)

        self.add_to_path('uni;inf110.firstsem.a2:admin(testPerson)')
        SimplifiedAssignment.read(self.testPerson, self.inf110_firstsem_a2.id)


    def test_search(self):
        self.allExtras = SimplifiedAssignment._meta.resultfields.additional_aslist()
        # search with no query and no extra fields
        search_res = SimplifiedAssignment.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstsem_a2, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondsem_a2, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_firstsem_a2, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a2, SimplifiedAssignment._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no querys, but all extra fields
        search_res = SimplifiedAssignment.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_secondsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_secondsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_firstsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_firstsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedAssignment.search(self.admin1, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondsem_a1,SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1, SimplifiedAssignment._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields, only subject containing '11' is 'inf110'.
        search_res = SimplifiedAssignment.search(self.admin1, query='11', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_firstsem_a1,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_firstsem_a2,
                                              SimplifiedAssignment._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res)) 
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security(self):
        self.add_to_path('uni;inf110.firstsem.a2.g1:candidate(testPerson)')

        search_res = SimplifiedAssignment.search(self.testPerson)
        self.assertEquals(search_res.count(), 0)

        self.add_to_path('uni;inf110.firstsem.a2:admin(testPerson)')
        search_res = SimplifiedAssignment.search(self.testPerson)
        expected_res = [modelinstance_to_dict(self.inf110_firstsem_a2,
            SimplifiedAssignment._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_filters(self):
        qrywrap = SimplifiedAssignment.search(self.admin1)
        self.assertEquals(len(qrywrap), 8)
        qrywrap = SimplifiedAssignment.search(self.admin1,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='parentnode__short_name', comp='exact', value='firstsem')])
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedAssignment.search(self.admin1,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='parentnode__short_name', comp='exact', value='firstsem'),
                                                       dict(field='parentnode__parentnode__short_name', comp='endswith', value='101')])
        self.assertEquals(len(qrywrap), 2)

    def test_create(self):
        kw = dict(
                long_name = 'Test',
                parentnode = self.inf110_firstsem_a2.parentnode,
                publishing_time = self.inf110_firstsem_a2.publishing_time)

        newpk = SimplifiedAssignment.create(self.admin1, short_name='test1', **kw)
        create_res = models.Assignment.objects.get(pk=newpk)
        self.assertEquals(create_res.short_name, 'test1')
        self.assertEquals(create_res.long_name, 'Test')
        self.assertEquals(create_res.parentnode,
                self.inf110_firstsem_a2.parentnode)
        self.assertEquals(create_res.publishing_time,
                self.inf110_firstsem_a2.publishing_time)

    def test_create_security(self):
        kw = dict(
                long_name = 'Test',
                parentnode = self.inf110_firstsem_a2.parentnode,
                publishing_time = self.inf110_firstsem_a2.publishing_time)

        #test that a student cannot create an assignment
        self.add_to_path('uni;inf110.firstsem.a2.g1:candidate(inf110Student)')
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.create(self.inf110Student, short_name='test1', **kw)

        #test that an administrator cannot create assignment for the wrong course
        self.add_to_path('uni;inf101:admin(inf101Admin)')
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.create(self.inf101Admin, short_name='test1', **kw)

        #test that a course-administrator can create assignments for his/her course..
        self.add_to_path('uni;inf110:admin(inf110Admin)')
        SimplifiedAssignment.create(self.inf110Admin, short_name='test1', **kw)

    def test_update(self):
        self.assertEquals(self.inf110_firstsem_a2.short_name, 'a2')

        kw = dict(short_name = 'testa2',
                    long_name = 'Test',
                    parentnode = self.inf110_firstsem_a2.parentnode)

        pk = SimplifiedAssignment.update(self.admin1,
                            pk = self.inf110_firstsem_a2.id,
                            **kw)
        update_res = models.Assignment.objects.get(pk=pk)

        self.assertEquals(update_res.short_name, 'testa2')
        self.assertEquals(self.inf110_firstsem_a2.short_name, 'a2')

        update_res = SimplifiedAssignment.update(self.admin1,
                                                 pk=self.inf110_firstsem_a2.id,
                                                 short_name = 'test110')
        self.refresh_var(self.inf110_firstsem_a2)
        self.assertEquals(self.inf110_firstsem_a2.short_name, 'test110')

    def test_update_security(self):
        kw = dict(
                long_name = 'TestAssignment',
                short_name = 'ta')

        #test that a student cannot change an assignment
        self.add_to_path('uni;inf110.firstsem.a2.g1:candidate(inf110Student)')
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.update(self.inf110Student, pk=self.inf110_firstsem_a2.id, **kw)

        #test that an administrator cannot change assignment for the wrong course
        self.add_to_path('uni;inf101:admin(inf101Admin)')
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.update(self.inf101Admin, pk=self.inf110_firstsem_a2.id, **kw)

        #test that a course-administrator can change assignments for his/her course..
        self.add_to_path('uni;inf110:admin(inf110Admin)')
        SimplifiedAssignment.update(self.inf110Admin, pk=self.inf110_firstsem_a2.id, **kw)

    def test_delete_asnodeadmin(self):
        self.add_to_path('uni;inf110.firstsem.a1:admin(testadmin)')
        SimplifiedAssignment.delete(self.testadmin, self.inf110_firstsem_a1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.delete(self.testadmin, self.inf110_firstsem_a1.id)

    def test_delete_assuperadmin(self):
        SimplifiedAssignment.delete(self.superadminuser, self.inf110_firstsem_a1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.delete(self.admin1, self.inf110_firstsem_a1.id)

    def test_delete_noperm(self):
        self.add_to_path('uni;inf110.firstsem.a1.g1:candidate(testPerson)')

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.delete(self.testPerson, self.inf110_firstsem_a1.id)


class TestSimplifiedAdminAssignmentGroup(SimplifiedAdminTestBase):

    allExtras = SimplifiedAssignmentGroup._meta.resultfields.additional_aslist()
    baseFields = SimplifiedAssignmentGroup._meta.resultfields.aslist()
    allFields = SimplifiedAssignmentGroup._meta.resultfields.aslist(allExtras)

    def setUp(self):
        super(TestSimplifiedAdminAssignmentGroup, self).setUp()

    def test_search(self):
        # search with no query and no extra fields

        search_res = SimplifiedAssignmentGroup.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1, self.baseFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1, self.baseFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1, self.baseFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1, self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2, self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2, self.baseFields),
                        ]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedAssignmentGroup.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1, self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1, self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1, self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1, self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2, self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2, self.allFields),
                        ]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedAssignmentGroup.search(self.admin1, query='secondStud')
        expected_res = [modelinstance_to_dict(self.inf101_secondsem_a1_g2, self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2, self.baseFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedAssignmentGroup.search(self.admin1, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1, self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1, self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2, self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2, self.allFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedAssignmentGroup.read(self.admin1, self.inf101_firstsem_a1_g1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1,
                                             SimplifiedAssignmentGroup._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedAssignmentGroup.read(self.admin1, self.inf101_firstsem_a1_g1.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1,
                                             SimplifiedAssignmentGroup._meta.resultfields.aslist(self.allExtras))

        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for firstsem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.secondStud, self.inf101_firstsem_a1_g1.id)


class TestSimplifiedAdminstratorStaticFeedback(SimplifiedAdminTestBase):
    
    allExtras = SimplifiedStaticFeedback._meta.resultfields.additional_aslist()
    
    def setUp(self):
        super(TestSimplifiedAdminstratorStaticFeedback, self).setUp()
        # we need to add some deliveries here! Use the admin of uni as
        # an examiner
        # add deliveries and feedbacks to every group that was
        # created. Default values are good enough
        for var in dir(self):
            # find any variable that ends with '_gN' where N is a
            # number
            if re.search('_g\d$', var):
                group = getattr(self, var)
                group.examiners.add(self.exam1)
                self.add_delivery(group)
                self.add_feedback(group)
    
    def test_search(self):
        # search with no query and no extra fields
        search_res = SimplifiedStaticFeedback.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedStaticFeedback.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedStaticFeedback.search(self.admin1, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedStaticFeedback.search(self.admin1, query='inf110', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedStaticFeedback.read(self.admin1, self.inf101_firstsem_a1_g1_deliveries[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                             SimplifiedStaticFeedback._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedStaticFeedback.read(self.admin1, self.inf101_firstsem_a1_g1_feedbacks[0].id,
                                           result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                             SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # test with someone who's not an admin
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.firstStud, self.inf101_firstsem_a1_g1_feedbacks[0].id)

        # test with someone who's not an admin
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.exam1, self.inf101_firstsem_a1_g1_feedbacks[0].id)


class TestSimplifiedAdminDeadline(SimplifiedAdminTestBase):

    allExtras = SimplifiedDeadline._meta.resultfields.additional_aslist()
    baseFields = SimplifiedDeadline._meta.resultfields.aslist()
    allFields = SimplifiedDeadline._meta.resultfields.aslist(allExtras)

    def setUp(self):
        super(TestSimplifiedAdminDeadline, self).setUp()

    def test_search(self):
        # search with no query and no extra fields
        # should only have the deafault deadlines created when the
        # assignment group was created
        search_res = SimplifiedDeadline.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2.deadlines.all()[0], self.baseFields),
                        ]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedDeadline.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2.deadlines.all()[0], self.allFields),
                        ]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedDeadline.search(self.admin1, query='secondStud')
        expected_res = [modelinstance_to_dict(self.inf101_secondsem_a1_g2.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2.deadlines.all()[0], self.baseFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedDeadline.search(self.admin1, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2.deadlines.all()[0], self.allFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # add some new deadlines, to simulate groups getting a second
        # chance
        self.add_to_path('uni;inf101.secondsem.a1.g2.deadline:ends(10):text(This is your last shot!)')

        search_res = SimplifiedDeadline.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1.deadlines.all()[0], self.allFields),
                        # this group now has 2 deadlines. make sure to include the old one here
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2.deadlines.order_by('deadline')[0], self.allFields),
                        # and the new one here
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_deadlines[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2.deadlines.all()[0], self.allFields),
                        ]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedDeadline.read(self.admin1, self.inf101_firstsem_a1_g1.deadlines.all()[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0],
                                             SimplifiedDeadline._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedDeadline.read(self.admin1, self.inf101_firstsem_a1_g1.deadlines.all()[0].id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0],
                                             SimplifiedDeadline._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.read(self.secondStud, self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

        # test that an admin in another subject cant read outside his
        # subjects
        self.add_to_path('uni;inf110:admin(inf110admin)')
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.read(self.inf110admin, self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

    def test_create(self):

        # create a deadline that runs out in 3 days
        kw = dict(
            assignment_group=self.inf101_firstsem_a1_g1,
            deadline=self.inf101_firstsem_a1_g1.deadlines.order_by('deadline')[0].deadline + timedelta(days=3),
            text='Last shot!')

        createdpk = SimplifiedDeadline.create(self.admin1, **kw)
        read_res = SimplifiedDeadline.read(self.admin1, createdpk, result_fieldgroups=self.allExtras)
        create_res = models.Deadline.objects.get(pk=createdpk)
        expected_res = modelinstance_to_dict(create_res, SimplifiedDeadline._meta.resultfields.aslist(self.allExtras))

        self.assertEquals(read_res, expected_res)

    def test_create_security(self):

        # create an invalid deadline, which runs out before the
        # publishing date
        invalid_deadline_dict = dict(
            assignment_group=self.inf101_firstsem_a1_g1,
            deadline=self.inf101_firstsem_a1_g1.deadlines.order_by('deadline')[0].deadline + timedelta(days=-10),
            text='this deadline is impossible')
        with self.assertRaises(Exception):  # TODO: Where is ValidationError declared?
            SimplifiedDeadline.create(self.admin1, **invalid_deadline_dict)

        # Now try a valid deadline, but with a student
        valid = dict(
            assignment_group=self.inf101_firstsem_a1_g1,
            deadline=self.inf101_firstsem_a1_g1.deadlines.order_by('deadline')[0].deadline + timedelta(days=3),
            text='Last shot!')
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.create(self.firstStud, **valid)

        # and another admin that isnt an admin for this course
        self.add_to_path('uni;inf110:admin(inf110admin)')

        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.create(self.inf110admin, **valid)

        # see that the new admin can create a deadline where he is admin
        SimplifiedDeadline.create(self.inf110admin,
                                  assignment_group=self.inf110_secondsem_a1_g1,
                                  deadline=self.inf110_secondsem_a1_g1.deadlines.order_by('deadline')[0].deadline + timedelta(days=3),
                                  text='Last shot!')


class TestSimplifiedAdminFileMeta(SimplifiedAdminTestBase):

    allExtras = SimplifiedFileMeta._meta.resultfields.additional_aslist()
    baseFields = SimplifiedFileMeta._meta.resultfields.aslist()
    allFields = SimplifiedFileMeta._meta.resultfields.aslist(allExtras)

    def setUp(self):
        super(TestSimplifiedAdminFileMeta, self).setUp()

        for var in dir(self):
            # find any variable that ends with '_gN' where N is a
            # number
            if re.search('_g\d$', var):
                group = getattr(self, var)
                group.examiners.add(self.exam1)
                files = {'good.py': ['print ', 'awesome']}
                self.add_delivery(group, files)

    def test_search(self):
        # search with no query and no extra fields
        # should only have the deafault deadlines created when the
        # assignment group was created
        search_res = SimplifiedFileMeta.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2_deliveries[0].filemetas.all()[0], self.baseFields),
                        ]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedFileMeta.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2_deliveries[0].filemetas.all()[0], self.allFields),
                        ]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedFileMeta.search(self.admin1, query='secondStud')
        expected_res = [modelinstance_to_dict(self.inf101_secondsem_a1_g2_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2_deliveries[0].filemetas.all()[0], self.baseFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedFileMeta.search(self.admin1, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2_deliveries[0].filemetas.all()[0], self.allFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedFileMeta.read(self.admin1, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0],
                                             SimplifiedFileMeta._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedFileMeta.read(self.admin1, self.inf101_firstsem_a1_g1.deadlines.all()[0].id,
                                           result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0],
                                             SimplifiedFileMeta._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)
