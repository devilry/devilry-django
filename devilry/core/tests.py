"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from datetime import datetime, timedelta
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from devilry.addons.grade_approved.models import ApprovedGrade
from devilry.core import pluginloader

from models import (Node, Subject, Period, Assignment, AssignmentGroup,
        Delivery, Candidate, Feedback)
from deliverystore import (MemoryDeliveryStore, FsDeliveryStore,
    DbmDeliveryStore)
from testhelpers import TestDeliveryStoreMixin, create_from_path

pluginloader.autodiscover()


class TestBaseNode(TestCase):
    fixtures = ['tests/core/users.json', 'tests/core/core.json']

    def setUp(self):
        self.thesuperuser= User.objects.get(username='thesuperuser')
        self.uioadmin = User.objects.get(username='uioadmin')
        self.uioadmin = User.objects.get(username='uioadmin')
        self.ifiadmin = User.objects.get(username='ifiadmin')
        self.uio = Node.objects.get(pk=1)
        self.ifi = Node.objects.get(pk=2)

    def test_is_admin(self):
        self.assertTrue(self.uio.is_admin(self.uioadmin))
        self.assertFalse(self.uio.is_admin(self.ifiadmin))
        self.assertTrue(self.ifi.is_admin(self.uioadmin))
        self.assertTrue(self.ifi.is_admin(self.ifiadmin))

    def test_get_admins(self):
        def split_and_sort(admins):
            l = admins.split(', ')
            l.sort()
            return ', '.join(l)
        self.assertEquals(self.uio.get_admins(), 'uioadmin')
        self.assertEquals(split_and_sort(self.ifi.get_admins()),
                'ifiadmin, ifitechsupport')

    def test_can_save(self):
        self.assertTrue(self.uio.can_save(self.uioadmin))
        self.assertFalse(self.uio.can_save(self.ifiadmin))
        self.assertTrue(self.ifi.can_save(self.ifiadmin))
        self.assertTrue(self.ifi.can_save(self.uioadmin))
        self.assertTrue(Node().can_save(self.thesuperuser))

    def test_can_save_id_none(self):
        deepdummy1 = Node.objects.get(pk=4)
        self.assertTrue(Subject(parentnode=deepdummy1).can_save(self.uioadmin))
        self.assertFalse(Subject(parentnode=deepdummy1).can_save(self.ifiadmin))



