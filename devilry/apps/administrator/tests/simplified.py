from datetime import timedelta
import re

from django.test import TransactionTestCase


from devilry.simplified import PermissionDenied, FilterValidationError, InvalidNumberOfResults, InvalidUsername
from devilry.simplified.utils import modelinstance_to_dict, fix_expected_data_missing_database_fields
from devilry.apps.core import models, testhelper
from devilry.apps.administrator.simplified import (SimplifiedNode, SimplifiedSubject, SimplifiedPeriod,
                                                   SimplifiedAssignment, SimplifiedAssignmentGroup,
                                                   SimplifiedDeadline, SimplifiedStaticFeedback,
                                                   SimplifiedFileMeta)

testhelper.TestHelper.set_memory_deliverystore()


class SimplifiedAdminTestBase(TransactionTestCase, testhelper.TestHelper):

    def setUp(self):
        self.create_superuser('superadminuser')

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

        self.add_to_path('uni;inf101:admin(testadmin).firstsem.a1.g1:candidate(teststud):examiner(testexam)')

class TestSimplifiedAdminNode(SimplifiedAdminTestBase):
    allExtras = SimplifiedNode._meta.resultfields.additional_aslist()

    def setUp(self):
        self.add(nodes='uni:admin(admin1).mat.inf')
        self.add(nodes='uni.fys')
        self.create_superuser('superadminuser')
        self.add_to_path('uni;inf101:admin(testadmin).firstsem.a1.g1:candidate(teststud):examiner(testexam)')

    def test_create_asadmin(self):
        kw = dict(
                long_name='TestOne',
                parentnode = self.uni)

        newpk = SimplifiedNode.create(self.admin1, short_name='test1', **kw)
        create_res = models.Node.objects.get(pk=newpk)
        self.assertEquals(create_res.short_name, 'test1')
        self.assertEquals(create_res.long_name, 'TestOne')
        self.assertEquals(create_res.parentnode, self.uni)

    def test_create_assuperadmin(self):
        newpk = SimplifiedNode.create(self.superadminuser, short_name='test1', long_name='TestOne', parentnode=None)
        create_res = models.Node.objects.get(pk=newpk)
        self.assertEquals(create_res.short_name, 'test1')
        self.assertEquals(create_res.long_name, 'TestOne')
        self.assertEquals(create_res.parentnode, None)

    def test_createmany_assuperadmin(self):
        list_of_field_values = [dict(short_name='test1', long_name='TestOne', parentnode=None),
                                dict(short_name='test2', long_name='TestTwo', parentnode=None),
                                dict(short_name='test3', long_name='TestThree', parentnode=None),
                                dict(short_name='test4', long_name='TestFour', parentnode=None)]
        newpks = SimplifiedNode.createmany(self.superadminuser, *list_of_field_values)
        for index, newpk in enumerate(newpks):
            expected = list_of_field_values[index]
            create_res = models.Node.objects.get(pk=newpk)
            self.assertEquals(create_res.short_name, expected['short_name'])
            self.assertEquals(create_res.long_name, expected['long_name'])
            self.assertEquals(create_res.parentnode, expected['parentnode'])

    def test_create_security_asstudent(self):
        # test that a student cant create a node
        kw = dict(
                long_name='TestOne',
                parentnode = self.uni)

        with self.assertRaises(PermissionDenied):
            SimplifiedNode.create(self.teststud, short_name='test1', **kw)

    def test_create_security_asexaminer(self):
        # test that an examiner cant create a node
        kw = dict(
                long_name='TestOne',
                parentnode = self.uni)

        with self.assertRaises(PermissionDenied):
            SimplifiedNode.create(self.testexam, short_name='test1', **kw)

    def test_create_security_assubjectadmin(self):
        # test that an admin for a subject cant create a node
        kw = dict(
                long_name='TestOne',
                parentnode = self.uni)

        with self.assertRaises(PermissionDenied):
            SimplifiedNode.create(self.testadmin, short_name='test1', **kw)

    def test_read(self):
        # do a read with no extra fields
        read_res = SimplifiedNode.read(self.admin1, self.uni.id)
        expected_res = modelinstance_to_dict(self.uni, SimplifiedNode._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedNode.read(self.admin1, self.uni.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.uni, SimplifiedNode._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security_asstudent(self):
        # test that a student cant read a node
        with self.assertRaises(PermissionDenied):
            read_res = SimplifiedNode.read(self.teststud, self.uni.id)

    def test_read_security_asexam(self):
        # test that a student cant read a node
        with self.assertRaises(PermissionDenied):
            read_res = SimplifiedNode.read(self.testexam, self.uni.id)

    def test_read_security_assubjectadmin(self):
        # test that a student cant read a node
        with self.assertRaises(PermissionDenied):
            read_res = SimplifiedNode.read(self.testadmin, self.uni.id)

    def test_update(self):
        self.assertEquals(self.uni.short_name, 'uni')

        kw = dict(short_name = 'testuni',
                    long_name = 'Test')

        pk = SimplifiedNode.update(self.admin1,
                            pk = self.uni.id,
                            **kw)
        update_res = models.Node.objects.get(pk=pk)
        self.assertEquals(update_res.short_name, 'testuni')

        self.assertEquals(self.uni.short_name, 'uni')
        self.refresh_var(self.uni)
        self.assertEquals(self.uni.short_name, 'testuni')

    def test_updatemany(self):
        list_of_field_values = [dict(short_name='test1', long_name='TestOne', parentnode=None),
                                dict(short_name='test2', long_name='TestTwo', parentnode=None),
                                dict(short_name='test3', long_name='TestThree', parentnode=None),
                                dict(short_name='test4', long_name='TestFour', parentnode=None)]
        updated_list_of_field_values = []
        for field_values in list_of_field_values:
            node = models.Node.objects.create(**field_values)
            updated_field_values = dict(pk=node.id,
                                        short_name=node.short_name + 'updated',
                                        long_name=node.long_name + 'updated')
            updated_list_of_field_values.append(updated_field_values)

        newpks = SimplifiedNode.updatemany(self.superadminuser, *updated_list_of_field_values)
        for index, newpk in enumerate(newpks):
            create_res = models.Node.objects.get(pk=newpk)

            not_expected = list_of_field_values[index]
            self.assertNotEquals(create_res.short_name, not_expected['short_name'])
            self.assertNotEquals(create_res.long_name, not_expected['long_name'])

            expected = updated_list_of_field_values[index]
            self.assertEquals(create_res.short_name, expected['short_name'])
            self.assertEquals(create_res.long_name, expected['long_name'])

    def test_update_security_asstudent(self):
        # test that an admin for a subject cant create a node
        kw = dict(
                short_name='test1',
                long_name='TestOne')

        with self.assertRaises(PermissionDenied):
            SimplifiedNode.update(self.teststud, pk=self.uni.id, **kw)

    def test_update_security_asexaminer(self):
        # test that an admin for a subject cant create a node
        kw = dict(
                short_name='test1',
                long_name='TestOne')

        with self.assertRaises(PermissionDenied):
            SimplifiedNode.update(self.testexam, pk=self.uni.id, **kw)

    def test_update_security_assubjectadmin(self):
        # test that an admin for a subject cant create a node
        kw = dict(
                short_name='test1',
                long_name='TestOne')

        with self.assertRaises(PermissionDenied):
            SimplifiedNode.update(self.testadmin, pk=self.uni.id, **kw)

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

    def test_search_noextras(self):
        # search with no query and no extra fields
        search_res = SimplifiedNode.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.uni, SimplifiedNode._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.uni_mat, SimplifiedNode._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.uni_fys, SimplifiedNode._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.uni_mat_inf, SimplifiedNode._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_allextras(self):
        # search with no querys, but all extra fields
        search_res = SimplifiedNode.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.uni, SimplifiedNode._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.uni_mat, SimplifiedNode._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.uni_fys, SimplifiedNode._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.uni_mat_inf, SimplifiedNode._meta.resultfields.aslist(self.allExtras))]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_withquery(self):
        # search with query
        search_res = SimplifiedNode.search(self.admin1, query='inf')
        expected_res = [modelinstance_to_dict(self.uni_mat_inf, SimplifiedNode._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_queryandextras(self):
        # with query and extra fields.
        search_res = SimplifiedNode.search(self.admin1, query='inf', result_fieldgroups = self.allExtras)
        expected_res = [modelinstance_to_dict(self.uni_mat_inf, SimplifiedNode._meta.resultfields.aslist(self.allExtras))]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedNode.search(self.teststud)
        self.assertEquals(search_res.count(), 0)

    def test_search_security_asexaminer(self):
        search_res = SimplifiedNode.search(self.testexam)
        self.assertEquals(search_res.count(), 0)

    def test_search_security_assubjectadmin(self):
        search_res = SimplifiedNode.search(self.testadmin)
        self.assertEquals(search_res.count(), 0)

    def test_delete_asnodeadmin(self):
        # this node has children and should raise permissiondenied
        with self.assertRaises(PermissionDenied):
            SimplifiedNode.delete(self.admin1, self.uni.id)

    def test_delete_assuperadmin(self):
        SimplifiedNode.delete(self.superadminuser, self.uni.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedNode.delete(self.superadminuser, self.uni.id)

    def test_deletemany(self):
        pks = []
        for short_name in ('a', 'b', 'c'):
            node = models.Node.objects.create(short_name=short_name)
            pks.append(node.pk)
        before = models.Node.objects.all().count()
        resuls_pks = SimplifiedNode.deletemany(self.superadminuser, *pks)
        after = models.Node.objects.all().count()
        self.assertEquals(after, before - 3)
        self.assertEquals(resuls_pks, tuple(pks))


    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedNode.delete(self.teststud, self.uni.id)
        with self.assertRaises(PermissionDenied):
            SimplifiedNode.delete(self.testexam, self.uni.id)

class TestSimplifiedAdminSubject(SimplifiedAdminTestBase):
    allExtras = SimplifiedSubject._meta.resultfields.additional_aslist()
    def setUp(self):
        super(TestSimplifiedAdminSubject,self).setUp()

    def test_create_asadmin(self):
        kw = dict(
                long_name='TestOne',
                parentnode = self.uni)

        newpk = SimplifiedSubject.create(self.admin1, short_name='test1', **kw)
        create_res = models.Subject.objects.get(pk=newpk)
        self.assertEquals(create_res.short_name, 'test1')
        self.assertEquals(create_res.long_name, 'TestOne')
        self.assertEquals(create_res.parentnode, self.uni)

    def test_create_assuperadmin(self):
        kw = dict(
                long_name='TestOne',
                parentnode = self.uni)

        newpk = SimplifiedSubject.create(self.superadminuser, short_name='test1', **kw)
        create_res = models.Subject.objects.get(pk=newpk)
        self.assertEquals(create_res.short_name, 'test1')
        self.assertEquals(create_res.long_name, 'TestOne')
        self.assertEquals(create_res.parentnode, self.uni)

    def test_create_security_asstudent(self):
        # test that a student cant create a subject
        kw = dict(
                long_name='TestOne',
                parentnode = self.uni)

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.create(self.teststud, short_name='test1', **kw)

    def test_create_security_asexaminer(self):
        # test that an examiner cant create a subject
        kw = dict(
                long_name='TestOne',
                parentnode = self.uni)

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.create(self.testexam, short_name='test1', **kw)

    def test_create_security_assubjectadmin(self):
        # test that an admin for a subject cant create a subject
        kw = dict(
                long_name='TestOne',
                parentnode = self.uni)

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.create(self.testadmin, short_name='test1', **kw)

    def test_read(self):
        # do a read with no extra fields
        read_res = SimplifiedSubject.read(self.admin1, self.inf110.id)
        expected_res = modelinstance_to_dict(self.inf110, SimplifiedSubject._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedSubject.read(self.admin1, self.inf110.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf110, SimplifiedSubject._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security_asstudent(self):
        # test that a student cant read a subject
        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.read(self.teststud, self.inf101.id)

    def test_read_security_asexam(self):
        # test that an examiner cant read a subject
        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.read(self.testexam, self.inf101.id)

    def test_read_security_assubjectadmin(self):
        # test that a subjectadmin cant read another subject
        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.read(self.testadmin, self.inf110.id)

    def test_update(self):
        self.assertEquals(self.inf110.short_name, 'inf110')

        kw = dict(short_name = 'test110',
                    long_name = 'Test')

        pk = SimplifiedSubject.update(self.admin1,
                            pk = self.inf110.id,
                            **kw)
        update_res = models.Subject.objects.get(pk=pk)
        self.assertEquals(update_res.short_name, 'test110')

        self.assertEquals(self.inf110.short_name, 'inf110')
        self.refresh_var(self.inf110)
        self.assertEquals(self.inf110.short_name, 'test110')

    def test_update_security_asstudent(self):
        # test that a student cant update another subject
        kw = dict(
                short_name='test1',
                long_name='TestOne')

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.update(self.teststud, pk=self.inf101.id, **kw)

    def test_update_security_asexaminer(self):
        # test that an examiner cant update another subject
        kw = dict(
                short_name='test1',
                long_name='TestOne')

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.update(self.testexam, pk=self.inf101.id, **kw)

    def test_update_security_assubjectadmin(self):
        # test that an admin for a subject cant update another subject
        kw = dict(
                short_name='test1',
                long_name='TestOne')

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.update(self.testadmin, pk=self.inf110.id, **kw)

    def test_search_filters(self):
        qrywrap = SimplifiedSubject.search(self.admin1)
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedSubject.search(self.admin1,
                                        filters=[dict(field='parentnode__short_name', comp='exact', value='uni')])
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedSubject.search(self.admin1,
                                        filters=[dict(field='short_name', comp='exact', value='inf110')])
        self.assertEquals(len(qrywrap), 1)

        with self.assertRaises(FilterValidationError):
            SimplifiedSubject.search(self.admin1,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='uni')])
        with self.assertRaises(FilterValidationError):
            SimplifiedSubject.search(self.admin1,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='uni')])
        with self.assertRaises(FilterValidationError):
            SimplifiedSubject.search(self.admin1,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='uni')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedSubject.search(self.admin1, exact_number_of_results=2)
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedSubject.search(self.admin1, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 2)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedSubject.search(self.admin1, exact_number_of_results=1)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedSubject.search(self.admin1, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedSubject.search(self.admin1, exact_number_of_results=0)

    def test_search_noextras(self):
        # search with no query and no extra fields
        search_res = SimplifiedSubject.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf110, SimplifiedSubject._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101, SimplifiedSubject._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_allextras(self):
        # search with no querys, but all extra fields
        search_res = SimplifiedSubject.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110, SimplifiedSubject._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101, SimplifiedSubject._meta.resultfields.aslist(self.allExtras))]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_withquery(self):
        # search with query
        search_res = SimplifiedSubject.search(self.admin1, query='11')
        expected_res = [modelinstance_to_dict(self.inf110, SimplifiedSubject._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_queryandextras(self):
        # with query and extra fields.
        search_res = SimplifiedSubject.search(self.admin1, query='11', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110, SimplifiedSubject._meta.resultfields.aslist(self.allExtras))]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedSubject.search(self.teststud)
        self.assertEquals(search_res.count(), 0)

    def test_search_security_asexaminer(self):
        search_res = SimplifiedSubject.search(self.testexam)
        self.assertEquals(search_res.count(), 0)

    def test_delete_asnodeadmin(self):
        self.add_to_path('uni;test111:admin(testadmin)')
        SimplifiedSubject.delete(self.testadmin, self.test111.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.delete(self.testadmin, self.test111.id)

        self.add_to_path('uni;inf101:admin(testadmin)')
        # this node has children and should raise permissionDenied
        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.delete(self.testadmin, self.inf101.id)

    def test_delete_assuperadmin(self):
        SimplifiedSubject.delete(self.superadminuser, self.inf101.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.delete(self.superadminuser, self.inf101.id)

    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.delete(self.firstStud, self.inf101.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.delete(self.exam1, self.inf101.id)

class TestSimplifiedAdminPeriod(SimplifiedAdminTestBase):
    allExtras = SimplifiedSubject._meta.resultfields.additional_aslist()
    def setUp(self):
        super(TestSimplifiedAdminPeriod, self).setUp()

    def test_create_asadmin(self):
        kw = dict(
                long_name='TestOne',
                parentnode = self.inf110,
                start_time = self.inf110_firstsem.start_time,
                end_time = self.inf110_firstsem.end_time)

        newpk = SimplifiedPeriod.create(self.admin1, short_name='test1', **kw)
        create_res = models.Period.objects.get(pk=newpk)
        self.assertEquals(create_res.short_name, 'test1')
        self.assertEquals(create_res.long_name, 'TestOne')
        self.assertEquals(create_res.parentnode, self.inf110)

    def test_create_assuperadmin(self):
        kw = dict(
                long_name='TestOne',
                parentnode = self.inf110,
                start_time = self.inf110_firstsem.start_time,
                end_time = self.inf110_firstsem.end_time)

        newpk = SimplifiedPeriod.create(self.superadminuser, short_name='test1', **kw)
        create_res = models.Period.objects.get(pk=newpk)
        self.assertEquals(create_res.short_name, 'test1')
        self.assertEquals(create_res.long_name, 'TestOne')
        self.assertEquals(create_res.parentnode, self.inf110)

    def test_create_security_asstudent(self):
        # test that a student cant create a period
        kw = dict(
                long_name='TestOne',
                parentnode = self.inf101,
                start_time = self.inf101_firstsem.start_time,
                end_time = self.inf101_firstsem.end_time)

        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.create(self.teststud, short_name='test1', **kw)

    def test_create_security_asexaminer(self):
        # test that an examiner cant create a period
        kw = dict(
                long_name='TestOne',
                parentnode = self.inf101,
                start_time = self.inf101_firstsem.start_time,
                end_time = self.inf101_firstsem.end_time)

        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.create(self.testexam, short_name='test1', **kw)

    def test_create_security_assubjectadmin(self):
        # test that an admin for a subject cant create a period for another subject
        kw = dict(
                long_name='TestOne',
                parentnode = self.inf110,
                start_time = self.inf110_firstsem.start_time,
                end_time = self.inf110_firstsem.end_time)

        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.create(self.testadmin, short_name='test1', **kw)

    def test_read(self):
        # do a read with no extra fields
        read_res = SimplifiedPeriod.read(self.admin1, self.inf110_firstsem.id)
        expected_res = modelinstance_to_dict(self.inf110_firstsem, SimplifiedPeriod._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

    def test_read_allextras(self):
        # do a read with all extras
        read_res = SimplifiedPeriod.read(self.admin1, self.inf110_firstsem.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf110_firstsem, SimplifiedPeriod._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security_asstudent(self):
        # test that a student cant read a period
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.read(self.teststud, self.inf101_firstsem.id)

    def test_read_security_asexam(self):
        # test that an examiner cant read a period
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.read(self.testexam, self.inf101_firstsem.id)

    def test_read_security_assubjectadmin(self):
        # test that a subjectadmin cant read another subjects period
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.read(self.testadmin, self.inf110_firstsem.id)

    def test_update(self):
        self.assertEquals(self.inf110_firstsem.short_name, 'firstsem')

        kw = dict(short_name = 'testsem',
                    long_name = 'TestPeriod')

        pk = SimplifiedPeriod.update(self.admin1,
                            pk = self.inf110_firstsem.id,
                            **kw)
        update_res = models.Period.objects.get(pk=pk)
        self.assertEquals(update_res.short_name, 'testsem')

        self.assertEquals(self.inf110_firstsem.short_name, 'firstsem')
        self.refresh_var(self.inf110_firstsem)
        self.assertEquals(self.inf110_firstsem.short_name, 'testsem')

    def test_update_security_asstudent(self):
        # test that a student cant update another subject
        kw = dict(
                short_name='test1',
                long_name='TestOne')

        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.update(self.teststud, pk=self.inf101_firstsem.id, **kw)

    def test_update_security_asexaminer(self):
        # test that an examiner cant update another subject
        kw = dict(
                short_name='test1',
                long_name='TestOne')

        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.update(self.testexam, pk=self.inf101_firstsem.id, **kw)

    def test_update_security_assubjectadmin(self):
        # test that an admin for a subject cant update another subject
        kw = dict(
                short_name='test1',
                long_name='TestOne')

        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.update(self.testadmin, pk=self.inf110_firstsem.id, **kw)

    def test_search_filters(self):
        qrywrap = SimplifiedPeriod.search(self.admin1)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedPeriod.search(self.admin1,
                                        filters=[dict(field='parentnode__short_name', comp='exact', value='inf110')])
        self.assertEquals(len(qrywrap), 2)

        with self.assertRaises(FilterValidationError):
            SimplifiedPeriod.search(self.admin1,
                                  filters=[dict(field='parentnode__INVALID__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedPeriod.search(self.admin1,
                                  filters=[dict(field='INVALIDparentnode__short_name', comp='exact', value='inf110')])
        with self.assertRaises(FilterValidationError):
            SimplifiedPeriod.search(self.admin1,
                                  filters=[dict(field='parentnode__short_nameINVALID', comp='exact', value='inf110')])

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedPeriod.search(self.admin1, exact_number_of_results=4)
        self.assertEquals(len(qrywrap), 4)
        qrywrap = SimplifiedPeriod.search(self.admin1, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 4)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedPeriod.search(self.admin1, exact_number_of_results=3)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedPeriod.search(self.admin1, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedPeriod.search(self.admin1, exact_number_of_results=0)

    def test_search_noextras(self):
        # search with no query and no extra fields
        search_res = SimplifiedPeriod.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf110_firstsem,SimplifiedPeriod._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem,SimplifiedPeriod._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstsem,SimplifiedPeriod._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondsem,SimplifiedPeriod._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_allextras(self):
        # search with no querys, but all extra fields
        search_res = SimplifiedPeriod.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_firstsem,SimplifiedPeriod._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem,SimplifiedPeriod._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstsem,SimplifiedPeriod._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_secondsem,SimplifiedPeriod._meta.resultfields.aslist(self.allExtras))]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_withquery(self):
        # search with query
        search_res = SimplifiedPeriod.search(self.admin1, query='11')
        expected_res = [modelinstance_to_dict(self.inf110_firstsem,SimplifiedPeriod._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem,SimplifiedPeriod._meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_queryandextras(self):
        # with query and extra fields.
        search_res = SimplifiedPeriod.search(self.admin1, query='11', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_firstsem,SimplifiedPeriod._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem,SimplifiedPeriod._meta.resultfields.aslist(self.allExtras))]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedPeriod.search(self.teststud)
        self.assertEquals(search_res.count(), 0)

    def test_search_security_asexaminer(self):
        search_res = SimplifiedPeriod.search(self.testexam)
        self.assertEquals(search_res.count(), 0)

    def test_delete_asnodeadmin(self):
        self.add_to_path('uni;test111.testsem:admin(testadmin)')
        SimplifiedPeriod.delete(self.testadmin, self.test111_testsem.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.delete(self.testadmin, self.test111_testsem.id)

        # this node has children so this should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.delete(self.admin1, self.inf101_firstsem.id)

    def test_delete_assuperadmin(self):
        SimplifiedPeriod.delete(self.superadminuser, self.inf101_firstsem.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.delete(self.superadminuser, self.inf101_firstsem.id)

    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.delete(self.firstStud, self.inf101_firstsem.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.delete(self.exam1, self.inf101_firstsem.id)

class TestSimplifiedAdminAssignment(SimplifiedAdminTestBase):
    allExtras = SimplifiedAssignment._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedAdminAssignment, self).setUp()

    def test_read_base(self):
        # do a read with no extra fields
        read_res = SimplifiedAssignment.read(self.admin1, self.inf101_firstsem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1,
                                             SimplifiedAssignment._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

    def test_read_period(self):
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

    def test_read_security_asstudent(self):
        # test that a student cant read a assignment
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.teststud, self.inf101_firstsem_a1.id)

    def test_read_security_asexam(self):
        # test that an examiner cant read an assignment
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.testexam, self.inf101_firstsem_a1.id)

    def test_read_security_assubjectadmin(self):
        # test that a subjectadmin cant read another subjects Assignments
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.testadmin, self.inf110_firstsem_a1.id)

    def test_read_security(self):
        self.add_to_path('uni;inf110.firstsem.a2.g1:candidate(testPerson)')

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.testPerson,
                    self.inf110_firstsem_a2.id)

        self.add_to_path('uni;inf110.firstsem.a2:admin(testPerson)')
        SimplifiedAssignment.read(self.testPerson, self.inf110_firstsem_a2.id)

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

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedAssignment.search(self.admin1, exact_number_of_results=8)
        self.assertEquals(len(qrywrap), 8)
        qrywrap = SimplifiedAssignment.search(self.admin1, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 8)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignment.search(self.admin1, exact_number_of_results=7)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignment.search(self.admin1, exact_number_of_results=9)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignment.search(self.admin1, exact_number_of_results=0)

    def test_search_noextras(self):
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

    def test_search_allextras(self):
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

    def test_search_query(self):
        # search with query
        search_res = SimplifiedAssignment.search(self.admin1, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_firstsem_a1, SimplifiedAssignment._meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondsem_a1, SimplifiedAssignment._meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_queryandextras(self):
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

    def test_search_security_asstudent(self):
        search_res = SimplifiedAssignment.search(self.teststud)
        self.assertEquals(search_res.count(), 0)

    def test_search_security_asexaminer(self):
        search_res = SimplifiedAssignment.search(self.testexam)
        self.assertEquals(search_res.count(), 0)

    def test_create(self):
        kw = dict(
                long_name='Test',
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

    def test_create_security_asstudent(self):
        kw = dict(
                long_name='Test',
                parentnode = self.inf110_firstsem_a2.parentnode,
                publishing_time = self.inf110_firstsem_a2.publishing_time)

        #test that a student cannot create an assignment
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.create(self.teststud, short_name='test1', **kw)

    def test_create_security_asexaminer(self):
        kw = dict(
                long_name='Test',
                parentnode = self.inf110_firstsem_a2.parentnode,
                publishing_time = self.inf110_firstsem_a2.publishing_time)

        #test that an administrator cannot create assignment for the wrong course
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.create(self.testexam, short_name='test1', **kw)

    def test_create_security_asadmin(self):
        kw = dict(
                long_name='Test',
                parentnode = self.inf110_firstsem_a2.parentnode,
                publishing_time = self.inf110_firstsem_a2.publishing_time)

        #test that an administrator cannot create assignment for the wrong course
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.create(self.testadmin, short_name='test1', **kw)

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

    def test_update_security_asstudent(self):
        kw = dict(
                long_name = 'TestAssignment',
                short_name = 'ta')

        #test that a student cannot change an assignment
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.update(self.teststud, pk=self.inf110_firstsem_a2.id, **kw)

    def test_update_security_asexaminer(self):
        kw = dict(
                long_name = 'TestAssignment',
                short_name = 'ta')

        #test that an examiner cannot change an assignment
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.update(self.testexam, pk=self.inf110_firstsem_a2.id, **kw)

    def test_update_security_asadmin(self):
        kw = dict(
                long_name = 'TestAssignment',
                short_name = 'ta')
        #test that an administrator cannot change assignment for the wrong course
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.update(self.testadmin, pk=self.inf110_firstsem_a2.id, **kw)

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
        self.add_delivery(self.inf101_firstsem_a1_g1)
        self.secondDelivery = self.add_delivery(self.inf101_firstsem_a1_g1)
        self.maxDiff = None # Shows entire diff
        
    def test_search_filters(self):
        qrywrap = SimplifiedAssignment.search(self.admin1)
        self.assertEquals(len(qrywrap), 8)
        qrywrap = SimplifiedAssignmentGroup.search(self.admin1,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='parentnode__short_name', comp='exact', value='a1')])
        self.assertEquals(len(qrywrap), 3)
        qrywrap = SimplifiedAssignmentGroup.search(self.admin1,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='parentnode__short_name', comp='exact', value='a2'),
                                                       dict(field='parentnode__parentnode__short_name', comp='endswith', value='sem'),
                                                       dict(field='parentnode__parentnode__parentnode__short_name', comp='endswith', value='101')])
        self.assertEquals(len(qrywrap), 2)

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=6)
        self.assertEquals(len(qrywrap), 6)
        qrywrap = SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 6)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=7)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=0)

    def test_search_noextras(self):
        # search with no query and no extra fields
        search_res = SimplifiedAssignmentGroup.search(self.admin1)
        test_groups = [self.inf101_firstsem_a1_g1,
                       self.inf101_firstsem_a2_g1, 
                       self.inf110_secondsem_a1_g1,
                       self.inf110_secondsem_a2_g1,
                       self.inf101_secondsem_a1_g2,
                       self.inf101_secondsem_a2_g2,]
        expected_res = map(lambda group: modelinstance_to_dict(group, self.baseFields), test_groups)
        
        expected_res[0].update(dict(latest_delivery_id=self.secondDelivery.id))
        for expected_resitem in expected_res[1:]:
            expected_resitem.update(dict(latest_delivery_id=None))

        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res, search_res)
        
        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])
            
    def test_search_allextras(self):
        # search with no query and with extra fields
        search_res = SimplifiedAssignmentGroup.search(self.admin1, result_fieldgroups=self.allExtras)
        test_groups = [self.inf101_firstsem_a1_g1,
                       self.inf101_firstsem_a2_g1, 
                       self.inf110_secondsem_a1_g1,
                       self.inf110_secondsem_a2_g1,
                       self.inf101_secondsem_a1_g2,
                       self.inf101_secondsem_a2_g2,]
        expected_res = map(lambda group: modelinstance_to_dict(group, self.allFields), test_groups)
        self.assertEquals(search_res.count(), len(expected_res))
        
        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res, search_res)
        
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])

    def test_search_query(self):
        # search with query
        search_res = SimplifiedAssignmentGroup.search(self.admin1, query='secondStud')
        test_groups = [self.inf101_secondsem_a1_g2,
                       self.inf101_secondsem_a2_g2,]
        expected_res = map(lambda group: modelinstance_to_dict(group, self.baseFields), test_groups)
        
        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res, search_res)
                
        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])

    def test_search_queryandextras(self):
        # with query and extra fields
        search_res = SimplifiedAssignmentGroup.search(self.admin1, query='inf101', result_fieldgroups=self.allExtras)
        test_groups = [self.inf101_firstsem_a1_g1,
                       self.inf101_firstsem_a2_g1,
                       self.inf101_secondsem_a1_g2,
                       self.inf101_secondsem_a2_g2,]
        expected_res = map(lambda group: modelinstance_to_dict(group, self.allFields), test_groups)

        # Fix missing database fields by adding data from the test_groups
        fix_expected_data_missing_database_fields(test_groups, expected_res, search_res)

        self.assertEquals(search_res.count(), len(expected_res))
        for i in xrange(len(search_res)):
            self.assertEquals(search_res[i], expected_res[i])

    def test_read(self):
        # This line is necessary for the value of 'status' to be equal and the test to pass.
        # TODO: Look at this when status is removed?
        self.inf101_firstsem_a1_g1.save()

        # do a read with no extra fields
        read_res = SimplifiedAssignmentGroup.read(self.admin1, self.inf101_firstsem_a1_g1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1,
                                             SimplifiedAssignmentGroup._meta.resultfields.aslist())
        self.assertDictEqual(read_res, expected_res)

    def test_read_allextras(self):
        # do a read with all extras
        read_res = SimplifiedAssignmentGroup.read(self.admin1, self.inf101_firstsem_a1_g1.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1,
                                             SimplifiedAssignmentGroup._meta.resultfields.aslist(self.allExtras))
        self.assertDictEqual(read_res, expected_res)

    def test_read_security_asstudent(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.teststud, self.inf101_firstsem_a1_g1.id)

    def test_read_security_asexam(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.testexam, self.inf101_firstsem_a1_g1.id)

    def test_read_security_asadmin(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.testadmin, self.inf110_secondsem_a1_g1.id)

    def test_create(self):
        kw = dict(
                name='test1',
                parentnode=self.inf101_firstsem_a1_g1.parentnode)

        newpk = SimplifiedAssignmentGroup.create(self.admin1, **kw)
        create_res = models.AssignmentGroup.objects.get(pk=newpk)
        self.assertEquals(create_res.name, 'test1')
        self.assertEquals(create_res.parentnode,
                self.inf101_firstsem_a1_g1.parentnode)

    def test_create_security_asstudent(self):
        kw = dict(
                long_name='Test',
                parentnode=self.inf101_firstsem_a1_g1.parentnode)

        #test that a student cannot create an assignmentgroup
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.create(self.teststud, **kw)

    def test_create_security_asexaminer(self):
        kw = dict(
                long_name='Test',
                parentnode=self.inf101_firstsem_a1_g1.parentnode)

        #test that an examiner cannot create assignmentgroup
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.create(self.testexam, **kw)

    def test_create_security_asadmin(self):
        kw = dict(
                long_name='Test',
                parentnode=self.inf110_secondsem_a1_g1.parentnode)

        #test that an administrator cannot create assignmentgroup for the wrong course
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.create(self.testadmin, **kw)

    def test_create_with_examiners_and_candidates(self):
        self.create_user('exampleexaminer1')
        self.create_user('exampleexaminer2')
        self.create_user('examplestudent1')
        self.create_user('examplestudent2')
        newpk = SimplifiedAssignmentGroup.create(self.admin1,
                                                 name='test1',
                                                 parentnode=self.inf101_firstsem_a1,
                                                 fake_examiners=('exampleexaminer1', 'exampleexaminer2'),
                                                 fake_candidates=(dict(username='examplestudent1'),
                                                                  dict(username='examplestudent2',
                                                                       candidate_id='23xx')))
        create_res = models.AssignmentGroup.objects.get(pk=newpk)
        self.assertEquals(create_res.name, 'test1')
        self.assertEquals(create_res.parentnode,
                          self.inf101_firstsem_a1_g1.parentnode)
        self.assertEquals(create_res.examiners.filter(user__username='exampleexaminer1').count(), 1)
        self.assertEquals(create_res.examiners.filter(user__username='exampleexaminer2').count(), 1)
        self.assertEquals(create_res.candidates.filter(student__username='examplestudent1').count(), 1)
        self.assertEquals(create_res.candidates.filter(student__username='examplestudent2').count(), 1)
        self.assertEquals(create_res.candidates.get(student__username='examplestudent2').candidate_id,
                          '23xx')


    def test_create_with_examiners_errors_rollback(self):
        def count():
            return models.AssignmentGroup.objects.filter(parentnode=self.inf101_firstsem_a1).count()
        count_before = count()
        try:
            SimplifiedAssignmentGroup.create(self.admin1,
                                             name='test1',
                                             parentnode=self.inf101_firstsem_a1,
                                             fake_examiners=('invalidexaminer',))
        except InvalidUsername, e:
            count_after = count() #make sure transaction rolls back everything
            self.assertEquals(count_before, count_after)

    def test_create_with_candidates_errors_rollback(self):
        self.create_user('exampleexaminer1')
        def count():
            return models.AssignmentGroup.objects.filter(parentnode=self.inf101_firstsem_a1).count()
        count_before = count()
        try:
            SimplifiedAssignmentGroup.create(self.admin1,
                                             name='test1',
                                             parentnode=self.inf101_firstsem_a1,
                                             fake_examiners=('exampleexaminer1',),
                                             fake_candidates=(dict(username='invaliduser'),)
                                            )
        except InvalidUsername, e:
            count_after = count() #make sure transaction rolls back everything
            self.assertEquals(count_before, count_after)

    def test_update_with_examiners_and_candidates(self):
        self.create_user('exampleexaminer1')
        self.create_user('exampleexaminer2')
        self.create_user('examplestudent1')
        self.create_user('examplestudent2')
        pk = SimplifiedAssignmentGroup.update(self.admin1,
                                              pk=self.inf101_firstsem_a1_g1.id,
                                              name='test1',
                                              parentnode=self.inf101_firstsem_a1_g1.parentnode,
                                              fake_examiners=('exampleexaminer1', 'exampleexaminer2'),
                                              fake_candidates=(dict(username='firstStud'),
                                                               dict(username='examplestudent1'),
                                                               dict(username='examplestudent2',
                                                                    candidate_id='23xx')))
        update_res = models.AssignmentGroup.objects.get(pk=pk)
        self.assertEquals(update_res.name, 'test1')
        self.assertEquals(update_res.parentnode,
                          self.inf101_firstsem_a1_g1.parentnode)
        self.assertEquals(update_res.examiners.filter(user__username='exampleexaminer1').count(), 1)
        self.assertEquals(update_res.examiners.filter(user__username='exampleexaminer2').count(), 1)
        self.assertEquals(update_res.candidates.filter(student__username='examplestudent1').count(), 1)
        self.assertEquals(update_res.candidates.filter(student__username='examplestudent2').count(), 1)
        self.assertEquals(update_res.candidates.get(student__username='examplestudent2').candidate_id,
                          '23xx')

    def test_update_remove_student_with_delivery(self):
        self.create_user('examplestudent1')
        self.assertRaises(PermissionDenied, SimplifiedAssignmentGroup.update,
                          self.admin1,
                          pk=self.inf101_firstsem_a1_g1.id,
                          name='test1',
                          parentnode=self.inf101_firstsem_a1_g1.parentnode,
                          fake_candidates=(dict(username='examplestudent1'),))

    def test_update_with_candidates_errors_rollback(self):
        self.create_user('exampleexaminer1')
        self.create_user('exampleexaminer2')
        def get():
            return models.AssignmentGroup.objects.get(id=self.inf101_firstsem_a1_g1.id)
        before = get()
        self.assertEquals(before.examiners.count(), 3)
        self.assertEquals(before.candidates.count(), 2)
        try:
            SimplifiedAssignmentGroup.update(self.admin1,
                                             pk=self.inf101_firstsem_a1_g1.id,
                                             name='updated',
                                             parentnode=self.inf101_firstsem_a1,
                                             fake_examiners=('exampleexaminer1'),
                                             fake_candidates=(dict(username='invaliduser'),)
                                            )
        except InvalidUsername, e:
            #make sure transaction rolls back everything
            after = get()
            self.assertEquals(after.name, before.name)
            self.assertEquals(after.examiners.count(), 3)
            self.assertEquals(after.candidates.count(), 2)

    def test_update(self):
        kw = dict(name = 'test')

        self.assertEquals(self.inf101_firstsem_a1_g1.name, 'g1')

        newpk = SimplifiedAssignmentGroup.update(self.admin1, pk = self.inf101_firstsem_a1_g1.id, **kw)
        create_res = models.AssignmentGroup.objects.get(pk=newpk)
        self.assertEquals(create_res.name, 'test')

    def test_update_security_asstudent(self):
        #test that a student cannot create an assignmentgroup
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.update(self.teststud, pk = self.inf101_firstsem_a1_g1.id, name='test')

    def test_update_security_asexaminer(self):
        #test that an examiner cannot create assignmentgroup
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.update(self.testexam, pk = self.inf101_firstsem_a1_g1.id, name='test')

    def test_update_security_asadmin(self):
        #test that an administrator cannot create assignmentgroup for the wrong course
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.update(self.testadmin, pk = self.inf110_secondsem_a1_g1.id, name='test')

    def test_delete_asnodeadmin(self):
        self.add_to_path('uni;inf101.firstsem:admin(testadmin)')
        # this node has children and should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.delete(self.testadmin, self.inf101_firstsem_a1_g1.id)

    def test_delete_assuperadmin(self):
        SimplifiedAssignmentGroup.delete(self.superadminuser, self.inf101_firstsem_a1_g1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.delete(self.superadminuser, self.inf101_firstsem_a1_g1.id)

    def test_delete_noperm_asstudent(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.delete(self.teststud, self.inf101_firstsem_a1_g1.id)

    def test_delete_noperm_asexam(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.delete(self.testexam, self.inf101_firstsem_a1_g1.id)


class TestSimplifiedAdminStaticFeedback(SimplifiedAdminTestBase):

    allExtras = SimplifiedStaticFeedback._meta.resultfields.additional_aslist()

    def setUp(self):
        super(TestSimplifiedAdminStaticFeedback, self).setUp()
        # we need to add some deliveries here! Use the admin of uni as
        # an examiner
        # add deliveries and feedbacks to every group that was
        # created. Default values are good enough
        for var in dir(self):
            # find any variable that ends with '_gN' where N is a
            # number
            if re.search('_g\d$', var):
                group = getattr(self, var)
                if group.examiners.filter(user=self.exam1).count() == 0:
                    group.examiners.create(user=self.exam1)
                self.add_delivery(group)
                self.add_feedback(group)

    def test_search_filters(self):
        qrywrap = SimplifiedStaticFeedback.search(self.admin1)
        self.assertEquals(len(qrywrap), 6)
        qrywrap = SimplifiedStaticFeedback.search(self.admin1,
                                              filters=[dict(field='delivery', comp='exact', value='1')])
        self.assertEquals(len(qrywrap), 1)

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedStaticFeedback.search(self.admin1, exact_number_of_results=6)
        self.assertEquals(len(qrywrap), 6)
        qrywrap = SimplifiedStaticFeedback.search(self.admin1, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 6)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedStaticFeedback.search(self.admin1, exact_number_of_results=7)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedStaticFeedback.search(self.admin1, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedStaticFeedback.search(self.admin1, exact_number_of_results=0)

    def test_search_noextras(self):
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

    def test_search_allextras(self):
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

    def test_search_query(self):
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

    def test_search_queryandextras(self):
        # with query and extra fields
        search_res = SimplifiedStaticFeedback.search(self.admin1, query='inf110', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondsem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedStaticFeedback.search(self.teststud)
        self.assertEquals(search_res.count(), 0)

    def test_search_security_asexaminer(self):
        search_res = SimplifiedStaticFeedback.search(self.testexam)
        self.assertEquals(search_res.count(), 0)

    def test_read(self):
        # do a read with no extra fields
        read_res = SimplifiedStaticFeedback.read(self.admin1, self.inf101_firstsem_a1_g1_feedbacks[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                             SimplifiedStaticFeedback._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

    def test_read_allextras(self):
        # do a read with all extras
        read_res = SimplifiedStaticFeedback.read(self.admin1, self.inf101_firstsem_a1_g1_feedbacks[0].id,
                                           result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_feedbacks[0],
                                             SimplifiedStaticFeedback._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security_asstudent(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.teststud, self.inf101_firstsem_a1_g1_feedbacks[0].id)

    def test_read_security_asexaminer(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.testexam, self.inf101_firstsem_a1_g1_feedbacks[0].id)

    def test_read_security_asadmin(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.testadmin, self.inf110_secondsem_a1_g1_feedbacks[0].id)

    def test_delete_asnodeadmin(self):
        self.add_to_path('uni;inf101:admin(testadmin)')
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.delete(self.testadmin, self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

    def test_delete_assuperadmin(self):
        delid = self.inf101_firstsem_a1_g1.deadlines.all()[0].id
        SimplifiedStaticFeedback.delete(self.superadminuser, delid)

        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.delete(self.superadminuser, delid)

    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.delete(self.firstStud, self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.delete(self.exam1, self.inf101_firstsem_a1_g1.deadlines.all()[0].id)


class TestSimplifiedAdminDeadline(SimplifiedAdminTestBase):

    allExtras = SimplifiedDeadline._meta.resultfields.additional_aslist()
    baseFields = SimplifiedDeadline._meta.resultfields.aslist()
    allFields = SimplifiedDeadline._meta.resultfields.aslist(allExtras)

    def setUp(self):
        super(TestSimplifiedAdminDeadline, self).setUp()

    def test_search_filters(self):
        qrywrap = SimplifiedDeadline.search(self.admin1)
        self.assertEquals(len(qrywrap), 6)
        qrywrap = SimplifiedDeadline.search(self.admin1,
                                              #result_fieldgroups=['subject'], # has no effect on filters but nice for debugging
                                              filters=[dict(field='assignment_group__parentnode__short_name', comp='exact', value='a1'),
                                                       dict(field='assignment_group__parentnode__parentnode__short_name', comp='endswith', value='sem'),
                                                       dict(field='assignment_group__parentnode__parentnode__parentnode__short_name', comp='endswith', value='101')])
        self.assertEquals(len(qrywrap), 2)

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=6)
        self.assertEquals(len(qrywrap), 6)
        qrywrap = SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 6)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedDeadline.search(self.admin1, exact_number_of_results=7)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedDeadline.search(self.admin1, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedDeadline.search(self.admin1, exact_number_of_results=0)

    def test_search_noextras(self):
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
        for expected in expected_res: # Set annotated fields
            expected['number_of_deliveries'] = 0

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_allextras(self):
        # search with no query and with extra fields
        search_res = SimplifiedDeadline.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2.deadlines.all()[0], self.allFields),
                        ]
        for expected in expected_res: # Set annotated fields
            expected['number_of_deliveries'] = 0

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_query(self):
        # search with query
        search_res = SimplifiedDeadline.search(self.admin1, query='secondStud')
        expected_res = [modelinstance_to_dict(self.inf101_secondsem_a1_g2.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2.deadlines.all()[0], self.baseFields)]
        for expected in expected_res: # Set annotated fields
            expected['number_of_deliveries'] = 0

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_queryandextras(self):
        # with query and extra fields
        search_res = SimplifiedDeadline.search(self.admin1, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2.deadlines.all()[0], self.allFields)]
        for expected in expected_res: # Set annotated fields
            expected['number_of_deliveries'] = 0

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_query_newdeadlines_andextras(self):
        # add some new deadlines, to simulate groups getting a second
        # chance
        self.add_to_path('uni;inf101.secondsem.a1.g2.deadline:ends(10):text(This is your last shot!)')

        search_res = SimplifiedDeadline.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondsem_a2_g1.deadlines.all()[0], self.allFields),
                        # this group now has 2 deadlines. make sure to include the old one here
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_deadline2, self.allFields),
                        # and the new one here
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_deadlines[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2.deadlines.all()[0], self.allFields),
                        ]
        for expected in expected_res: # Set annotated fields
            expected['number_of_deliveries'] = 0

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedDeadline.search(self.teststud)
        self.assertEquals(search_res.count(), 0)

    def test_search_security_asexam(self):
        search_res = SimplifiedDeadline.search(self.testexam)
        self.assertEquals(search_res.count(), 0)

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

    def test_read_security_asstud(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.read(self.teststud, self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

    def test_read_security_asexam(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.read(self.testexam, self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

    def test_read_security_asadmin(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.read(self.testadmin, self.inf110_secondsem_a1_g1.deadlines.all()[0].id)

    def test_create(self):
        # create a deadline that runs out in 3 days
        kw = dict(
            assignment_group=self.inf101_firstsem_a1_g1,
            deadline=self.inf101_firstsem_a1.publishing_time + timedelta(days=3),
            text='Last shot!')

        createdpk = SimplifiedDeadline.create(self.admin1, **kw)
        read_res = SimplifiedDeadline.read(self.admin1, createdpk, result_fieldgroups=self.allExtras)
        create_res = models.Deadline.objects.get(pk=createdpk)
        expected_res = modelinstance_to_dict(create_res, SimplifiedDeadline._meta.resultfields.aslist(self.allExtras))

        self.assertEquals(read_res, expected_res)

    def test_create_invaliddeadline(self):
        # create an invalid deadline, which runs out before the
        # publishing date
        invalid_deadline_dict = dict(
            assignment_group=self.inf101_firstsem_a1_g1,
            deadline=self.inf101_firstsem_a1_g1.deadlines.order_by('deadline')[0].deadline + timedelta(days=-11),
            text='this deadline is impossible')
        with self.assertRaises(Exception):  # TODO: Where is ValidationError declared?
            SimplifiedDeadline.create(self.admin1, **invalid_deadline_dict)

    def test_create_security_asstudent(self):
        kw = dict(
            assignment_group=self.inf101_firstsem_a1_g1,
            deadline=self.inf101_firstsem_a1_g1.deadlines.order_by('deadline')[0].deadline + timedelta(days=3),
            text='Last shot!')

        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.create(self.teststud, **kw)

    def test_create_security_asexam(self):
        kw = dict(
            assignment_group=self.inf101_firstsem_a1_g1,
            deadline=self.inf101_firstsem_a1_g1.deadlines.order_by('deadline')[0].deadline + timedelta(days=3),
            text='Last shot!')

        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.create(self.testexam, **kw)

    def test_create_security_asadmin(self):
        kw = dict(
            assignment_group=self.inf110_secondsem_a1_g1,
            deadline=self.inf110_secondsem_a1_g1.deadlines.order_by('deadline')[0].deadline + timedelta(days=3),
            text='Last shot!')

        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.create(self.testadmin, **kw)

    def test_delete_asnodeadmin(self):
        self.add_to_path('uni;inf101:admin(testadmin)')
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.delete(self.testadmin, self.inf101_firstsem_a1_g1.deadlines.all()[0].id)

    def test_delete_assuperadmin(self):
        delid = self.inf101_firstsem_a1_g1.deadlines.all()[0].id
        SimplifiedDeadline.delete(self.superadminuser, delid)

        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.delete(self.superadminuser, delid)

    def test_delete_noperm(self):
        delid = self.inf101_firstsem_a1_g1.deadlines.all()[0].id
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.delete(self.firstStud, delid)

        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.delete(self.exam1, delid)

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
                if group.examiners.filter(user=self.exam1).count() == 0:
                    group.examiners.create(user=self.exam1)
                files = {'good.py': ['print ', 'awesome']}
                self.add_delivery(group, files)

    def test_search_filters(self):
        qrywrap = SimplifiedFileMeta.search(self.admin1)
        self.assertEquals(len(qrywrap), 6)
        qrywrap = SimplifiedFileMeta.search(self.admin1,
                                              filters=[dict(field='delivery', comp='exact', value='1')])
        self.assertEquals(len(qrywrap), 1)

    def test_search_exact_number_of_results(self):
        qrywrap = SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=6)
        self.assertEquals(len(qrywrap), 6)
        qrywrap = SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=None)
        self.assertEquals(len(qrywrap), 6)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=7)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=5)
        with self.assertRaises(InvalidNumberOfResults):
            SimplifiedAssignmentGroup.search(self.admin1, exact_number_of_results=0)

    def test_search_noextras(self):
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

    def test_search_allextras(self):
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

    def test_search_query(self):
        # search with query
        search_res = SimplifiedFileMeta.search(self.admin1, query='secondStud')
        expected_res = [modelinstance_to_dict(self.inf101_secondsem_a1_g2_deliveries[0].filemetas.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2_deliveries[0].filemetas.all()[0], self.baseFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_queryandextras(self):
        # with query and extra fields
        search_res = SimplifiedFileMeta.search(self.admin1, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstsem_a2_g1_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a1_g2_deliveries[0].filemetas.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondsem_a2_g2_deliveries[0].filemetas.all()[0], self.allFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security_asstudent(self):
        search_res = SimplifiedFileMeta.search(self.teststud)
        self.assertEquals(search_res.count(), 0)

    def test_search_security_asexaminer(self):
        search_res = SimplifiedFileMeta.search(self.testexam)
        self.assertEquals(search_res.count(), 0)

    def test_read(self):
        # do a read with no extra fields
        read_res = SimplifiedFileMeta.read(self.admin1, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0],
                                             SimplifiedFileMeta._meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

    def test_read_allextras(self):
        # do a read with all extras
        read_res = SimplifiedFileMeta.read(self.admin1, self.inf101_firstsem_a1_g1.deadlines.all()[0].id,
                                           result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0],
                                             SimplifiedFileMeta._meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security_asstudent(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedFileMeta.read(self.teststud, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)

    def test_read_security_asexaminer(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedFileMeta.read(self.testexam, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)

    def test_read_security_asadmin(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedFileMeta.read(self.testadmin, self.inf110_secondsem_a1_g1_deliveries[0].filemetas.all()[0].id)

    def test_delete_asnodeadmin(self):
        self.add_to_path('uni;inf101:admin(testadmin)')
        with self.assertRaises(PermissionDenied):
            SimplifiedFileMeta.delete(self.testadmin, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)

    def test_delete_assuperadmin(self):
        delid = self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id
        SimplifiedFileMeta.delete(self.superadminuser, delid)

        with self.assertRaises(PermissionDenied):
            SimplifiedFileMeta.delete(self.superadminuser, delid)

    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedFileMeta.delete(self.firstStud, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)

        with self.assertRaises(PermissionDenied):
            SimplifiedFileMeta.delete(self.exam1, self.inf101_firstsem_a1_g1_deliveries[0].filemetas.all()[0].id)
