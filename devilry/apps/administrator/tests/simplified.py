from django.test import TestCase

import re

from ....simplified import PermissionDenied

from ...core import testhelper
from ....simplified.utils import modelinstance_to_dict
from ..simplified import SimplifiedNode, SimplifiedSubject, SimplifiedPeriod, SimplifiedAssignment, SimplifiedAssignmentGroup, SimplifiedStaticFeedback
from ....simplified.utils import modelinstance_to_dict
from ...core import models, testhelper
from ..simplified import SimplifiedNode, SimplifiedSubject, SimplifiedPeriod, SimplifiedAssignment, SimplifiedAssignmentGroup, SimplifiedDeadline

class SimplifiedAdminTestBase(TestCase, testhelper.TestHelper):

    def setUp(self):
        # create a base structure
        self.add(nodes='uni:admin(admin1)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstSem', 'secondSem:admin(admin2)'],
                 assignments=['a1', 'a2'])

        # add firstStud to the first and secondSem assignments
        self.add_to_path('uni;inf101.firstSem.a1.g1:candidate(firstStud):examiner(exam1,exam3)')
        self.add_to_path('uni;inf101.firstSem.a2.g1:candidate(firstStud):examiner(exam1)')
        self.add_to_path('uni;inf110.secondSem.a1.g1:candidate(firstStud):examiner(exam2)')
        self.add_to_path('uni;inf110.secondSem.a2.g1:candidate(firstStud):examiner(exam2)')

        # secondStud began secondSem
        self.add_to_path('uni;inf101.secondSem.a1.g2:candidate(secondStud):examiner(exam1)')
        self.add_to_path('uni;inf101.secondSem.a2.g2:candidate(secondStud):examiner(exam1)')
        
###########################################################################
# commented out the old tests for administrator because the old testdata no
# longer exists. Need to rewrite these to match data from the new
# testdatagenerator
###########################################################################