class TestNode(TestCase):
    fixtures = ['tests/core/users.json', 'tests/core/core.json']

    def setUp(self):
        self.uioadmin = User.objects.get(username='uioadmin')
        self.ifiadmin = User.objects.get(username='ifiadmin')
        self.uio = Node.objects.get(pk=1)
        self.ifi = Node.objects.get(pk=2)
        self.deepdummy1 = Node.objects.get(pk=4)
        self.deepdummy3 = Node.objects.get(pk=6)

    def test_unique(self):
        n = Node(parentnode=self.deepdummy1, short_name='ifi', long_name='Ifi')
        n.save()
        n.parentnode = self.uio
        self.assertRaises(IntegrityError, n.save)

    def test_can_save(self):
        self.assertFalse(Node().can_save(self.ifiadmin))

    def test_short_name_validation(self):
        self.uio.short_name = '1'
        self.uio.full_clean()
        self.uio.short_name = '_'
        self.uio.full_clean()
        self.uio.short_name = '-'
        self.uio.full_clean()
        self.uio.short_name = 'u'
        self.uio.full_clean()
        self.uio.short_name = 'u-i_o--0'
        self.uio.full_clean()
        self.uio.short_name = 'L'
        self.assertRaises(ValidationError, self.uio.full_clean)

    def test_unicode(self):
        self.assertEquals(unicode(self.deepdummy3),
                'uio.deepdummy1.deepdummy2.deepdummy3')

    def test_get_path(self):
        self.assertEquals(self.uio.get_path(), 'uio')
        self.assertEquals(self.ifi.get_path(), 'uio.ifi')
        self.assertEquals(self.deepdummy3.get_path(),
                'uio.deepdummy1.deepdummy2.deepdummy3')

    def test_iter_childnodes(self):
        self.assertEquals(
                [n.short_name for n in self.deepdummy1.iter_childnodes()],
                [u'deepdummy2', u'deepdummy3'])

        s = set([n.short_name for n in self.uio.iter_childnodes()])
        self.assertEquals(s,
                set([u'deepdummy1', u'deepdummy2', u'deepdummy3', u'fys', u'ifi']))

    def test_clean_parent_is_child(self):
        """ Can not be child of it's own child. """
        self.uio.parentnode = self.ifi
        self.assertRaises(ValidationError, self.uio.clean)

    def test_clean_parent_is_self(self):
        """ Can not be child of itself. """
        self.uio.parentnode = self.uio
        self.assertRaises(ValidationError, self.uio.clean)

    def test_clean_noerrors(self):
        self.ifi.clean()

    def test_create_multiple_roots(self):
        n = Node(short_name='test', long_name='Test', parentnode=None)
        n.clean()
        n.save()
        n2 = Node(short_name='test2', long_name='Test2', parentnode=None)
        n2.clean()
        n2.save()

    def test_where_is_admin(self):
        self.assertEquals(Node.where_is_admin(self.uioadmin).count(), 6)
        self.assertEquals(Node.where_is_admin(self.ifiadmin).count(), 1)

    def test_get_pathlist_kw(self):
        expected = {
                'short_name': 'deepdummy3',
                'parentnode__short_name': 'deepdummy2',
                'parentnode__parentnode__short_name': 'deepdummy1',
                'parentnode__parentnode__parentnode__short_name': 'uio'
                }
        self.assertEquals(expected,
                Node.get_by_path_kw(
                    ['uio', 'deepdummy1', 'deepdummy2', 'deepdummy3']))

    def test_get_by_path(self):
        self.assertEquals(
                Node.get_by_path('uio.deepdummy1.deepdummy2').short_name,
                'deepdummy2')
        self.assertRaises(Node.DoesNotExist, Node.get_by_path,
                'uio.deepdummy1.nonode')
        self.assertRaises(Node.DoesNotExist, Node.get_by_path,
                'does.not.exist')

    def test_get_nodepks_where_isadmin(self):
        uioadmin = User.objects.get(username='uioadmin')
        pks = Node._get_nodepks_where_isadmin(uioadmin)
        self.assertEquals(set(pks), set([1,2,3,4,5,6]))



class TestSubject(TestCase):
    fixtures = ['tests/core/users.json', 'tests/core/core.json']

    def test_unique(self):
        s = Subject(parentnode=Node.objects.get(short_name='ifi'),
                short_name='inf1060', long_name='INF1060')
        self.assertRaises(IntegrityError, s.save)

    def test_unique2(self):
        s = Subject(parentnode=Node.objects.get(short_name='uio'),
                short_name='inf1060', long_name='INF1060')
        self.assertRaises(IntegrityError, s.save)

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(Subject.where_is_admin(teacher1).count(), 1)
        self.assertEquals(Subject.where_is_admin(uioadmin).count(), 2)

    def test_get_path(self):
        inf1100 = Subject.objects.get(id=1)
        self.assertEquals(inf1100.get_path(), 'inf1100')

    def test_get_full_path(self):
        inf1100 = Subject.objects.get(id=1)
        self.assertEquals(inf1100.get_full_path(), 'uio.ifi.inf1100')

    def test_get_by_path(self):
        self.assertEquals(Subject.get_by_path('inf1100').short_name,
                'inf1100')
        self.assertRaises(Subject.DoesNotExist, Subject.get_by_path,
                'doesnotexist')


class TestPeriod(TestCase):
    fixtures = ['tests/core/users.json', 'tests/core/core.json']

    def test_unique(self):
        n = Period(parentnode=Subject.objects.get(short_name='inf1100'),
                short_name='old', long_name='Old',
                start_time=datetime.now(),
                end_time=datetime.now())
        self.assertRaises(IntegrityError, n.save)

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(Period.where_is_admin(uioadmin).count(), 2)

    def test_clean(self):
        p = Period.objects.get(id=1)
        p.start_time = datetime(2010, 1, 1)
        p.end_time = datetime(2011, 1, 1)
        p.clean()
        p.start_time = datetime(2012, 1, 1)
        self.assertRaises(ValidationError, p.clean)

    def test_get_by_path(self):
        self.assertEquals(Period.get_by_path('inf1100.old').short_name,
                'old')
        self.assertRaises(Period.DoesNotExist, Period.get_by_path,
                'does.notexist')
        self.assertRaises(ValueError, Period.get_by_path,
                'does.not.exist')


