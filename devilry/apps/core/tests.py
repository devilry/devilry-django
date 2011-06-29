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

from models import (Node, Subject, Period, Assignment, AssignmentGroup,
        Delivery, Candidate, Feedback, FileMeta, Deadline)
from deliverystore import (MemoryDeliveryStore, FsDeliveryStore,
    DbmDeliveryStore)
from testhelpers import TestDeliveryStoreMixin, create_from_path
import pluginloader

pluginloader.autodiscover()
FileMeta.deliverystore = MemoryDeliveryStore()


class TestBaseNode(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

    def setUp(self):
        self.thesuperuser= User.objects.get(username='thesuperuser')
        self.uio = Node.objects.get(short_name='uio', parentnode=None)
        self.ifi = Node.objects.get(short_name='ifi', parentnode=self.uio)
        self.uioadmin = User.objects.get(username='uioadmin') # admin on the uio node
        self.ifiadmin = User.objects.get(username='ifiadmin') # admin on the ifi node

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
        self.assertFalse(Node(parentnode=None).can_save(self.uioadmin))
        self.assertTrue(Node(parentnode=self.uio).can_save(self.uioadmin))
        self.assertFalse(Node(parentnode=self.uio).can_save(self.ifiadmin))

    def test_can_save_id_none(self):
        deepdummy1 = Node.objects.get(pk=4)
        self.assertTrue(Subject(parentnode=deepdummy1).can_save(self.uioadmin))
        self.assertFalse(Subject(parentnode=deepdummy1).can_save(self.ifiadmin))



class TestNode(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

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

    def test_unique_noneparent(self):
        n = Node(parentnode=None, short_name='stuff', long_name='Ifi')
        n.clean()
        n.save()
        n2 = Node(parentnode=None, short_name='stuff', long_name='Ifi')
        self.assertRaises(ValidationError, n2.clean)

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
    fixtures = ['core/deprecated_users.json', 'core/core.json']

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

    def test_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        q = Subject.where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'inf1100')

        ag = create_from_path(
                'ifi:inf1010.spring10.oblig1.student1')
        ag.examiners.add(examiner1)
        ag.save()
        q = Subject.where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 2)
        self.assertEquals(q[0].short_name, 'inf1010')
        self.assertEquals(q[1].short_name, 'inf1100')

    def test_published_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        q = Subject.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'inf1100')

        ag = create_from_path(
                'ifi:inf1010.spring10.oblig1.student1')
        ag.examiners.add(examiner1)
        ag.save()
        q = Subject.published_where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 2)
        self.assertEquals(q[0].short_name, 'inf1010')
        self.assertEquals(q[1].short_name, 'inf1100')

        assignment1010 = ag.parentnode
        assignment1010.publishing_time = datetime.now() + timedelta(10)
        assignment1010.save()
        q = Subject.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)


class TestPeriod(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

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

    def test_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        q = Period.where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'looong')

        ag = create_from_path(
                'ifi:inf1010.spring10.oblig1.student1')
        ag.examiners.add(examiner1)
        ag.save()
        q = Period.where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 2)
        self.assertEquals(q[0].short_name, 'looong')
        self.assertEquals(q[1].short_name, 'spring10')

    def test_published_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        ag = create_from_path(
                'ifi:inf1010.spring10.oblig1.student1')
        ag.examiners.add(examiner1)
        ag.save()
        q = Period.where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 2)

        assignment1010 = ag.parentnode
        assignment1010.publishing_time = datetime.now() + timedelta(10)
        assignment1010.save()
        q = Period.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)


class TestAssignment(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

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

        q = Assignment.published_where_is_examiner(examiner1, old=False,
                active=False)
        self.assertEquals(q.count(), 0)

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
                oblig1.assignment_groups_where_can_examine(examiner1)[0].id)
        self.assertEquals(2,
                oblig1.assignment_groups_where_can_examine(examiner1).count())

        self.assertEquals(1,
                oblig1.assignment_groups_where_can_examine(ifiadmin)[0].id)
        self.assertEquals(4,
                oblig1.assignment_groups_where_can_examine(ifiadmin).count())

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


    def test_pointscale(self):
        student1 = User.objects.get(username='student1')
        teacher1 = User.objects.get(username='teacher1')
        test = Assignment(
                parentnode = Period.objects.get(pk=1),
                publishing_time = datetime.now(),
                anonymous = False,
                autoscale = True,
                grade_plugin = "grade_approved:approvedgrade")
        test.save()
        self.assertEquals(test.pointscale, 1)
        self.assertEquals(test.maxpoints, 1)

        a = test.assignmentgroups.create(name="a")
        b = test.assignmentgroups.create(name="b")
        c = test.assignmentgroups.create(name="c")
        for g, grade in ((a, "+"), (b, "+"), (c, "-")):
            d = Delivery.begin(g, student1)
            d.add_file("test.txt", ["test"])
            d.finish()
            f = d.get_feedback()
            f.last_modified_by = teacher1
            f.published = True
            f.set_grade_from_xmlrpcstring(grade)
            f.save()

        # With autoscale
        points = [g.points for g in test.assignmentgroups.all()]
        self.assertEquals(points, [1, 1, 0])
        scaled_points = [g.scaled_points for g in test.assignmentgroups.all()]
        self.assertEquals(scaled_points, [1.0, 1.0, 0.0])

        # With manual scale of 20
        test.autoscale = False
        test.pointscale = 20
        test.save()
        points = [g.points for g in test.assignmentgroups.all()]
        self.assertEquals(points, [1, 1, 0])
        scaled_points = [g.scaled_points for g in test.assignmentgroups.all()]
        self.assertEquals(scaled_points, [20.0, 20.0, 0.0])
        