#class TestSimplifiedAdministratorSimplifiedNode(TestCase, testhelper.Testhelper):
    #fixtures = ["simplified/data.json"]

    #def setUp(self):
        #self.grandma = User.objects.get(username='grandma') # superuser
        #self.clarabelle = User.objects.get(username="clarabelle")
        #self.univ = models.Node.objects.get(short_name='univ')
        #self.duckburgh = models.Node.objects.get(short_name='duckburgh')
        #self.univ.admins.add(self.clarabelle)
        #self.duckburgh.admins.add(self.clarabelle)

        #self.daisy = User.objects.get(username="daisy")
        #self.assertEquals(0,
                #models.Node.where_is_admin_or_superadmin(self.daisy).count())

        #self.invalidid = 100000
        #self.assertRaises(models.Node.DoesNotExist, models.Node.objects.get,
                #id=self.invalidid)



    #def test_create(self):
        #kw = dict(long_name='Test',
                #parentnode_id=self.univ.id)
        #node = SimplifiedNode.create(self.clarabelle, short_name='test1', **kw)
        #self.assertEquals(node.short_name, 'test1')
        #self.assertEquals(node.long_name, 'Test')
        #self.assertEquals(node.parentnode, self.univ)

    #def test_create_sequrity(self):
        #kw = dict(long_name='Test',
                #parentnode_id=self.univ.id)
        #node = SimplifiedNode.create(self.grandma, short_name='test2', **kw) # superuser allowed
        #with self.assertRaises(PermissionDenied):
            #node = SimplifiedNode.create(self.daisy, short_name='test3', **kw)

    #def test_create_validation(self):
        #with self.assertRaises(models.Node.DoesNotExist):
            #SimplifiedNode.create(self.clarabelle,
                    #short_name='test',
                    #long_name='Test',
                    #parentnode_id=self.invalidid)
        #with self.assertRaisesRegexp(ValidationError,
                #"long_name.*short_name"):
            #SimplifiedNode.update(
                    #self.clarabelle, self.duckburgh.id,
                    #short_name=None, long_name=None)

    #def test_insecure_read_model(self):
        #node = SimplifiedNode.insecure_read_model(self.clarabelle, idorkw=self.univ.id)
        #node = SimplifiedNode.insecure_read_model(self.grandma, self.univ.id) # superuser allowed
        #node = SimplifiedNode.insecure_read_model(self.grandma, dict(short_name=self.univ.short_name))
        #self.assertEquals(node.short_name, 'univ')
        #node = SimplifiedNode.insecure_read_model(self.grandma, idorkw=self.univ.id)
        #self.assertEquals(node.short_name, 'univ')

    #def test_insecure_read_model_security(self):
        #with self.assertRaises(PermissionDenied):
            #node = SimplifiedNode.insecure_read_model(self.daisy, self.univ.id)

    #def test_update(self):
        #self.assertEquals(self.duckburgh.short_name, 'duckburgh')
        #self.assertEquals(self.duckburgh.long_name, 'Duckburgh')
        #self.assertEquals(self.duckburgh.parentnode, None)

        #kw = dict(idorkw=self.duckburgh.id,
                    #short_name='test',
                    #long_name='Test',
                    #parentnode_id=self.univ.id)
        #node = SimplifiedNode.update(self.clarabelle, **kw)
        #self.assertEquals(node.short_name, 'test')
        #self.assertEquals(node.long_name, 'Test')
        #self.assertEquals(node.parentnode, self.univ)

    #def test_update_security(self):
        #kw = dict(idorkw=self.duckburgh.id,
                    #short_name='test',
                    #long_name='Test',
                    #parentnode_id=self.univ.id)
        
        #with self.assertRaises(PermissionDenied):
            #node = SimplifiedNode.update(self.daisy, **kw)

        #node = SimplifiedNode.update(self.grandma, **kw) # superuser allowed
        #node = SimplifiedNode.update(self.grandma,
                #dict(short_name='test'),
                #long_name = 'My Duckburgh Test')
        #self.assertEquals(node.long_name, 'My Duckburgh Test')
        
    #def test_update_validation(self):
        #with self.assertRaises(models.Node.DoesNotExist):
            #SimplifiedNode.update(self.clarabelle,
                    #idorkw=self.duckburgh.id,
                    #short_name='test',
                    #long_name='Test',
                    #parentnode_id=self.invalidid)
        #with self.assertRaises(models.Node.DoesNotExist):
            #SimplifiedNode.update(self.clarabelle,
                    #idorkw=self.invalidid,
                    #short_name='test2',
                    #long_name='Test 2',
                    #parentnode_id=None)
        #with self.assertRaisesRegexp(ValidationError,
                #"long_name.*short_name"):
            #SimplifiedNode.update(
                    #self.clarabelle, self.duckburgh.id,
                    #short_name=None, long_name=None)


    #def test_delete_asnodeadmin(self):
        #SimplifiedNode.delete(self.clarabelle, idorkw=self.univ.id)
        #with self.assertRaises(models.Node.DoesNotExist):
            #node = models.Node.objects.get(id=self.univ.id)

    #def test_delete_asnodeadmin_by_short_name(self):
        #SimplifiedNode.delete(self.clarabelle, dict(short_name='univ'))
        #with self.assertRaises(models.Node.DoesNotExist):
            #SimplifiedNode.delete(self.clarabelle, dict(short_name='univ'))

    #def test_delete_assuperadmin(self):
        #SimplifiedNode.delete(self.grandma, idorkw=self.univ.id)
        #with self.assertRaises(models.Node.DoesNotExist):
            #node = models.Node.objects.get(id=self.univ.id)
    #def test_delete_noperm(self):
        #with self.assertRaises(PermissionDenied):
            #SimplifiedNode.delete(self.daisy, idorkw=self.univ.id)


    #def test_search(self):
        #clarabelle = User.objects.get(username="clarabelle")
        #nodes = models.Node.objects.all().order_by("short_name")
        #qrywrap = SimplifiedNode.search(self.clarabelle)
        #self.assertEquals(len(qrywrap), len(nodes))
        #self.assertEquals(qrywrap[0]['short_name'], nodes[0].short_name)

        ## query
        #qrywrap = SimplifiedNode.search(self.clarabelle, query="burgh")
        #self.assertEquals(len(qrywrap), 1)
        #qrywrap = SimplifiedNode.search(self.clarabelle, query="univ")
        #self.assertEquals(len(qrywrap), 1)
        #qrywrap = SimplifiedNode.search(self.clarabelle)
        #self.assertEquals(len(qrywrap), 2)
        #qrywrap = SimplifiedNode.search(self.grandma)
        #self.assertEquals(len(qrywrap), len(nodes))

        #self.univ.parentnode = self.duckburgh
        #self.univ.save()
        #qrywrap = SimplifiedNode.search(self.grandma,
                #parentnode_id=self.duckburgh.id)
        #self.assertEquals(len(qrywrap), 1)
        #self.assertEquals(qrywrap[0]['short_name'], 'univ')

    #def test_search_security(self):
        #qrywrap = SimplifiedNode.search(self.daisy)
        #self.assertEquals(len(qrywrap), 0)

        #self.duckburgh.admins.add(self.daisy)
        #qrywrap = SimplifiedNode.search(self.daisy)
        #self.assertEquals(len(qrywrap), 1)