class TestAssignment(TestCase):
    fixtures = ['tests/core/users.json', 'tests/core/core.json']

    def test_unique(self):
        n = Assignment(parentnode=Period.objects.get(short_name='looong'),
                short_name='oblig1', long_name='O1',
                publishing_time=datetime.now())
        self.assertRaises(IntegrityError, n.save)

    def test_where_is_admin(self):
        ifiadmin = User.objects.get(username='ifiadmin')
        self.assertEquals(Assignment.where_is_admin(ifiadmin).count(), 3)

    def test_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        q = Assignment.where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oblig1')
        ag = AssignmentGroup.objects.get(pk=4)
        ag.examiners.add(examiner1)
        ag.save()
        q = Assignment.where_is_examiner(examiner1)
        self.assertEquals(q.count(), 2)

    def test_published_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        q = Assignment.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oblig1')

        ag = AssignmentGroup.objects.get(pk=4)
        ag.examiners.add(examiner1)
        ag.save()
        q = Assignment.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 2)

        ag.parentnode.publishing_time = datetime.now() + timedelta(10)
        ag.parentnode.save()
        q = Assignment.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)

    def test_active_where_is_examiner(self):
        future = datetime.now() + timedelta(10)
        examiner1 = User.objects.get(username='examiner1')
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oblig1')

        ag = AssignmentGroup.objects.get(pk=4)
        ag.examiners.add(examiner1)
        ag.save()
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        ag.parentnode.parentnode.end_time = future
        ag.parentnode.parentnode.save()
        self.assertEquals(q.count(), 2)

        ag.parentnode.publishing_time = future
        ag.parentnode.save()
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)

    def test_old_where_is_examiner(self):
        past = datetime.now() - timedelta(10)
        examiner3 = User.objects.get(username='examiner3')
        q = Assignment.old_where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oldone')

        ag = AssignmentGroup.objects.get(pk=1)
        ag.examiners.add(examiner3)
        ag.save()
        q = Assignment.old_where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        ag.parentnode.parentnode.end_time = past
        ag.parentnode.parentnode.save()
        self.assertEquals(q.count(), 2)


    def test_assignmentgroups_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(3,
                oblig1.assignment_groups_where_is_examiner(examiner2)[0].id)
        self.assertEquals(2,
                oblig1.assignment_groups_where_is_examiner(examiner1).count())

    def test_assignmentgroups_where_is_examiner_or_admin(self):
        examiner1 = User.objects.get(username='examiner1')
        ifiadmin = User.objects.get(username='ifiadmin')

        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(1,
                oblig1.assignment_groups_where_is_examiner_or_admin(examiner1)[0].id)
        self.assertEquals(2,
                oblig1.assignment_groups_where_is_examiner_or_admin(examiner1).count())

        self.assertEquals(1,
                oblig1.assignment_groups_where_is_examiner_or_admin(ifiadmin)[0].id)
        self.assertEquals(4,
                oblig1.assignment_groups_where_is_examiner_or_admin(ifiadmin).count())

    def test_clean_publishing_time_before(self):
        oblig1 = Assignment.objects.get(id=1)
        oblig1.parentnode.start_time = datetime(2010, 1, 1)
        oblig1.parentnode.end_time = datetime(2011, 1, 1)
        oblig1.publishing_time = datetime(2010, 1, 2)
        oblig1.clean()
        oblig1.publishing_time = datetime(2009, 1, 1)
        self.assertRaises(ValidationError, oblig1.clean)

    def test_clean_publishing_time_after(self):
        oblig1 = Assignment.objects.get(id=1)
        oblig1.parentnode.start_time = datetime(2010, 1, 1)
        oblig1.parentnode.end_time = datetime(2011, 1, 1)
        oblig1.publishing_time = datetime(2010, 1, 2)
        oblig1.clean()
        oblig1.publishing_time = datetime(2012, 1, 1)
        self.assertRaises(ValidationError, oblig1.clean)
        
    def test_get_path(self):
        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(oblig1.get_path(), 'inf1100.looong.oblig1')

    def test_get_full_path(self):
        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(oblig1.get_full_path(),
                'uio.ifi.inf1100.looong.oblig1')

    def test_get_by_path(self):
        self.assertEquals(
                Assignment.get_by_path('inf1100.looong.oblig1').short_name,
                'oblig1')
        self.assertRaises(Assignment.DoesNotExist, Assignment.get_by_path,
                'does.not.exist')
        self.assertRaises(ValueError, Assignment.get_by_path, 'does.not')


