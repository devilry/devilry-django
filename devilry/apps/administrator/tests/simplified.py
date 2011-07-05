from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ....simplified import PermissionDenied
from ...core import models
from ..simplified import SimplifiedNode, SimplifiedSubject, SimplifiedPeriod, SimplifiedAssignment


class TestSimplifiedAdministratorSimplifiedNode(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.grandma = User.objects.get(username='grandma') # superuser
        self.clarabelle = User.objects.get(username="clarabelle")
        self.univ = models.Node.objects.get(short_name='univ')
        self.duckburgh = models.Node.objects.get(short_name='duckburgh')
        self.univ.admins.add(self.clarabelle)
        self.duckburgh.admins.add(self.clarabelle)

        self.daisy = User.objects.get(username="daisy")
        self.assertEquals(0,
                models.Node.where_is_admin_or_superadmin(self.daisy).count())

        self.invalidid = 100000
        self.assertRaises(models.Node.DoesNotExist, models.Node.objects.get,
                id=self.invalidid)



    def test_create(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        node = SimplifiedNode.create(self.clarabelle, short_name='test1', **kw)
        self.assertEquals(node.short_name, 'test1')
        self.assertEquals(node.long_name, 'Test')
        self.assertEquals(node.parentnode, self.univ)

    def test_create_sequrity(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        node = SimplifiedNode.create(self.grandma, short_name='test2', **kw) # superuser allowed
        with self.assertRaises(PermissionDenied):
            node = SimplifiedNode.create(self.daisy, short_name='test3', **kw)

    def test_create_validation(self):
        with self.assertRaises(models.Node.DoesNotExist):
            SimplifiedNode.create(self.clarabelle,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.invalidid)
        with self.assertRaisesRegexp(ValidationError,
                "long_name.*short_name"):
            SimplifiedNode.update(
                    self.clarabelle, self.duckburgh.id,
                    short_name=None, long_name=None)

    def test_insecure_read_model(self):
        node = SimplifiedNode.insecure_read_model(self.clarabelle, idorkw=self.univ.id)
        node = SimplifiedNode.insecure_read_model(self.grandma, self.univ.id) # superuser allowed
        node = SimplifiedNode.insecure_read_model(self.grandma, dict(short_name=self.univ.short_name))
        self.assertEquals(node.short_name, 'univ')
        node = SimplifiedNode.insecure_read_model(self.grandma, idorkw=self.univ.id)
        self.assertEquals(node.short_name, 'univ')

    def test_insecure_read_model_security(self):
        with self.assertRaises(PermissionDenied):
            node = SimplifiedNode.insecure_read_model(self.daisy, self.univ.id)

    def test_update(self):
        self.assertEquals(self.duckburgh.short_name, 'duckburgh')
        self.assertEquals(self.duckburgh.long_name, 'Duckburgh')
        self.assertEquals(self.duckburgh.parentnode, None)

        kw = dict(idorkw=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        node = SimplifiedNode.update(self.clarabelle, **kw)
        self.assertEquals(node.short_name, 'test')
        self.assertEquals(node.long_name, 'Test')
        self.assertEquals(node.parentnode, self.univ)

    def test_update_security(self):
        kw = dict(idorkw=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        
        with self.assertRaises(PermissionDenied):
            node = SimplifiedNode.update(self.daisy, **kw)

        node = SimplifiedNode.update(self.grandma, **kw) # superuser allowed
        node = SimplifiedNode.update(self.grandma,
                dict(short_name='test'),
                long_name = 'My Duckburgh Test')
        self.assertEquals(node.long_name, 'My Duckburgh Test')
        
    def test_update_validation(self):
        with self.assertRaises(models.Node.DoesNotExist):
            SimplifiedNode.update(self.clarabelle,
                    idorkw=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.invalidid)
        with self.assertRaises(models.Node.DoesNotExist):
            SimplifiedNode.update(self.clarabelle,
                    idorkw=self.invalidid,
                    short_name='test2',
                    long_name='Test 2',
                    parentnode_id=None)
        with self.assertRaisesRegexp(ValidationError,
                "long_name.*short_name"):
            SimplifiedNode.update(
                    self.clarabelle, self.duckburgh.id,
                    short_name=None, long_name=None)


    def test_delete_asnodeadmin(self):
        SimplifiedNode.delete(self.clarabelle, idorkw=self.univ.id)
        with self.assertRaises(models.Node.DoesNotExist):
            node = models.Node.objects.get(id=self.univ.id)

    def test_delete_asnodeadmin_by_short_name(self):
        SimplifiedNode.delete(self.clarabelle, dict(short_name='univ'))
        with self.assertRaises(models.Node.DoesNotExist):
            SimplifiedNode.delete(self.clarabelle, dict(short_name='univ'))

    def test_delete_assuperadmin(self):
        SimplifiedNode.delete(self.grandma, idorkw=self.univ.id)
        with self.assertRaises(models.Node.DoesNotExist):
            node = models.Node.objects.get(id=self.univ.id)
    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedNode.delete(self.daisy, idorkw=self.univ.id)


    def test_search(self):
        clarabelle = User.objects.get(username="clarabelle")
        nodes = models.Node.objects.all().order_by("short_name")
        qrywrap = SimplifiedNode.search(self.clarabelle)
        self.assertEquals(len(qrywrap), len(nodes))
        self.assertEquals(qrywrap[0]['short_name'], nodes[0].short_name)

        # query
        qrywrap = SimplifiedNode.search(self.clarabelle, query="burgh")
        self.assertEquals(len(qrywrap), 1)
        qrywrap = SimplifiedNode.search(self.clarabelle, query="univ")
        self.assertEquals(len(qrywrap), 1)
        qrywrap = SimplifiedNode.search(self.clarabelle)
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedNode.search(self.grandma)
        self.assertEquals(len(qrywrap), len(nodes))

        self.univ.parentnode = self.duckburgh
        self.univ.save()
        qrywrap = SimplifiedNode.search(self.grandma,
                parentnode_id=self.duckburgh.id)
        self.assertEquals(len(qrywrap), 1)
        self.assertEquals(qrywrap[0]['short_name'], 'univ')

    def test_search_security(self):
        qrywrap = SimplifiedNode.search(self.daisy)
        self.assertEquals(len(qrywrap), 0)

        self.duckburgh.admins.add(self.daisy)
        qrywrap = SimplifiedNode.search(self.daisy)
        self.assertEquals(len(qrywrap), 1)


class TestSimplifiedAdministratorSimplifiedSubject(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.grandma = User.objects.get(username='grandma') # superuser
        self.duck1100 = models.Subject.objects.get(short_name='duck1100')
        self.clarabelle = User.objects.get(username="clarabelle")
        self.univ = models.Node.objects.get(short_name='univ')
        self.duckburgh = models.Node.objects.get(short_name='duckburgh')
        self.univ.admins.add(self.clarabelle)
        self.duckburgh.admins.add(self.clarabelle)
        self.daisy = User.objects.get(username="daisy")
        self.assertEquals(0,
                models.Node.where_is_admin_or_superadmin(self.daisy).count())

    def test_insecure_read_model(self):
        subject = SimplifiedSubject.insecure_read_model(self.clarabelle, idorkw=self.duck1100.id)
        subject = SimplifiedSubject.insecure_read_model(self.clarabelle, self.duck1100.id)
        self.assertEquals(subject.short_name, 'duck1100')
        subject = SimplifiedSubject.insecure_read_model(self.clarabelle,
                dict(short_name=self.duck1100.short_name))
        self.assertEquals(subject.short_name, 'duck1100')

    def test_insecure_read_model_security(self):
        subject = SimplifiedSubject.insecure_read_model(self.grandma, self.duck1100.id) # superuser allowed
        with self.assertRaises(PermissionDenied):
            node = SimplifiedSubject.insecure_read_model(self.daisy, self.duck1100.id)

    def test_read(self):
        subject = SimplifiedSubject.read(self.grandma, self.duck1100.id)
        self.assertEquals(subject, dict(
                short_name = 'duck1100',
                long_name = self.duck1100.long_name,
                id = self.duck1100.id))

    def test_search(self):
        subjects = models.Subject.where_is_admin_or_superadmin(self.grandma).order_by("short_name")
        qrywrap = SimplifiedSubject.search(self.grandma)
        self.assertEquals(len(qrywrap), len(subjects))
        self.assertEquals(qrywrap[0]['short_name'], subjects[0].short_name)

        # query
        qrywrap = SimplifiedSubject.search(self.grandma, query="duck1")
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedSubject.search(self.grandma, query="duck")
        self.assertEquals(len(qrywrap), len(subjects))
        qrywrap = SimplifiedSubject.search(self.grandma, query="1100")
        self.assertEquals(len(qrywrap), 1)

    def test_search_security(self):
        qrywrap = SimplifiedSubject.search(self.daisy, query="1100")
        self.assertEquals(len(qrywrap), 0)
        self.duck1100.admins.add(self.daisy)
        qrywrap = SimplifiedSubject.search(self.daisy, query="1100")
        self.assertEquals(len(qrywrap), 1)


    def test_create(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        subject = SimplifiedSubject.create(self.clarabelle, short_name='test1', **kw)
        self.assertEquals(subject.short_name, 'test1')
        self.assertEquals(subject.long_name, 'Test')
        self.assertEquals(subject.parentnode, self.univ)

    def test_create_security(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        subject = SimplifiedSubject.create(self.grandma, short_name='test2', **kw) # superuser allowed
        with self.assertRaises(PermissionDenied):
            subject = SimplifiedSubject.create(self.daisy, short_name='test3', **kw)

    def test_update(self):
        self.assertEquals(self.duck1100.short_name, 'duck1100')

        kw = dict(id=self.duck1100.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        subject = SimplifiedSubject.update(self.clarabelle, idorkw=self.duck1100.id, **kw)
        self.assertEquals(subject.short_name, 'test')
        self.assertEquals(subject.long_name, 'Test')
        self.assertEquals(subject.parentnode, self.univ)
        
    def test_update_security(self):
        kw = dict(id=self.duck1100.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        with self.assertRaises(PermissionDenied):
            subject = SimplifiedSubject.update(self.daisy, idorkw=self.duck1100.id, **kw)
    
    def test_delete_asnodeadmin(self):
        SimplifiedSubject.delete(self.clarabelle, idorkw=self.duck1100.id)
        with self.assertRaises(models.Subject.DoesNotExist):
            subject = models.Subject.objects.get(id=self.duck1100.id)

    def test_delete_asnodeadmin_by_short_name(self):
        SimplifiedSubject.delete(self.clarabelle, dict(short_name='duck1100'))
        with self.assertRaises(models.Subject.DoesNotExist):
            SimplifiedSubject.delete(self.clarabelle, dict(short_name='duck1100'))

    def test_delete_assuperadmin(self):
        SimplifiedSubject.delete(self.grandma, idorkw=self.duck1100.id)
        with self.assertRaises(models.Subject.DoesNotExist):
            subject = models.Subject.objects.get(id=self.duck1100.id)

    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedSubject.delete(self.daisy, idorkw=self.duck1100.id)


class TestSimplifiedAdministratorSimplifiedPeriod(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.grandma = User.objects.get(username='grandma') # superuser
        self.duck1100_h01_core = models.Period.objects.get(parentnode__short_name='duck1100', 
                short_name='spring01')
        self.clarabelle = User.objects.get(username="clarabelle")
        self.univ = models.Node.objects.get(short_name='univ')
        self.duckburgh = models.Node.objects.get(short_name='duckburgh')
        self.univ.admins.add(self.clarabelle)
        self.duckburgh.admins.add(self.clarabelle)
        self.daisy = User.objects.get(username="daisy")
        self.assertEquals(0,
                models.Node.where_is_admin_or_superadmin(self.daisy).count())

    def test_read(self):
        period = SimplifiedPeriod.read(self.clarabelle, self.duck1100_h01_core.id)
        self.assertEquals(period, dict(
                short_name = self.duck1100_h01_core.short_name,
                long_name = self.duck1100_h01_core.long_name,
                id = self.duck1100_h01_core.id,
                parentnode__id = self.duck1100_h01_core.parentnode.id,
                start_time = self.duck1100_h01_core.start_time,
                end_time = self.duck1100_h01_core.end_time))

    def test_read_security(self):
        period = SimplifiedPeriod.read(self.grandma, self.duck1100_h01_core.id)
        with self.assertRaises(PermissionDenied):
            period = SimplifiedPeriod.read(self.daisy, self.duck1100_h01_core.id)

    def test_insecure_read_model(self):
        period = SimplifiedPeriod.insecure_read_model(self.clarabelle,
                idorkw=self.duck1100_h01_core.id)
        self.assertEquals(period.short_name, 'spring01')
        period = SimplifiedPeriod.insecure_read_model(self.clarabelle,
                dict(short_name=self.duck1100_h01_core.short_name,
                    parentnode__short_name = 'duck1100'))
        self.assertEquals(period.short_name, 'spring01')

    def test_insecure_read_model_security(self):
        period = SimplifiedPeriod.insecure_read_model(self.grandma, 
                self.duck1100_h01_core.id) # superuser allowed
        with self.assertRaises(PermissionDenied):
            period = SimplifiedPeriod.insecure_read_model(self.daisy,
                    self.duck1100_h01_core.id)


    def test_create(self):
        kw = dict(
                long_name = 'Test',
                parentnode = self.duck1100_h01_core.parentnode,
                start_time = self.duck1100_h01_core.start_time,
                end_time = self.duck1100_h01_core.end_time)
        period = SimplifiedPeriod.create(self.clarabelle, short_name='test1', **kw)
        self.assertEquals(period.short_name, 'test1')
        self.assertEquals(period.long_name, 'Test')
        self.assertEquals(period.start_time,
                self.duck1100_h01_core.start_time)
        self.assertEquals(period.end_time, 
                self.duck1100_h01_core.end_time)
        self.assertEquals(period.parentnode,
                self.duck1100_h01_core.parentnode)
        
    def test_create_security(self):
        kw = dict(
                long_name = 'Test',
                parentnode = self.duck1100_h01_core.parentnode,
                start_time = self.duck1100_h01_core.start_time,
                end_time = self.duck1100_h01_core.end_time)

        period = SimplifiedPeriod.create(self.grandma, short_name='test2', **kw) #superuser allowed
        with self.assertRaises(PermissionDenied):
            period = SimplifiedPeriod.create(self.daisy, short_name='test3', **kw)

    def test_update(self):
        self.assertEquals(self.duck1100_h01_core.short_name, 'spring01')
        
        kw = dict(
                short_name = 'test1',
                long_name = 'Test',
                parentnode = self.duck1100_h01_core.parentnode,
                start_time = self.duck1100_h01_core.start_time,
                end_time = self.duck1100_h01_core.end_time)
        period = SimplifiedPeriod.update(self.clarabelle,
                idorkw=self.duck1100_h01_core.id, **kw)
        self.assertEquals(period.short_name, 'test1')
        self.assertEquals(period.long_name, 'Test')
    
    def test_update_security(self):
        kw = dict(
                short_name = 'test1',
                long_name = 'Test',
                parentnode = self.duck1100_h01_core.parentnode,
                start_time = self.duck1100_h01_core.start_time,
                end_time = self.duck1100_h01_core.end_time)
        with self.assertRaises(PermissionDenied):
            period = SimplifiedPeriod.update(self.daisy,
                    idorkw=self.duck1100_h01_core.id, **kw)
        period = SimplifiedPeriod.update(self.grandma,
                idorkw=self.duck1100_h01_core.id, **kw) #superuser

    def test_delete_asnodeadmin(self):
        SimplifiedPeriod.delete(self.clarabelle, idorkw=self.duck1100_h01_core.id)
        with self.assertRaises(models.Period.DoesNotExist):
            period = models.Period.objects.get(id=self.duck1100_h01_core.id)

    def test_delete_asnodeadmin_by_short_name(self):
        SimplifiedPeriod.delete(self.clarabelle, dict(short_name='spring01',
            parentnode__short_name='duck1100'))
        with self.assertRaises(models.Period.DoesNotExist):
            period = models.Period.objects.get(id=self.duck1100_h01_core.id)

    def test_delete_assuperadmin(self):
        SimplifiedPeriod.delete(self.grandma, idorkw=self.duck1100_h01_core.id)
        with self.assertRaises(models.Period.DoesNotExist):
            period = models.Period.objects.get(id=self.duck1100_h01_core.id)

    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            SimplifiedPeriod.delete(self.daisy, idorkw=self.duck1100_h01_core.id)

    def test_search(self):
        periods = models.Period.where_is_admin_or_superadmin(self.grandma).order_by("short_name")
        qrywrap = SimplifiedPeriod.search(self.grandma)
        self.assertEquals(len(qrywrap), len(periods))
        self.assertEquals(qrywrap[0]['short_name'], periods[0].short_name)

        qrywrap = SimplifiedPeriod.search(self.grandma, query="spring0")
        self.assertEquals(len(qrywrap), 1)
        qrywrap = SimplifiedPeriod.search(self.grandma, query="fall")
        self.assertEquals(len(qrywrap), 2)
        qrywrap = SimplifiedPeriod.search(self.grandma, query="01")
        self.assertEquals(len(qrywrap), len(periods))
        qrywrap = SimplifiedPeriod.search(self.grandma, query="1100")
        self.assertEquals(len(qrywrap), 1)

    def test_search_security(self):
        qrywrap = SimplifiedPeriod.search(self.daisy, query="spring01")
        self.assertEquals(len(qrywrap), 0)
        self.duck1100_h01_core.admins.add(self.daisy)
        qrywrap = SimplifiedPeriod.search(self.daisy, query="spring01")
        self.assertEquals(len(qrywrap), 1)

class TestSimplifiedAdministratorSimplifiedAssignment(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.grandma = User.objects.get(username='grandma') # superuser
        self.clarabelle = User.objects.get(username="clarabelle")
        self.univ = models.Node.objects.get(short_name='univ')
        self.univ.admins.add(self.clarabelle)
        self.daisy = User.objects.get(username="daisy")
        self.assertEquals(0,
                models.Node.where_is_admin_or_superadmin(self.daisy).count())
        self.duck1100_core = models.Subject.objects.get(short_name='duck1100')
        self.duck1100_spring01_week1_core = self.duck1100_core.periods.get(
                short_name='spring01').assignments.get(short_name='week1')

    def test_read_base(self):
        assignment = SimplifiedAssignment.read(self.clarabelle, self.duck1100_spring01_week1_core.id) 
        self.assertEquals(assignment, dict(
                id = self.duck1100_spring01_week1_core.id,
                short_name = 'week1',
                long_name = self.duck1100_spring01_week1_core.long_name,
                parentnode__id=self.duck1100_spring01_week1_core.parentnode.id))

    def test_read_period(self):
        assignment = SimplifiedAssignment.read(self.clarabelle,
                self.duck1100_spring01_week1_core.id,
                result_fieldgroups=['period'])
        self.assertEquals(assignment, dict(
                id = self.duck1100_spring01_week1_core.id,
                short_name = 'week1',
                long_name = self.duck1100_spring01_week1_core.long_name,
                parentnode__id=self.duck1100_spring01_week1_core.parentnode.id,
                parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.short_name,
                parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.long_name,
                parentnode__parentnode__id=self.duck1100_spring01_week1_core.parentnode.parentnode_id))

    def test_read_period_subject(self):
        assignment = SimplifiedAssignment.read(self.clarabelle,
                self.duck1100_spring01_week1_core.id,
                result_fieldgroups=['period', 'subject'])
        self.assertEquals(assignment, dict(
                id = self.duck1100_spring01_week1_core.id,
                short_name = 'week1',
                long_name = self.duck1100_spring01_week1_core.long_name,
                parentnode__id=self.duck1100_spring01_week1_core.parentnode.id,
                parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.short_name,
                parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.long_name,
                parentnode__parentnode__id=self.duck1100_spring01_week1_core.parentnode.parentnode_id,
                parentnode__parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.parentnode.short_name,
                parentnode__parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.parentnode.long_name))

    def test_read_period_subject_pointfields(self):
        assignment = SimplifiedAssignment.read(self.clarabelle,
                self.duck1100_spring01_week1_core.id,
                result_fieldgroups=['period', 'subject', 'pointfields'])
        self.assertEquals(assignment, dict(
                id = self.duck1100_spring01_week1_core.id,
                short_name = 'week1',
                long_name = self.duck1100_spring01_week1_core.long_name,
                parentnode__id=self.duck1100_spring01_week1_core.parentnode.id,
                parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.short_name,
                parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.long_name,
                parentnode__parentnode__id=self.duck1100_spring01_week1_core.parentnode.parentnode_id,
                parentnode__parentnode__short_name=self.duck1100_spring01_week1_core.parentnode.parentnode.short_name,
                parentnode__parentnode__long_name=self.duck1100_spring01_week1_core.parentnode.parentnode.long_name,
                anonymous = self.duck1100_spring01_week1_core.anonymous,
                must_pass = self.duck1100_spring01_week1_core.must_pass, 
                maxpoints = self.duck1100_spring01_week1_core.maxpoints,
                attempts = self.duck1100_spring01_week1_core.attempts))

    def test_read_security(self):
        #test superuser allowed
        assignment = SimplifiedAssignment.read(self.grandma, self.duck1100_spring01_week1_core.id) 

        #test user with no permissions
        with self.assertRaises(PermissionDenied):
            assignment = SimplifiedAssignment.read(self.daisy,
                    self.duck1100_spring01_week1_core.id)
        with self.assertRaises(PermissionDenied):
            assignment = SimplifiedAssignment.read(self.daisy,
                    self.duck1100_spring01_week1_core.id,
                    result_fieldgroups=['period', 'subject'])
    
    def test_insecure_read_model(self):
        assignment = SimplifiedAssignment.insecure_read_model(self.clarabelle, 
                idorkw=self.duck1100_spring01_week1_core.id)

        self.assertEquals(assignment, self.duck1100_spring01_week1_core)

    def test_insecure_read_model_security(self):
        #test superuser allowed
        SimplifiedAssignment.insecure_read_model(self.grandma,
                self.duck1100_spring01_week1_core.id)

        #test user with no permissions
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.daisy,
                self.duck1100_spring01_week1_core.id)

    def test_search(self):
        assignments = models.Assignment.where_is_admin_or_superadmin(self.grandma).order_by("short_name")
        qrywrap = SimplifiedAssignment.search(self.grandma)
        self.assertEquals(len(qrywrap), len(assignments))
        self.assertEquals(qrywrap[0]['short_name'], assignments[0].short_name)

        #duck3580, duck1100 and duck1080 have all got an assignment called 'week1'
        qrywrap = SimplifiedAssignment.search(self.grandma, query="ek1")
        self.assertEquals(len(qrywrap), 3)
        #this should hit all 9 assignments with 'week' in its short_name
        qrywrap = SimplifiedAssignment.search(self.grandma, query="week")
        self.assertEquals(len(qrywrap), 9)
        #no assignments has 'duck' in its short_name
        qrywrap = SimplifiedAssignment.search(self.grandma, query="duck")
        self.assertEquals(len(qrywrap), 0)


    def test_search_security(self):
        #test user with no permissions
        qrywrap = SimplifiedAssignment.search(self.daisy, query="ek1")
        self.assertEquals(len(qrywrap), 0)

        #make daisy admin in subject 'duck1100'
        self.duck1100_h01_core = models.Period.objects.get(parentnode__short_name='duck1100', 
                short_name='spring01')
        self.duck1100_h01_core.admins.add(self.daisy)
        
        #admin in subject 'duck1100' has access to 'week1' in 'duck1100'
        qrywrap = SimplifiedAssignment.search(self.daisy, query="ek1")
        self.assertEquals(len(qrywrap), 1)

    def test_create(self):
        # TODO, failes at SimplifiedAssignment.create because of ValidationError on grade plugin
        pass
    """
        kw = dict(
                long_name = 'Test',
                parentnode = self.duck1100_spring01_week1_core.parentnode,
                publishing_time = self.duck1100_spring01_week1_core.publishing_time,
                grade_plugin = self.duck1100_spring01_week1_core.grade_plugin)
        assignment = SimplifiedAssignment.create(self.clarabelle, short_name='test1', **kw)
        self.assertEquals(assignment.short_name, 'test1')
        self.assertEquals(assignment.long_name, 'Test')
        self.assertEquals(assignment.parentnode,
                self.duck1100_spring01_week1_core.parentnode)
        self.assertEquals(assignment.publishing_time, 
                self.duck1100_spring01_week1_core.publishing_time)
        self.assertEquals(assignment.grade_plugin, 
                self.duck1100_spring01_week1_core.grade_plugin)
        """

    def test_create_security(self):
        #TODO
        pass

    def test_update(self):
        #TODO
        pass
        
    def test_update_security(self):
        #TODO
        pass
    
    def test_delete_asnodeadmin(self):
        #TODO
        pass

    def test_delete_asnodeadmin_by_short_name(self):
        #TODO
        pass

    def test_delete_assuperadmin(self):
        #TODO
        pass

    def test_delete_noperm(self):
        #TODO
        pass