#class TestSimplifiedAdministratorSimplifiedSubject(TestCase, testhelper.Testhelper):
    #fixtures = ["simplified/data.json"]

    #def setUp(self):
        #self.grandma = User.objects.get(username='grandma') # superuser
        #self.duck1100 = models.Subject.objects.get(short_name='duck1100')
        #self.clarabelle = User.objects.get(username="clarabelle")
        #self.univ = models.Node.objects.get(short_name='univ')
        #self.duckburgh = models.Node.objects.get(short_name='duckburgh')
        #self.univ.admins.add(self.clarabelle)
        #self.duckburgh.admins.add(self.clarabelle)
        #self.daisy = User.objects.get(username="daisy")
        #self.assertEquals(0,
                #models.Node.where_is_admin_or_superadmin(self.daisy).count())

    #def test_insecure_read_model(self):
        #subject = SimplifiedSubject.insecure_read_model(self.clarabelle, idorkw=self.duck1100.id)
        #subject = SimplifiedSubject.insecure_read_model(self.clarabelle, self.duck1100.id)
        #self.assertEquals(subject.short_name, 'duck1100')
        #subject = SimplifiedSubject.insecure_read_model(self.clarabelle,
                #dict(short_name=self.duck1100.short_name))
        #self.assertEquals(subject.short_name, 'duck1100')

    #def test_insecure_read_model_security(self):
        #subject = SimplifiedSubject.insecure_read_model(self.grandma, self.duck1100.id) # superuser allowed
        #with self.assertRaises(PermissionDenied):
            #node = SimplifiedSubject.insecure_read_model(self.daisy, self.duck1100.id)

    #def test_read(self):
        #subject = SimplifiedSubject.read(self.grandma, self.duck1100.id)
        #self.assertEquals(subject, dict(
                #short_name = 'duck1100',
                #long_name = self.duck1100.long_name,
                #id = self.duck1100.id))

    #def test_search(self):
        #subjects = models.Subject.where_is_admin_or_superadmin(self.grandma).order_by("short_name")
        #qrywrap = SimplifiedSubject.search(self.grandma)
        #self.assertEquals(len(qrywrap), len(subjects))
        #self.assertEquals(qrywrap[0]['short_name'], subjects[0].short_name)

        ## query
        #qrywrap = SimplifiedSubject.search(self.grandma, query="duck1")
        #self.assertEquals(len(qrywrap), 2)
        #qrywrap = SimplifiedSubject.search(self.grandma, query="duck")
        #self.assertEquals(len(qrywrap), len(subjects))
        #qrywrap = SimplifiedSubject.search(self.grandma, query="1100")
        #self.assertEquals(len(qrywrap), 1)

    #def test_search_security(self):
        #qrywrap = SimplifiedSubject.search(self.daisy, query="1100")
        #self.assertEquals(len(qrywrap), 0)
        #self.duck1100.admins.add(self.daisy)
        #qrywrap = SimplifiedSubject.search(self.daisy, query="1100")
        #self.assertEquals(len(qrywrap), 1)


    #def test_create(self):
        #kw = dict(long_name='Test',
                #parentnode_id=self.univ.id)
        #subject = SimplifiedSubject.create(self.clarabelle, short_name='test1', **kw)
        #self.assertEquals(subject.short_name, 'test1')
        #self.assertEquals(subject.long_name, 'Test')
        #self.assertEquals(subject.parentnode, self.univ)

    #def test_create_security(self):
        #kw = dict(long_name='Test',
                #parentnode_id=self.univ.id)
        #subject = SimplifiedSubject.create(self.grandma, short_name='test2', **kw) # superuser allowed
        #with self.assertRaises(PermissionDenied):
            #subject = SimplifiedSubject.create(self.daisy, short_name='test3', **kw)

    #def test_update(self):
        #self.assertEquals(self.duck1100.short_name, 'duck1100')

        #kw = dict(id=self.duck1100.id,
                    #short_name='test',
                    #long_name='Test',
                    #parentnode_id=self.univ.id)
        #subject = SimplifiedSubject.update(self.clarabelle, idorkw=self.duck1100.id, **kw)
        #self.assertEquals(subject.short_name, 'test')
        #self.assertEquals(subject.long_name, 'Test')
        #self.assertEquals(subject.parentnode, self.univ)
        
    #def test_update_security(self):
        #kw = dict(id=self.duck1100.id,
                    #short_name='test',
                    #long_name='Test',
                    #parentnode_id=self.univ.id)
        #with self.assertRaises(PermissionDenied):
            #subject = SimplifiedSubject.update(self.daisy, idorkw=self.duck1100.id, **kw)
    
    #def test_delete_asnodeadmin(self):
        #SimplifiedSubject.delete(self.clarabelle, idorkw=self.duck1100.id)
        #with self.assertRaises(models.Subject.DoesNotExist):
            #subject = models.Subject.objects.get(id=self.duck1100.id)

    #def test_delete_asnodeadmin_by_short_name(self):
        #SimplifiedSubject.delete(self.clarabelle, dict(short_name='duck1100'))
        #with self.assertRaises(models.Subject.DoesNotExist):
            #SimplifiedSubject.delete(self.clarabelle, dict(short_name='duck1100'))

    #def test_delete_assuperadmin(self):
        #SimplifiedSubject.delete(self.grandma, idorkw=self.duck1100.id)
        #with self.assertRaises(models.Subject.DoesNotExist):
            #subject = models.Subject.objects.get(id=self.duck1100.id)

    #def test_delete_noperm(self):
        #with self.assertRaises(PermissionDenied):
            #SimplifiedSubject.delete(self.daisy, idorkw=self.duck1100.id)