class TestAssignmentGroup(TestCase):
    fixtures = ['tests/core/users.json', 'tests/core/core.json']

    def test_where_is_admin(self):
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(5, AssignmentGroup.where_is_admin(teacher1).count())

    def test_where_is_candidate(self):
        student2 = User.objects.get(username='student2')
        student1 = User.objects.get(username='student1')
        self.assertEquals(1, AssignmentGroup.where_is_candidate(student2).count())
        self.assertEquals(3, AssignmentGroup.where_is_candidate(student1).count())

    def test_published_where_is_candidate(self):
        student2 = User.objects.get(username='student2')
        student3 = User.objects.get(username='student3')
        self.assertEquals(1,
                AssignmentGroup.published_where_is_candidate(student2).count())
        self.assertEquals(2,
                AssignmentGroup.published_where_is_candidate(student3).count())

    def test_active_where_is_candidate(self):
        student2 = User.objects.get(username='student2')
        student3 = User.objects.get(username='student3')
        self.assertEquals(1,
                AssignmentGroup.active_where_is_candidate(student2).count())
        self.assertEquals(2,
                AssignmentGroup.active_where_is_candidate(student3).count())

    def test_old_where_is_candidate(self):
        student1 = User.objects.get(username='student1')
        student4 = User.objects.get(username='student4')
        self.assertEquals(2,
                AssignmentGroup.old_where_is_candidate(student1).count())
        self.assertEquals(1,
                AssignmentGroup.old_where_is_candidate(student4).count())


    def test_where_is_examiner(self):
        examiner2 = User.objects.get(username='examiner2')
        examiner4 = User.objects.get(username='examiner4')
        self.assertEquals(1,
                AssignmentGroup.where_is_examiner(examiner2).count())
        self.assertEquals(2,
                AssignmentGroup.where_is_examiner(examiner4).count())

    def test_published_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        self.assertEquals(1,
                AssignmentGroup.published_where_is_examiner(examiner2).count())
        self.assertEquals(2,
                AssignmentGroup.published_where_is_examiner(examiner1).count())

    def test_active_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        self.assertEquals(1,
                AssignmentGroup.active_where_is_examiner(examiner2).count())
        self.assertEquals(2,
                AssignmentGroup.active_where_is_examiner(examiner1).count())

    def test_old_where_is_examiner(self):
        examiner3 = User.objects.get(username='examiner3')
        examiner4 = User.objects.get(username='examiner4')
        self.assertEquals(1,
                AssignmentGroup.old_where_is_examiner(examiner4).count())
        self.assertEquals(2,
                AssignmentGroup.old_where_is_examiner(examiner3).count())

    def test_get_students(self):
        g = AssignmentGroup.objects.get(id=5)
        self.assertEquals('student1, student4', g.get_students())

    def test_get_candidates(self):
        g = AssignmentGroup.objects.get(id=5)
        self.assertEquals('student1, student4', g.get_candidates())
        a = Assignment.objects.get(id=3)
        a.anonymous = True
        a.save()
        g = AssignmentGroup.objects.get(id=5)
        self.assertEquals('1, 4', g.get_candidates())

    def test_get_examiners(self):
        a = AssignmentGroup.objects.get(id=5)
        self.assertEquals('examiner3, examiner4', a.get_examiners())

    def test_is_admin(self):
        teacher1 = User.objects.get(username='teacher1')
        student1 = User.objects.get(username='student1')
        uioadmin = User.objects.get(username='uioadmin')
        a = AssignmentGroup.objects.get(id=1)
        self.assertTrue(a.is_admin(teacher1))
        self.assertFalse(a.is_admin(student1))
        self.assertTrue(a.is_admin(uioadmin))

    def test_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        a = AssignmentGroup.objects.get(id=1)
        self.assertTrue(a.is_examiner(examiner1))
        self.assertFalse(a.is_examiner(examiner2))

    def test_is_candidate(self):
        student1 = User.objects.get(username='student1')
        student2 = User.objects.get(username='student2')
        a = AssignmentGroup.objects.get(id=1)
        self.assertTrue(a.is_candidate(student1))
        self.assertFalse(a.is_candidate(student2))

    def test_clean_deadline_after_endtime(self):
        assignment_group = AssignmentGroup.objects.get(id=1)
        oblig1 = assignment_group.parentnode
        oblig1.parentnode.start_time = datetime(2010, 1, 1)
        oblig1.parentnode.end_time = datetime(2011, 1, 1)
        oblig1.publishing_time = datetime(2010, 1, 2)
        deadline = assignment_group.deadlines.create(deadline=datetime(2010, 5, 5), text=None)
        deadline.clean()
        deadline = assignment_group.deadlines.create(deadline=datetime(2012, 1, 1), text=None)
        self.assertRaises(ValidationError, deadline.clean)

    def test_clean_deadline_before_publishing_time(self):
        assignment_group = AssignmentGroup.objects.get(id=1)
        oblig1 = assignment_group.parentnode
        oblig1.publishing_time = datetime(2011, 12, 24)
        deadline = assignment_group.deadlines.create(deadline=datetime(2012, 1, 1), text=None)
        deadline.clean()
        oblig1.publishing_time = datetime(2012, 12, 24)
        deadline = assignment_group.deadlines.create(deadline=datetime(2011, 12, 24), text=None)
        self.assertRaises(ValidationError, deadline.clean)

    def test_status(self):
        teacher1 = User.objects.get(username='teacher1')
        ag = AssignmentGroup(
                parentnode = Assignment.objects.get(id=1))
        ag.save()
        self.assertEquals(ag.status,
                AssignmentGroup.NO_DELIVERIES)
        self.assertEquals(ag.get_status_string(),
                "No deliveries")
        self.assertEquals(ag.get_student_status_string(),
                "No deliveries")

        ag = AssignmentGroup.objects.get(id=1)
        d = ag.deliveries.all()[0]
        d.save()
        self.assertEquals(ag.status,
                AssignmentGroup.NOT_CORRECTED)
        self.assertEquals(ag.get_status_string(),
                "Not corrected")
        self.assertEquals(ag.get_student_status_string(),
                "Not corrected")

        d.feedback = Feedback(
                format = 'rst',
                text = 'test',
                last_modified_by = teacher1)
        d.feedback.set_grade_from_xmlrpcstring("+")
        d.feedback.save()
        d.save()
        ag = AssignmentGroup.objects.get(id=1)
        self.assertEquals(ag.status,
                AssignmentGroup.CORRECTED_NOT_PUBLISHED)
        self.assertEquals(ag.get_status_string(),
                "Corrected, not published")
        self.assertEquals(ag.get_student_status_string(),
                "Not corrected")

        d.feedback.published = True
        d.feedback.save()
        ag = AssignmentGroup.objects.get(id=1)
        self.assertEquals(ag.status,
                AssignmentGroup.CORRECTED_AND_PUBLISHED)
        self.assertEquals(ag.get_status_string(),
                "Corrected and published")
        self.assertEquals(ag.get_student_status_string(),
                "Corrected")


        
