from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ....simplified import PermissionDenied
from ...core import models
from ..simplified import Node, Subject, Period, Assignment


class TestSimplifiedAdministratorNode(TestCase):
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
        node = Node.create(self.clarabelle, short_name='test1', **kw)
        self.assertEquals(node.short_name, 'test1')
        self.assertEquals(node.long_name, 'Test')
        self.assertEquals(node.parentnode, self.univ)

    def test_create_sequrity(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        node = Node.create(self.grandma, short_name='test2', **kw) # superuser allowed
        with self.assertRaises(PermissionDenied):
            node = Node.create(self.daisy, short_name='test3', **kw)

    def test_create_validation(self):
        with self.assertRaises(models.Node.DoesNotExist):
            Node.create(self.clarabelle,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.invalidid)
        with self.assertRaisesRegexp(ValidationError,
                "long_name.*short_name"):
            Node.update(
                    self.clarabelle, self.duckburgh.id,
                    short_name=None, long_name=None)

    def test_read_model(self):
        node = Node.read_model(self.clarabelle, idorkw=self.univ.id)
        node = Node.read_model(self.grandma, self.univ.id) # superuser allowed
        node = Node.read_model(self.grandma, dict(short_name=self.univ.short_name))
        self.assertEquals(node.short_name, 'univ')
        node = Node.read_model(self.grandma, idorkw=self.univ.id)
        self.assertEquals(node.short_name, 'univ')

    def test_read_model_security(self):
        with self.assertRaises(PermissionDenied):
            node = Node.read_model(self.daisy, self.univ.id)

    def test_update(self):
        self.assertEquals(self.duckburgh.short_name, 'duckburgh')
        self.assertEquals(self.duckburgh.long_name, 'Duckburgh')
        self.assertEquals(self.duckburgh.parentnode, None)

        kw = dict(idorkw=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        node = Node.update(self.clarabelle, **kw)
        self.assertEquals(node.short_name, 'test')
        self.assertEquals(node.long_name, 'Test')
        self.assertEquals(node.parentnode, self.univ)

    def test_update_security(self):
        kw = dict(idorkw=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        
        with self.assertRaises(PermissionDenied):
            node = Node.update(self.daisy, **kw)

        node = Node.update(self.grandma, **kw) # superuser allowed
        node = Node.update(self.grandma,
                dict(short_name='test'),
                long_name = 'My Duckburgh Test')
        self.assertEquals(node.long_name, 'My Duckburgh Test')
        
    def test_update_validation(self):
        with self.assertRaises(models.Node.DoesNotExist):
            Node.update(self.clarabelle,
                    idorkw=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.invalidid)
        with self.assertRaises(models.Node.DoesNotExist):
            Node.update(self.clarabelle,
                    idorkw=self.invalidid,
                    short_name='test2',
                    long_name='Test 2',
                    parentnode_id=None)
        with self.assertRaisesRegexp(ValidationError,
                "long_name.*short_name"):
            Node.update(
                    self.clarabelle, self.duckburgh.id,
                    short_name=None, long_name=None)


    def test_delete_asnodeadmin(self):
        Node.delete(self.clarabelle, idorkw=self.univ.id)
        with self.assertRaises(models.Node.DoesNotExist):
            node = models.Node.objects.get(id=self.univ.id)

    def test_delete_asnodeadmin_by_short_name(self):
        Node.delete(self.clarabelle, dict(short_name='univ'))
        with self.assertRaises(models.Node.DoesNotExist):
            Node.delete(self.clarabelle, dict(short_name='univ'))

    def test_delete_assuperadmin(self):
        Node.delete(self.grandma, idorkw=self.univ.id)
        with self.assertRaises(models.Node.DoesNotExist):
            node = models.Node.objects.get(id=self.univ.id)
    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            Node.delete(self.daisy, idorkw=self.univ.id)


    def test_search(self):
        clarabelle = User.objects.get(username="clarabelle")
        nodes = models.Node.objects.all().order_by("short_name")
        qrywrap = Node.search(self.clarabelle)
        self.assertEquals(len(qrywrap), len(nodes))
        self.assertEquals(qrywrap[0]['short_name'], nodes[0].short_name)

        # query
        qrywrap = Node.search(self.clarabelle, query="burgh")
        self.assertEquals(len(qrywrap), 1)
        qrywrap = Node.search(self.clarabelle, query="univ")
        self.assertEquals(len(qrywrap), 1)
        qrywrap = Node.search(self.clarabelle)
        self.assertEquals(len(qrywrap), 2)
        qrywrap = Node.search(self.grandma)
        self.assertEquals(len(qrywrap), len(nodes))

        self.univ.parentnode = self.duckburgh
        self.univ.save()
        qrywrap = Node.search(self.grandma,
                parentnode_id=self.duckburgh.id)
        self.assertEquals(len(qrywrap), 1)
        self.assertEquals(qrywrap[0]['short_name'], 'univ')

    def test_search_security(self):
        qrywrap = Node.search(self.daisy)
        self.assertEquals(len(qrywrap), 0)

        self.duckburgh.admins.add(self.daisy)
        qrywrap = Node.search(self.daisy)
        self.assertEquals(len(qrywrap), 1)


class TestSimplifiedAdministratorSubject(TestCase):
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

    def test_read_model(self):
        subject = Subject.read_model(self.clarabelle, idorkw=self.duck1100.id)
        subject = Subject.read_model(self.clarabelle, self.duck1100.id)
        self.assertEquals(subject.short_name, 'duck1100')
        subject = Subject.read_model(self.clarabelle,
                dict(short_name=self.duck1100.short_name))
        self.assertEquals(subject.short_name, 'duck1100')

    def test_read_model_security(self):
        subject = Subject.read_model(self.grandma, self.duck1100.id) # superuser allowed
        with self.assertRaises(PermissionDenied):
            node = Subject.read_model(self.daisy, self.duck1100.id)

    def test_read(self):
        subject = Subject.read(self.grandma, self.duck1100.id)
        self.assertEquals(subject, dict(
                short_name = 'duck1100',
                long_name = self.duck1100.long_name,
                id = self.duck1100.id))

    def test_search(self):
        subjects = models.Subject.where_is_admin_or_superadmin(self.grandma).order_by("short_name")
        qrywrap = Subject.search(self.grandma)
        self.assertEquals(len(qrywrap), len(subjects))
        self.assertEquals(qrywrap[0]['short_name'], subjects[0].short_name)

        # query
        qrywrap = Subject.search(self.grandma, query="duck1")
        self.assertEquals(len(qrywrap), 2)
        qrywrap = Subject.search(self.grandma, query="duck")
        self.assertEquals(len(qrywrap), len(subjects))
        qrywrap = Subject.search(self.grandma, query="1100")
        self.assertEquals(len(qrywrap), 1)

    def test_search_security(self):
        qrywrap = Subject.search(self.daisy, query="1100")
        self.assertEquals(len(qrywrap), 0)
        self.duck1100.admins.add(self.daisy)
        qrywrap = Subject.search(self.daisy, query="1100")
        self.assertEquals(len(qrywrap), 1)


    def test_create(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        subject = Subject.create(self.clarabelle, short_name='test1', **kw)
        self.assertEquals(subject.short_name, 'test1')
        self.assertEquals(subject.long_name, 'Test')
        self.assertEquals(subject.parentnode, self.univ)

    def test_create_security(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        subject = Subject.create(self.grandma, short_name='test2', **kw) # superuser allowed
        with self.assertRaises(PermissionDenied):
            subject = Subject.create(self.daisy, short_name='test3', **kw)

    def test_update(self):
        self.assertEquals(self.duck1100.short_name, 'duck1100')

        kw = dict(id=self.duck1100.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        subject = Subject.update(self.clarabelle, idorkw=self.duck1100.id, **kw)
        self.assertEquals(subject.short_name, 'test')
        self.assertEquals(subject.long_name, 'Test')
        self.assertEquals(subject.parentnode, self.univ)
        
    def test_update_security(self):
        kw = dict(id=self.duck1100.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        with self.assertRaises(PermissionDenied):
            subject = Subject.update(self.daisy, idorkw=self.duck1100.id, **kw)
    
    def test_delete_asnodeadmin(self):
        Subject.delete(self.clarabelle, idorkw=self.duck1100.id)
        with self.assertRaises(models.Subject.DoesNotExist):
            subject = models.Subject.objects.get(id=self.duck1100.id)

    def test_delete_asnodeadmin_by_short_name(self):
        Subject.delete(self.clarabelle, dict(short_name='duck1100'))
        with self.assertRaises(models.Subject.DoesNotExist):
            Subject.delete(self.clarabelle, dict(short_name='duck1100'))

    def test_delete_assuperadmin(self):
        Subject.delete(self.grandma, idorkw=self.duck1100.id)
        with self.assertRaises(models.Subject.DoesNotExist):
            subject = models.Subject.objects.get(id=self.duck1100.id)

    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            Subject.delete(self.daisy, idorkw=self.duck1100.id)


class TestSimplifiedAdministratorPeriod(TestCase):
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
        period = Period.read(self.clarabelle, self.duck1100_h01_core.id)
        self.assertEquals(period, dict(
                short_name = self.duck1100_h01_core.short_name,
                long_name = self.duck1100_h01_core.long_name,
                id = self.duck1100_h01_core.id,
                parentnode__id = self.duck1100_h01_core.parentnode.id,
                start_time = self.duck1100_h01_core.start_time,
                end_time = self.duck1100_h01_core.end_time))

    def test_read_security(self):
        period = Period.read(self.grandma, self.duck1100_h01_core.id)
        with self.assertRaises(PermissionDenied):
            period = Period.read(self.daisy, self.duck1100_h01_core.id)

    def test_read_model(self):
        period = Period.read_model(self.clarabelle,
                idorkw=self.duck1100_h01_core.id)
        self.assertEquals(period.short_name, 'spring01')
        period = Period.read_model(self.clarabelle,
                dict(short_name=self.duck1100_h01_core.short_name,
                    parentnode__short_name = 'duck1100'))
        self.assertEquals(period.short_name, 'spring01')

    def test_read_model_security(self):
        period = Period.read_model(self.grandma, 
                self.duck1100_h01_core.id) # superuser allowed
        with self.assertRaises(PermissionDenied):
            period = Period.read_model(self.daisy,
                    self.duck1100_h01_core.id)


    def test_create(self):
        kw = dict(
                long_name = 'Test',
                parentnode = self.duck1100_h01_core.parentnode,
                start_time = self.duck1100_h01_core.start_time,
                end_time = self.duck1100_h01_core.end_time)
        period = Period.create(self.clarabelle, short_name='test1', **kw)
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

        period = Period.create(self.grandma, short_name='test2', **kw) #superuser allowed
        with self.assertRaises(PermissionDenied):
            period = Period.create(self.daisy, short_name='test3', **kw)

    def test_update(self):
        self.assertEquals(self.duck1100_h01_core.short_name, 'spring01')
        
        kw = dict(
                short_name = 'test1',
                long_name = 'Test',
                parentnode = self.duck1100_h01_core.parentnode,
                start_time = self.duck1100_h01_core.start_time,
                end_time = self.duck1100_h01_core.end_time)
        period = Period.update(self.clarabelle,
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
            period = Period.update(self.daisy,
                    idorkw=self.duck1100_h01_core.id, **kw)
        period = Period.update(self.grandma,
                idorkw=self.duck1100_h01_core.id, **kw) #superuser

    def test_delete_asnodeadmin(self):
        Period.delete(self.clarabelle, idorkw=self.duck1100_h01_core.id)
        with self.assertRaises(models.Period.DoesNotExist):
            period = models.Period.objects.get(id=self.duck1100_h01_core.id)

    def test_delete_asnodeadmin_by_short_name(self):
        Period.delete(self.clarabelle, dict(short_name='spring01',
            parentnode__short_name='duck1100'))
        with self.assertRaises(models.Period.DoesNotExist):
            period = models.Period.objects.get(id=self.duck1100_h01_core.id)

    def test_delete_assuperadmin(self):
        Period.delete(self.grandma, idorkw=self.duck1100_h01_core.id)
        with self.assertRaises(models.Period.DoesNotExist):
            period = models.Period.objects.get(id=self.duck1100_h01_core.id)

    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            Period.delete(self.daisy, idorkw=self.duck1100_h01_core.id)

    def test_search(self):
        periods = models.Period.where_is_admin_or_superadmin(self.grandma).order_by("short_name")
        qrywrap = Period.search(self.grandma)
        self.assertEquals(len(qrywrap), len(periods))
        self.assertEquals(qrywrap[0]['short_name'], periods[0].short_name)

        qrywrap = Period.search(self.grandma, query="spring0")
        self.assertEquals(len(qrywrap), 1)
        qrywrap = Period.search(self.grandma, query="fall")
        self.assertEquals(len(qrywrap), 2)
        qrywrap = Period.search(self.grandma, query="01")
        self.assertEquals(len(qrywrap), len(periods))
        qrywrap = Period.search(self.grandma, query="1100")
        self.assertEquals(len(qrywrap), 1)

    def test_search_security(self):
        qrywrap = Period.search(self.daisy, query="spring01")
        self.assertEquals(len(qrywrap), 0)
        self.duck1100_h01_core.admins.add(self.daisy)
        qrywrap = Period.search(self.daisy, query="spring01")
        self.assertEquals(len(qrywrap), 1)

class TestSimplifiedAdministratorAssignment(TestCase):
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
        assignment = Assignment.read(self.clarabelle, self.duck1100_spring01_week1_core.id) 
        self.assertEquals(assignment, dict(
                id = self.duck1100_spring01_week1_core.id,
                short_name = 'week1',
                long_name = self.duck1100_spring01_week1_core.long_name,
                parentnode__id=self.duck1100_spring01_week1_core.parentnode.id))

    def test_read_period(self):
        assignment = Assignment.read(self.clarabelle,
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
        assignment = Assignment.read(self.clarabelle,
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
        assignment = Assignment.read(self.clarabelle,
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
        assignment = Assignment.read(self.grandma, self.duck1100_spring01_week1_core.id) 

        #test user with no permissions
        with self.assertRaises(PermissionDenied):
            assignment = Assignment.read(self.daisy,
                    self.duck1100_spring01_week1_core.id)
        with self.assertRaises(PermissionDenied):
            assignment = Assignment.read(self.daisy,
                    self.duck1100_spring01_week1_core.id,
                    result_fieldgroups=['period', 'subject'])
    
    def test_read_model(self):
        assignment = Assignment.read_model(self.clarabelle, 
                idorkw=self.duck1100_spring01_week1_core.id)

        self.assertEquals(assignment, self.duck1100_spring01_week1_core)

    def test_read_model_security(self):
        #test superuser allowed
        Assignment.read_model(self.grandma,
                self.duck1100_spring01_week1_core.id)

        #test user with no permissions
        with self.assertRaises(PermissionDenied):
            Assignment.read(self.daisy,
                self.duck1100_spring01_week1_core.id)

    def test_search(self):
        assignments = models.Assignment.where_is_admin_or_superadmin(self.grandma).order_by("short_name")
        qrywrap = Assignment.search(self.grandma)
        self.assertEquals(len(qrywrap), len(assignments))
        self.assertEquals(qrywrap[0]['short_name'], assignments[0].short_name)

        #duck3580, duck1100 and duck1080 have all got an assignment called 'week1'
        qrywrap = Assignment.search(self.grandma, query="ek1")
        self.assertEquals(len(qrywrap), 3)
        #this should hit all 9 assignments with 'week' in its short_name
        qrywrap = Assignment.search(self.grandma, query="week")
        self.assertEquals(len(qrywrap), 9)
        #no assignments has 'duck' in its short_name
        qrywrap = Assignment.search(self.grandma, query="duck")
        self.assertEquals(len(qrywrap), 0)


    def test_search_security(self):
        #test user with no permissions
        qrywrap = Assignment.search(self.daisy, query="ek1")
        self.assertEquals(len(qrywrap), 0)

        #make daisy admin in subject 'duck1100'
        self.duck1100_h01_core = models.Period.objects.get(parentnode__short_name='duck1100', 
                short_name='spring01')
        self.duck1100_h01_core.admins.add(self.daisy)
        
        #admin in subject 'duck1100' has access to 'week1' in 'duck1100'
        qrywrap = Assignment.search(self.daisy, query="ek1")
        self.assertEquals(len(qrywrap), 1)

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