class TestAssignmentGroup(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

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
        self.assertEquals(0,
                AssignmentGroup.published_where_is_examiner(examiner1,
                    old=False, active=False).count())

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

    def add_delivery(self, assignmentgroup, user):
        delivery = Delivery.begin(assignmentgroup, user)
        delivery.add_file('hello.txt', ['hello', 'world'])
        delivery.add_file('example.py', ['print "hello world"'])
        delivery.finish()

    def test_status_one_deadline(self):
        teacher1 = User.objects.get(username='teacher1')
        student1 = User.objects.get(username='student1')
        ag = AssignmentGroup(parentnode=Assignment.objects.get(id=1))

        ag.save()
        self.assertEquals(ag.status, AssignmentGroup.NO_DELIVERIES)
        self.assertEquals(ag.get_localized_status(), "No deliveries")
        self.assertEquals(ag.get_localized_student_status(), "No deliveries")

        # 'cheat' by setting default deadline time to epoch
        head_deadline = ag.deadlines.all()[0]
        head_deadline.deadline = datetime(1970, 1, 1, 1, 0)
        head_deadline.save()
        
        # Adding delivery on head deadline
        self.add_delivery(ag, student1)
        self.assertEquals(ag.status, AssignmentGroup.HAS_DELIVERIES)
        self.assertEquals(ag.get_localized_status(), "Has deliveries")
        self.assertEquals(ag.get_localized_student_status(), "Has deliveries")

        time_now = datetime.now()
        deadline_5min = (time_now - timedelta(minutes=5))
        ag.deadlines.create(deadline=deadline_5min, text=None)
        # Adding delivery 5 minutes too late
        self.add_delivery(ag, student1)

        delivery1 = ag.deliveries.all()[1]
        delivery2 = ag.deliveries.all()[0]

        self.assertEquals(ag.deliveries.all().count(), 2)
        # First delivery is not after deadline even though the deadline was set
        # to 1970. That is because it's the head deadline.
        self.assertFalse(delivery1.after_deadline)
        # Second delivery delivered too late
        self.assertTrue(delivery2.after_deadline)
        # Status not corrected
        self.assertEquals(delivery2.get_status_number(), Delivery.NOT_CORRECTED)

        delivery2.feedback = Feedback(
                format = 'rst',
                text = 'test',
                last_modified_by = teacher1)
        delivery2.feedback.set_grade_from_xmlrpcstring("+")
        delivery2.feedback.save()
        # Update cache on assignment group
        ag = delivery2.assignment_group
        delivery2.save()

        self.assertEquals(delivery2.get_status_number(), Delivery.CORRECTED_NOT_PUBLISHED)

        self.assertEquals(ag.status, AssignmentGroup.CORRECTED_NOT_PUBLISHED)
        self.assertEquals(ag.get_localized_status(), "Corrected, not published")
        self.assertEquals(ag.get_localized_student_status(), "Has deliveries")

        # Test publishing feedback
        delivery2.feedback.published = True
        delivery2.feedback.save()
        ag = delivery2.assignment_group
        
        self.assertEquals(delivery2.get_status_number(), Delivery.CORRECTED_AND_PUBLISHED)
        self.assertEquals(ag.status, AssignmentGroup.CORRECTED_AND_PUBLISHED)
        self.assertEquals(ag.get_localized_status(), "Corrected and published")
        self.assertEquals(ag.get_localized_student_status(), "Corrected")
        
    def test_status_multiple_deadlines(self):
        teacher1 = User.objects.get(username='teacher1')
        student1 = User.objects.get(username='student1')
        ag = AssignmentGroup(parentnode=Assignment.objects.get(id=1))
        ag.save()

        self.assertEquals(ag.status, AssignmentGroup.NO_DELIVERIES)
        self.assertEquals(ag.get_localized_status(), "No deliveries")
        self.assertEquals(ag.get_localized_student_status(), "No deliveries")

        # 'cheat' by setting default deadline time to epoch
        head_deadline = ag.deadlines.all()[0]
        head_deadline.deadline = datetime(1970, 1, 1, 1, 0)
        head_deadline.save()
        
        time_now = datetime.now()
        time_min10 = (time_now - timedelta(minutes=10))
        ag.deadlines.create(deadline=time_min10, text=None)
        time_min5 = (time_now - timedelta(minutes=5))
        ag.deadlines.create(deadline=time_min5, text=None)
        time_plus5 = (time_now + timedelta(minutes=5))
        ag.deadlines.create(deadline=time_plus5, text=None)
        time_plus10 = (time_now + timedelta(minutes=10))
        ag.deadlines.create(deadline=time_plus10, text=None)

        # Adding delivery on deadline 
        self.add_delivery(ag, student1)
        self.add_delivery(ag, student1)
        delivery1 = ag.deliveries.all()[1]
        delivery2 = ag.deliveries.all()[0]

        deadline_min10 = Deadline.objects.get(deadline=time_min10)
        deadline_min5 = Deadline.objects.get(deadline=time_min5)
        deadline_plus5 = Deadline.objects.get(deadline=time_plus5)
        deadline_plus10 = Deadline.objects.get(deadline=time_plus10)
        
        # Was assigned the correct deadline
        self.assertEquals(delivery1.deadline_tag.id, deadline_plus5.id)
        self.assertEquals(delivery2.deadline_tag.id, deadline_plus5.id)
        
        self.assertEquals(deadline_min10.status, AssignmentGroup.NO_DELIVERIES)
        self.assertEquals(deadline_min5.status, AssignmentGroup.NO_DELIVERIES)
        self.assertEquals(deadline_plus5.status, AssignmentGroup.HAS_DELIVERIES)
        self.assertEquals(deadline_plus10.status, AssignmentGroup.NO_DELIVERIES)

        deadline_plus5.deliveries_available_before_deadline = True
        deadline_plus5.save()
        ag = delivery1.assignment_group

        self.add_delivery(ag, student1)
        deadline_plus5 = Deadline.objects.get(deadline=time_plus5)
        self.assertEquals(deadline_plus5.status, AssignmentGroup.HAS_DELIVERIES)


class TestCandidate(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']
    
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
    fixtures = ['core/deprecated_users.json', 'core/core.json']

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
        
    def test_published_where_is_candidate(self):
        student1 = User.objects.get(username='student1')
        student2 = User.objects.get(username='student2')
        student3 = User.objects.get(username='student3')
        student4 = User.objects.get(username='student4')

        # In the fixtures, student1 has 2 deliveries
        #                  student2 has 1 delivery
        #                  student3 has 1 delivery
        #                  student4 has 0 deliveries
        self.assertEquals(Delivery.published_where_is_candidate(student1).count(), 2)
        self.assertEquals(Delivery.published_where_is_candidate(student2).count(), 1)
        self.assertEquals(Delivery.published_where_is_candidate(student3).count(), 1)
        self.assertEquals(Delivery.published_where_is_candidate(student4).count(), 0)


# TODO: Feedback tests
class TestFeedback(TestCase):

    # fixtures = ['core/deprecated_users.json', 'core/core.json']
    # using the 'new' test-data, since the 'old' data doesn't have
    # feedbacks inserted
    fixtures = ['simplified/data.json']

    def setUp(self):
        self.candidate0 = User.objects.get(username='student0')
        self.candidate1 = User.objects.get(username='student1')

    def test_published_where_is_candidate(self):
        self.assertEquals(Feedback.published_where_is_candidate(self.candidate0).count(), 8)
        self.assertEquals(Feedback.published_where_is_candidate(self.candidate1).count(), 7)
        
    def test_published_where_is_examiner(self):
        examiner0 = User.objects.get(username='examiner0')
        examiner0_feedbacks = Feedback.published_where_is_examiner(examiner0)
        self.assertEquals(len(examiner0_feedbacks), 15)


class TestFeedbackPublish(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

    def create_feedback(self, delivery, text): # TODO: Simplify this when gradeplugin stuff is removed from Feedback
        assignment = delivery.assignment_group.parentnode
        feedback = delivery.get_feedback()
        feedback.text = text
        examiner = delivery.assignment_group.examiners.all()[0]
        feedback.last_modified_by = examiner
        gradeplugin = assignment.get_gradeplugin_registryitem().model_cls
        examplegrade = gradeplugin.get_example_xmlrpcstring(assignment, 1)
        feedback.set_grade_from_xmlrpcstring(examplegrade)
        feedback.save()
        return feedback

    def setUp(self):
        teacher1 = User.objects.get(username='teacher1')
        delivery = Delivery.objects.all()[0]
        delivery.assignment_group.examiners.add(teacher1)

        self.feedback = self.create_feedback(delivery, "Test")
        self.assignment = self.feedback.delivery.assignment_group.parentnode
        self.deadline = self.feedback.delivery.deadline_tag
        self.deadline.feedbacks_published = False
        self.deadline.save()

    def test_publish_feedbacks_directly(self):
        self.assignment.examiners_publish_feedbacks_directly = True
        self.assignment.save()
        self.feedback.save()
        self.assertTrue(Deadline.objects.get(id=self.deadline.id).feedbacks_published)

    def test_dont_publish_feedbacks_directly(self):
        self.assignment.examiners_publish_feedbacks_directly = False
        self.assignment.save()
        self.feedback.save()
        self.assertFalse(Deadline.objects.get(id=self.deadline.id).feedbacks_published)



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