class TestCandidate(TestCase):
    fixtures = ['tests/core/users.json', 'tests/core/core.json']
    
    def test_non_anonymous(self):
        assignmentgroup1 = AssignmentGroup.objects.get(id=1)
        student1_candidate = Candidate.objects.get(id=1)
        self.assertEquals(student1_candidate.get_identifier(), "student1")
        
    def test_anonymous(self):
        oblig1 = Assignment.objects.get(id=1)
        # Set anonymous
        oblig1.anonymous = True
        oblig1.save()
        student1_candidate = Candidate.objects.get(id=1)
        self.assertEquals(student1_candidate.get_identifier(), "1")
        

class TestDelivery(TestCase):
    fixtures = ['tests/core/users.json', 'tests/core/core.json']

    def test_where_is_admin(self):
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(Delivery.where_is_admin(teacher1).count(), 3)

    def test_delivery(self):
        student1 = User.objects.get(username='student1')
        assignmentgroup = AssignmentGroup.objects.get(id=1)
        d = Delivery.begin(assignmentgroup, student1)
        self.assertEquals(d.assignment_group, assignmentgroup)
        self.assertFalse(d.successful)
        d.finish()
        self.assertEquals(d.assignment_group, assignmentgroup)
        self.assertTrue(d.successful)
        self.assertEquals(d.number, 3)

        d2 = Delivery.begin(assignmentgroup, student1)
        d2.finish()
        self.assertTrue(d2.successful)
        self.assertEquals(d2.number, 4)
        d2.save()

        # TODO find a graceful way to handle this error:
        d2.number = 3
        self.assertRaises(IntegrityError, d2.save)

    def test_feedback_delete(self):
        student1 = User.objects.get(username='student1')
        examiner1 = User.objects.get(username='examiner1')
        assignmentgroup = AssignmentGroup.objects.get(id=1)
        d = Delivery.begin(assignmentgroup, student1)
        d.finish()
        self.assertEquals(ApprovedGrade.objects.all().count(), 0)
        feedback = d.get_feedback()
        feedback.set_grade_from_xmlrpcstring('+')
        feedback.last_modified_by = examiner1
        feedback.save()
        self.assertEquals(ApprovedGrade.objects.all().count(), 1)
        feedback.delete()
        self.assertEquals(ApprovedGrade.objects.all().count(), 0)
        