#class TestSimplifiedAdministratorSimplifiedPeriod(TestCase, testhelper.Testhelper):
    #fixtures = ["simplified/data.json"]

    #def setUp(self):
        #self.grandma = User.objects.get(username='grandma') # superuser
        #self.duck1100_h01_core = models.Period.objects.get(parentnode__short_name='duck1100', 
                #short_name='spring01')
        #self.clarabelle = User.objects.get(username="clarabelle")
        #self.univ = models.Node.objects.get(short_name='univ')
        #self.duckburgh = models.Node.objects.get(short_name='duckburgh')
        #self.univ.admins.add(self.clarabelle)
        #self.duckburgh.admins.add(self.clarabelle)
        #self.daisy = User.objects.get(username="daisy")
        #self.assertEquals(0,
                #models.Node.where_is_admin_or_superadmin(self.daisy).count())

    #def test_read(self):
        #period = SimplifiedPeriod.read(self.clarabelle, self.duck1100_h01_core.id)
        #self.assertEquals(period, dict(
                #short_name = self.duck1100_h01_core.short_name,
                #long_name = self.duck1100_h01_core.long_name,
                #id = self.duck1100_h01_core.id,
                #parentnode__id = self.duck1100_h01_core.parentnode.id,
                #start_time = self.duck1100_h01_core.start_time,
                #end_time = self.duck1100_h01_core.end_time))

    #def test_read_security(self):
        #period = SimplifiedPeriod.read(self.grandma, self.duck1100_h01_core.id)
        #with self.assertRaises(PermissionDenied):
            #period = SimplifiedPeriod.read(self.daisy, self.duck1100_h01_core.id)

    #def test_insecure_read_model(self):
        #period = SimplifiedPeriod.insecure_read_model(self.clarabelle,
                #idorkw=self.duck1100_h01_core.id)
        #self.assertEquals(period.short_name, 'spring01')
        #period = SimplifiedPeriod.insecure_read_model(self.clarabelle,
                #dict(short_name=self.duck1100_h01_core.short_name,
                    #parentnode__short_name = 'duck1100'))
        #self.assertEquals(period.short_name, 'spring01')

    #def test_insecure_read_model_security(self):
        #period = SimplifiedPeriod.insecure_read_model(self.grandma, 
                #self.duck1100_h01_core.id) # superuser allowed
        #with self.assertRaises(PermissionDenied):
            #period = SimplifiedPeriod.insecure_read_model(self.daisy,
                    #self.duck1100_h01_core.id)


    #def test_create(self):
        #kw = dict(
                #long_name = 'Test',
                #parentnode = self.duck1100_h01_core.parentnode,
                #start_time = self.duck1100_h01_core.start_time,
                #end_time = self.duck1100_h01_core.end_time)
        #period = SimplifiedPeriod.create(self.clarabelle, short_name='test1', **kw)
        #self.assertEquals(period.short_name, 'test1')
        #self.assertEquals(period.long_name, 'Test')
        #self.assertEquals(period.start_time,
                #self.duck1100_h01_core.start_time)
        #self.assertEquals(period.end_time, 
                #self.duck1100_h01_core.end_time)
        #self.assertEquals(period.parentnode,
                #self.duck1100_h01_core.parentnode)
        
    #def test_create_security(self):
        #kw = dict(
                #long_name = 'Test',
                #parentnode = self.duck1100_h01_core.parentnode,
                #start_time = self.duck1100_h01_core.start_time,
                #end_time = self.duck1100_h01_core.end_time)

        #period = SimplifiedPeriod.create(self.grandma, short_name='test2', **kw) #superuser allowed
        #with self.assertRaises(PermissionDenied):
            #period = SimplifiedPeriod.create(self.daisy, short_name='test3', **kw)

    #def test_update(self):
        #self.assertEquals(self.duck1100_h01_core.short_name, 'spring01')
        
        #kw = dict(
                #short_name = 'test1',
                #long_name = 'Test',
                #parentnode = self.duck1100_h01_core.parentnode,
                #start_time = self.duck1100_h01_core.start_time,
                #end_time = self.duck1100_h01_core.end_time)
        #period = SimplifiedPeriod.update(self.clarabelle,
                #idorkw=self.duck1100_h01_core.id, **kw)
        #self.assertEquals(period.short_name, 'test1')
        #self.assertEquals(period.long_name, 'Test')
    
    #def test_update_security(self):
        #kw = dict(
                #short_name = 'test1',
                #long_name = 'Test',
                #parentnode = self.duck1100_h01_core.parentnode,
                #start_time = self.duck1100_h01_core.start_time,
                #end_time = self.duck1100_h01_core.end_time)
        #with self.assertRaises(PermissionDenied):
            #period = SimplifiedPeriod.update(self.daisy,
                    #idorkw=self.duck1100_h01_core.id, **kw)
        #period = SimplifiedPeriod.update(self.grandma,
                #idorkw=self.duck1100_h01_core.id, **kw) #superuser

    #def test_delete_asnodeadmin(self):
        #SimplifiedPeriod.delete(self.clarabelle, idorkw=self.duck1100_h01_core.id)
        #with self.assertRaises(models.Period.DoesNotExist):
            #period = models.Period.objects.get(id=self.duck1100_h01_core.id)

    #def test_delete_asnodeadmin_by_short_name(self):
        #SimplifiedPeriod.delete(self.clarabelle, dict(short_name='spring01',
            #parentnode__short_name='duck1100'))
        #with self.assertRaises(models.Period.DoesNotExist):
            #period = models.Period.objects.get(id=self.duck1100_h01_core.id)

    #def test_delete_assuperadmin(self):
        #SimplifiedPeriod.delete(self.grandma, idorkw=self.duck1100_h01_core.id)
        #with self.assertRaises(models.Period.DoesNotExist):
            #period = models.Period.objects.get(id=self.duck1100_h01_core.id)

    #def test_delete_noperm(self):
        #with self.assertRaises(PermissionDenied):
            #SimplifiedPeriod.delete(self.daisy, idorkw=self.duck1100_h01_core.id)

    #def test_search(self):
        #periods = models.Period.where_is_admin_or_superadmin(self.grandma).order_by("short_name")
        #qrywrap = SimplifiedPeriod.search(self.grandma)
        #self.assertEquals(len(qrywrap), len(periods))
        #self.assertEquals(qrywrap[0]['short_name'], periods[0].short_name)

        #qrywrap = SimplifiedPeriod.search(self.grandma, query="spring0")
        #self.assertEquals(len(qrywrap), 1)
        #qrywrap = SimplifiedPeriod.search(self.grandma, query="fall")
        #self.assertEquals(len(qrywrap), 2)
        #qrywrap = SimplifiedPeriod.search(self.grandma, query="01")
        #self.assertEquals(len(qrywrap), len(periods))
        #qrywrap = SimplifiedPeriod.search(self.grandma, query="1100")
        #self.assertEquals(len(qrywrap), 1)

    #def test_search_security(self):
        #qrywrap = SimplifiedPeriod.search(self.daisy, query="spring01")
        #self.assertEquals(len(qrywrap), 0)
        #self.duck1100_h01_core.admins.add(self.daisy)
        #qrywrap = SimplifiedPeriod.search(self.daisy, query="spring01")
        #self.assertEquals(len(qrywrap), 1)