# TODO: Feedback tests

class TestMemoryDeliveryStore(TestDeliveryStoreMixin, TestCase):
    def get_storageobj(self):
        return MemoryDeliveryStore()


class TestFsDeliveryStore(TestDeliveryStoreMixin, TestCase):
    def setUp(self):
        self.root = mkdtemp()
        super(TestFsDeliveryStore, self).setUp()

    def get_storageobj(self):
        return FsDeliveryStore(self.root)

    def tearDown(self):
        rmtree(self.root)

class TestDbmDeliveryStore(TestDeliveryStoreMixin, TestCase):
    def setUp(self):
        self.root = mkdtemp()
        super(TestDbmDeliveryStore, self).setUp()

    def get_storageobj(self):
        return DbmDeliveryStore(join(self.root, 'test.dbm'))

    def tearDown(self):
        rmtree(self.root)


class TestTestHelpers(TestCase):
    def test_create_from_path(self):

        self.assertEquals(create_from_path('uio').short_name, 'uio')
        self.assertEquals(create_from_path('test.node').short_name, 'node')
        subject = create_from_path('uio:inf1010')
        self.assertEquals(subject.short_name, 'inf1010')
        self.assertTrue(isinstance(subject, Subject))
        period = create_from_path('uio:inf1010.spring11') 
        self.assertEquals(period.short_name, 'spring11')
        self.assertTrue(isinstance(period, Period))
        assignment = create_from_path('uio:inf1010.spring11.oblig1')
        self.assertEquals(assignment.short_name, 'oblig1')
        self.assertTrue(isinstance(assignment, Assignment))

        self.assertRaises(User.DoesNotExist,
                User.objects.get, username='student1')
        ag = create_from_path(
                'ifi:inf1100.spring10.oblig1.student1')
        students = [c.student.username for c in ag.candidates.all()]
        self.assertEquals(students, ['student1'])
        User.objects.get(username='student1')
        self.assertEquals(ag.parentnode.short_name, 'oblig1')
        self.assertEquals(ag.parentnode.parentnode.short_name, 'spring10')
        self.assertEquals(ag.parentnode.parentnode.parentnode.short_name,
                'inf1100')
        self.assertEquals(
                ag.parentnode.parentnode.parentnode.parentnode.short_name,
                'ifi')

        ag1 = create_from_path(
                'ifi:inf1100.spring10.oblig1.student1,student2')
        ag2 = create_from_path(
                'ifi:inf1100.spring10.oblig1.student1,student2')
        self.assertNotEquals(ag1.id, ag2.id)