class TestSimplifiedAssignment(SimplifiedAdminTestBase):

    def setUp(self):
        super(TestSimplifiedAssignment, self).setUp()

    def test_read_base(self):
        # do a read with no extra fields
        read_res = SimplifiedAssignment.read(self.admin1, self.inf101_firstSem_a1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1,
                                             SimplifiedAssignment.Meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)


    def test_read_period(self):
        # do a read with all extras
        read_res = SimplifiedAssignment.read(self.admin1,
                self.inf101_firstSem_a1.id, result_fieldgroups='period')
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1,
                                             SimplifiedAssignment.Meta.resultfields.aslist('period'))
        self.assertEquals(read_res, expected_res)

    def test_read_period_subject(self):
        read_res = SimplifiedAssignment.read(self.admin1,
                self.inf101_firstSem_a1.id, result_fieldgroups=['period',
                    'subject'])
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1,
                                             SimplifiedAssignment.Meta.resultfields.aslist(['period',
                                                 'subject']))
        self.assertEquals(read_res, expected_res)

    def test_read_period_subject_pointfields(self):
        read_res = SimplifiedAssignment.read(self.admin1,
                self.inf101_firstSem_a1.id, result_fieldgroups=['period',
                    'subject', 'pointfields'])
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1,
                                             SimplifiedAssignment.Meta.resultfields.aslist(['period',
                                                 'subject', 'pointfields']))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):
        self.add_to_path('uni;inf110.firstSem.a2.g1:candidate(testPerson)')

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.testPerson,
                    self.inf110_firstSem_a2.id)

        self.add_to_path('uni;inf110.firstSem.a2:admin(testPerson)')
        SimplifiedAssignment.read(self.testPerson, self.inf110_firstSem_a2.id)


    def test_insecure_read_model(self):
        read_res = SimplifiedAssignment.insecure_read_model(self.admin1, self.inf101_firstSem_a1.id)
        expected_res = self.inf101_firstSem_a1

        self.assertEquals(read_res, expected_res)

    def test_insecure_read_model_security(self):
        self.add_to_path('uni;inf110.firstSem.a2.g1:candidate(testPerson)')

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.insecure_read_model(self.testPerson,
                    self.inf110_firstSem_a2.id)

        self.add_to_path('uni;inf110.firstSem.a2:admin(testPerson)')
        SimplifiedAssignment.insecure_read_model(self.testPerson, self.inf110_firstSem_a2.id)

    def test_search(self):
        self.allExtras = SimplifiedAssignment.Meta.resultfields.additional_aslist()
        # search with no query and no extra fields
        search_res = SimplifiedAssignment.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstSem_a2, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondSem_a1, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondSem_a2, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_firstSem_a1, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_firstSem_a2, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a1, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a2, SimplifiedAssignment.Meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no querys, but all extra fields
        search_res = SimplifiedAssignment.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstSem_a2,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_secondSem_a1,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_secondSem_a2,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_firstSem_a1,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_firstSem_a2,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a1,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a2,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedAssignment.search(self.admin1, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondSem_a1,SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_firstSem_a1, SimplifiedAssignment.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a1, SimplifiedAssignment.Meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields, only subject containing '11' is 'inf110'.
        search_res = SimplifiedAssignment.search(self.admin1, query='11', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondSem_a1,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a2,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_firstSem_a1,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_firstSem_a2,
                                              SimplifiedAssignment.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res)) 
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_security(self):
        self.add_to_path('uni;inf110.firstSem.a2.g1:candidate(testPerson)')

        search_res = SimplifiedAssignment.search(self.testPerson)
        self.assertEquals(search_res.count(), 0)

        self.add_to_path('uni;inf110.firstSem.a2:admin(testPerson)')
        search_res = SimplifiedAssignment.search(self.testPerson)
        expected_res = [modelinstance_to_dict(self.inf110_firstSem_a2,
            SimplifiedAssignment.Meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_search_filters(self):
        qrywrap = SimplifiedAssignment.search(self.admin1,
                                              result_fieldgroups=['period'])
        self.assertEquals(len(qrywrap), 8)
        qrywrap = SimplifiedAssignment.search(self.admin1,
                                              result_fieldgroups=['period'],
                                              parentnode__short_name='firstSem')
        self.assertEquals(len(qrywrap), 4)

    def test_create(self):
        kw = dict(
                long_name = 'Test',
                parentnode = self.inf110_firstSem_a2.parentnode,
                publishing_time = self.inf110_firstSem_a2.publishing_time)

        self.create_res = SimplifiedAssignment.create(self.admin1, short_name='test1', **kw)
        self.assertEquals(self.create_res.short_name, 'test1')
        self.assertEquals(self.create_res.long_name, 'Test')
        self.assertEquals(self.create_res.parentnode,
                self.inf110_firstSem_a2.parentnode)
        self.assertEquals(self.create_res.publishing_time,
                self.inf110_firstSem_a2.publishing_time)

    def test_create_security(self):
        kw = dict(
                long_name = 'Test',
                parentnode = self.inf110_firstSem_a2.parentnode,
                publishing_time = self.inf110_firstSem_a2.publishing_time)

        #test that a student cannot create an assignment
        self.add_to_path('uni;inf110.firstSem.a2.g1:candidate(inf110Student)')
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
        self.assertEquals(self.inf110_firstSem_a2.short_name, 'a2')

        kw = dict(short_name = 'testa2',
                    long_name = 'Test',
                    parentnode = self.inf110_firstSem_a2.parentnode)

        update_res = SimplifiedAssignment.update(self.admin1, 
                            idorkw = self.inf110_firstSem_a2.id, 
                            **kw)

        self.assertEquals(update_res.short_name, 'testa2')
        self.assertEquals(self.inf110_firstSem_a2.short_name, 'a2')

        update_res = SimplifiedAssignment.update(self.admin1,
                                                 idorkw=self.inf110_firstSem_a2.id,
                                                 short_name = 'test110')
        self.refresh_var(self.inf110_firstSem_a2)
        self.assertEquals(self.inf110_firstSem_a2.short_name, 'test110')

    def test_update_security(self):
        kw = dict(
                long_name = 'TestAssignment',
                short_name = 'ta')

        #test that a student cannot change an assignment
        self.add_to_path('uni;inf110.firstSem.a2.g1:candidate(inf110Student)')
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.update(self.inf110Student, idorkw=self.inf110_firstSem_a2.id, **kw)

        #test that an administrator cannot change assignment for the wrong course
        self.add_to_path('uni;inf101:admin(inf101Admin)')
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.update(self.inf101Admin, idorkw=self.inf110_firstSem_a2.id, **kw)

        #test that a course-administrator can change assignments for his/her course..
        self.add_to_path('uni;inf110:admin(inf110Admin)')
        SimplifiedAssignment.update(self.inf110Admin, idorkw=self.inf110_firstSem_a2.id, **kw)

    def test_delete_asnodeadmin(self):
        self.add_to_path('uni;inf110.firstSem.a1:admin(testadmin)')
        SimplifiedAssignment.delete(self.testadmin, self.inf110_firstSem_a1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.delete(self.testadmin, self.inf110_firstSem_a1.id)

    def test_delete_asnodeadmin_by_short_name(self):
        self.add_to_path('uni;inf110.firstSem.a1:admin(testadmin)')
        SimplifiedAssignment.delete(self.testadmin, dict(short_name = 'a1',
            parentnode__short_name = 'firstSem',
            parentnode__parentnode__short_name = 'inf110'))

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.delete(self.testadmin, self.inf110_firstSem_a1.id)

    def test_delete_assuperadmin(self):
        SimplifiedAssignment.delete(self.admin1, self.inf110_firstSem_a1.id)

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.delete(self.admin1, self.inf110_firstSem_a1.id)

    def test_delete_noperm(self):
        self.add_to_path('uni;inf110.firstSem.a1.g1:candidate(testPerson)')

        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.delete(self.testPerson, self.inf110_firstSem_a1.id)


class TestSimplifiedAdminAssignmentGroup(SimplifiedAdminTestBase):

    allExtras = SimplifiedAssignmentGroup.Meta.resultfields.additional_aslist()
    baseFields = SimplifiedAssignmentGroup.Meta.resultfields.aslist()
    allFields = SimplifiedAssignmentGroup.Meta.resultfields.aslist(allExtras)

    def setUp(self):
        super(TestSimplifiedAdminAssignmentGroup, self).setUp()

    def test_search(self):
        # search with no query and no extra fields

        search_res = SimplifiedAssignmentGroup.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1, self.baseFields),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1, self.baseFields),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1, self.baseFields),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1, self.baseFields),
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2, self.baseFields),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2, self.baseFields),
                        ]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedAssignmentGroup.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1, self.allFields),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1, self.allFields),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1, self.allFields),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1, self.allFields),
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2, self.allFields),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2, self.allFields),
                        ]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedAssignmentGroup.search(self.admin1, query='secondStud')
        expected_res = [modelinstance_to_dict(self.inf101_secondSem_a1_g2, self.baseFields),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2, self.baseFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedAssignmentGroup.search(self.admin1, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1, self.allFields),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1, self.allFields),
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2, self.allFields),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2, self.allFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedAssignmentGroup.read(self.admin1, self.inf101_firstSem_a1_g1.id)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1_g1,
                                             SimplifiedAssignmentGroup.Meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedAssignmentGroup.read(self.admin1, self.inf101_firstSem_a1_g1.id, result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1_g1,
                                             SimplifiedAssignmentGroup.Meta.resultfields.aslist(self.allExtras))

        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for firstSem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignmentGroup.read(self.secondStud, self.inf101_firstSem_a1_g1.id)


class TestSimplifiedAdminstratorStaticFeedback(SimplifiedAdminTestBase):
    
    allExtras = SimplifiedStaticFeedback.Meta.resultfields.additional_aslist()
    
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
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist())]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedStaticFeedback.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedStaticFeedback.search(self.admin1, query='a1')
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist()),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist())]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedStaticFeedback.search(self.admin1, query='inf110', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf110_secondSem_a1_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist(self.allExtras)),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1_feedbacks[0],
                                              SimplifiedStaticFeedback.Meta.resultfields.aslist(self.allExtras))]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedStaticFeedback.read(self.admin1, self.inf101_firstSem_a1_g1_deliveries[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1_g1_feedbacks[0],
                                             SimplifiedStaticFeedback.Meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedStaticFeedback.read(self.admin1, self.inf101_firstSem_a1_g1_feedbacks[0].id,
                                           result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1_g1_feedbacks[0],
                                             SimplifiedStaticFeedback.Meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # test with someone who's not an admin
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.firstStud, self.inf101_firstSem_a1_g1_feedbacks[0].id)

        # test with someone who's not an admin
        with self.assertRaises(PermissionDenied):
            SimplifiedStaticFeedback.read(self.exam1, self.inf101_firstSem_a1_g1_feedbacks[0].id)


class TestSimplifiedAdminDeadline(SimplifiedAdminTestBase):

    allExtras = SimplifiedDeadline.Meta.resultfields.additional_aslist()
    baseFields = SimplifiedDeadline.Meta.resultfields.aslist()
    allFields = SimplifiedDeadline.Meta.resultfields.aslist(allExtras)

    def setUp(self):
        super(TestSimplifiedAdminDeadline, self).setUp()

    def test_search(self):
        # search with no query and no extra fields
        # should only have the deafault deadlines created when the
        # assignment group was created
        search_res = SimplifiedDeadline.search(self.admin1)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2.deadlines.all()[0], self.baseFields),
                        ]

        # assert that all search results are as expected
        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with no query and with extra fields
        search_res = SimplifiedDeadline.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2.deadlines.all()[0], self.allFields),
                        ]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # search with query
        search_res = SimplifiedDeadline.search(self.admin1, query='secondStud')
        expected_res = [modelinstance_to_dict(self.inf101_secondSem_a1_g2.deadlines.all()[0], self.baseFields),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2.deadlines.all()[0], self.baseFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # with query and extra fields
        search_res = SimplifiedDeadline.search(self.admin1, query='inf101', result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2.deadlines.all()[0], self.allFields)]

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

        # add some new deadlines, to simulate groups getting a second
        # chance
        self.add_to_path('uni;inf101.secondSem.a1.g2.deadline:ends(10):text(This is your last shot!)')

        search_res = SimplifiedDeadline.search(self.admin1, result_fieldgroups=self.allExtras)
        expected_res = [modelinstance_to_dict(self.inf101_firstSem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf101_firstSem_a2_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondSem_a1_g1.deadlines.all()[0], self.allFields),
                        modelinstance_to_dict(self.inf110_secondSem_a2_g1.deadlines.all()[0], self.allFields),
                        # this group now has 2 deadlines. make sure to include the old one here
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2.deadlines.order_by('deadline')[0], self.allFields),
                        # and the new one here
                        modelinstance_to_dict(self.inf101_secondSem_a1_g2_deadlines[0], self.allFields),
                        modelinstance_to_dict(self.inf101_secondSem_a2_g2.deadlines.all()[0], self.allFields),
                        ]

        print self.inf101_secondSem_a1_g2.deadlines.all()

        self.assertEquals(search_res.count(), len(expected_res))
        for s in search_res:
            self.assertTrue(s in expected_res)

    def test_read(self):

        # do a read with no extra fields
        read_res = SimplifiedDeadline.read(self.admin1, self.inf101_firstSem_a1_g1.deadlines.all()[0].id)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1_g1.deadlines.all()[0],
                                             SimplifiedDeadline.Meta.resultfields.aslist())
        self.assertEquals(read_res, expected_res)

        # do a read with all extras
        read_res = SimplifiedDeadline.read(self.admin1, self.inf101_firstSem_a1_g1.id.deadlines.all()[0], result_fieldgroups=self.allExtras)
        expected_res = modelinstance_to_dict(self.inf101_firstSem_a1_g1.deadlines.all()[0],
                                             SimplifiedDeadline.Meta.resultfields.aslist(self.allExtras))
        self.assertEquals(read_res, expected_res)

    def test_read_security(self):

        # We know secondStud hasn't signed up for firstSem.inf101.
        with self.assertRaises(PermissionDenied):
            SimplifiedDeadline.read(self.secondStud, self.inf101_firstSem_a1_g1.id)
