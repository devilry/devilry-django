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
        Delivery, Candidate, StaticFeedback, FileMeta, Deadline)
from deliverystore import (MemoryDeliveryStore, FsDeliveryStore,
    DbmDeliveryStore)
from testhelpers import TestDeliveryStoreMixin, create_from_path
from testinitializer import TestInitializer

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
        test = Assignment(parentnode = Period.objects.get(pk=1),
                          publishing_time = datetime.now(),
                          anonymous = False,
                          autoscale = True,
                          maxpoints = 1,
                          grade_plugin = "grade_approved:approvedgrade")
        test.save()
        self.assertEquals(test.pointscale, 1)
        self.assertEquals(test.maxpoints, 1)

        a = test.assignmentgroups.create(name="a")
        b = test.assignmentgroups.create(name="b")
        c = test.assignmentgroups.create(name="c")
        for assignmentgroup, points in ((a, 1), (b, 1), (c, 0)):
            delivery = assignmentgroup.deliveries.create(delivered_by=student1, successful=True)
            delivery.feedbacks.create(rendered_view="", grade="ok", points=points,
                                      is_passing_grade=bool(points),
                                      saved_by=teacher1)

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
        assignmentgroup.deliveries.create(delivered_by=user,
                                          successful=True)

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

        delivery2.feedbacks.create(rendered_view="", grade="ok", points=1,
                                   is_passing_grade=True, saved_by=teacher1)
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
        d = assignmentgroup.deliveries.create(delivered_by=student1,
                                              successful=False)
        self.assertEquals(d.assignment_group, assignmentgroup)
        self.assertFalse(d.successful)
        d.successful = True
        d.save()
        self.assertEquals(d.assignment_group, assignmentgroup)
        self.assertTrue(d.successful)
        self.assertEquals(d.number, 3)

        d2 = assignmentgroup.deliveries.create(delivered_by=student1,
                                               successful=True)
        self.assertTrue(d2.successful)
        self.assertEquals(d2.number, 4)
        d2.save()

        # TODO find a graceful way to handle this error:
        d2.number = 3
        self.assertRaises(IntegrityError, d2.save)

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


# TODO: StaticFeedback tests
class TestFeedback(TestCase):

    # fixtures = ['core/deprecated_users.json', 'core/core.json']
    # using the 'new' test-data, since the 'old' data doesn't have
    # feedbacks inserted
    fixtures = ['simplified/data.json']

    def setUp(self):
        self.candidate0 = User.objects.get(username='student0')
        self.candidate1 = User.objects.get(username='student1')

    def test_published_where_is_candidate(self):
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.candidate0).count(), 8)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.candidate1).count(), 7)
        
    def test_published_where_is_examiner(self):
        examiner0 = User.objects.get(username='examiner0')
        examiner0_feedbacks = StaticFeedback.published_where_is_examiner(examiner0)
        self.assertEquals(len(examiner0_feedbacks), 15)


class TestFeedbackPublish(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

    def create_feedback(self, delivery, text):
        examiner = delivery.assignment_group.examiners.all()[0]
        feedback = delivery.feedbacks.create(rendered_view=text, grade="ok", points=1,
                                             is_passing_grade=True,
                                             saved_by=examiner)
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


class TestTestInitializer(TestCase):

    def setUp(self):
        self.ti = TestInitializer()

    def test_nodes(self):
        self.ti.add(nodes='uio.ifi')
        self.assertEquals(Node.objects.all().count(), 2)

        # check relations between them
        self.assertEquals(self.ti.uio.parentnode, None)
        self.assertEquals(self.ti.ifi.parentnode, self.ti.uio)
        self.assertTrue(self.ti.ifi in self.ti.uio.child_nodes.all())

    def test_many_root_nodes(self):
        self.ti.add(nodes='uio.ifi')
        self.assertEquals(Node.objects.all().count(), 2)

        # check relations between them
        self.assertEquals(self.ti.uio.parentnode, None)
        self.assertEquals(self.ti.ifi.parentnode, self.ti.uio)
        self.assertTrue(self.ti.ifi in self.ti.uio.child_nodes.all())

    def test_single_nodes(self):
        self.ti.add(nodes='uio')
        self.ti.add(nodes='ifi')

        self.assertEquals(Node.objects.all().count(), 2)
        # uio = Node.objects.get(short_name='uio')
        # ifi = Node.objects.get(short_name='ifi')

        # check relations between them
        self.assertEquals(self.ti.uio.parentnode, None)
        self.assertEquals(self.ti.ifi.parentnode, None)
        self.assertTrue(self.ti.ifi not in self.ti.uio.child_nodes.all())

    def test_nodes_and_admins(self):
        self.ti.add(nodes='uio:admin(rektor).ifi:admin(mortend)')

        # Assert that all nodes and admins are created
        self.assertEquals(Node.objects.filter(short_name='uio').count(), 1)
        self.assertEquals(Node.objects.filter(short_name='ifi').count(), 1)
        self.assertEquals(User.objects.filter(username='rektor').count(), 1)
        self.assertEquals(User.objects.filter(username='mortend').count(), 1)

        # assert that they are both admins
        self.assertTrue(self.ti.rektor in self.ti.uio.admins.all())
        self.assertTrue(self.ti.mortend in self.ti.ifi.admins.all())

        # assert that uio has ifi as a child node and ifi has uio as parent
        self.assertTrue(self.ti.ifi in self.ti.uio.child_nodes.all())
        self.assertEquals(self.ti.ifi.parentnode, self.ti.uio)
        self.assertEquals(self.ti.uio.parentnode, None)

    def test_nodes_and_one_admin(self):
        self.ti.add(nodes='uio.ifi:admin(mortend)')

        self.assertEquals(Node.objects.filter(short_name='uio').count(), 1)
        self.assertEquals(Node.objects.filter(short_name='ifi').count(), 1)

        # mortend = User.objects.get(username='mortend')
        # ifi = Node.objects.get(short_name='ifi')
        self.assertTrue(self.ti.mortend in self.ti.ifi.admins.all())

    def test_subject(self):
        self.ti.add(nodes='ifi:admin(mortend)',
                    subjects=['inf1000', 'inf1010'])

        # assert that the subjects are there
        self.assertEquals(Subject.objects.filter(short_name='inf1000').count(), 1)
        self.assertEquals(Subject.objects.filter(short_name='inf1010').count(), 1)

        # assert that the parentnode is ifi
        self.assertEquals(self.ti.ifi, self.ti.inf1000.parentnode)
        self.assertEquals(self.ti.ifi, self.ti.inf1010.parentnode)

    def test_subject_with_admins(self):
        self.ti.add(nodes='uio:admin(rektor).ifi:admin(mortend)',
                    subjects=['inf1000:admin(arnem)', 'inf1010:admin(steinm,steingj)'])

        # assert that the subject admin users where created
        self.assertEquals(User.objects.filter(username='arnem').count(), 1)
        self.assertEquals(User.objects.filter(username='steinm').count(), 1)
        self.assertEquals(User.objects.filter(username='steingj').count(), 1)

        # inf1000 = Subject.objects.get(short_name='inf1000')
        # inf1010 = Subject.objects.get(short_name='inf1010')

        # arnem = User.objects.get(username='arnem')
        # steinm = User.objects.get(username='steinm')
        # steingj = User.objects.get(username='steingj')

        # assert that they are all admins in their subjects
        self.assertTrue(self.ti.arnem in self.ti.inf1000.admins.all())
        self.assertTrue(self.ti.steinm in self.ti.inf1010.admins.all())
        self.assertTrue(self.ti.steingj in self.ti.inf1010.admins.all())

    def test_period(self):
        self.ti.add(nodes='ifi:admin(mortend)',
                    subjects=['inf1000', 'inf1010'],
                    periods=['fall01', 'spring01'])

        # assert that the periods are there. There should be 2 of
        # each, since there are (should!) 2 subjects.
        self.assertEquals(Period.objects.filter(short_name='spring01').count(), 2)
        self.assertEquals(Period.objects.filter(short_name='fall01').count(), 2)

        # assert that the parentnodes are correct
        self.assertEquals(self.ti.inf1010_fall01.parentnode, self.ti.inf1010)
        self.assertEquals(self.ti.inf1010_spring01.parentnode, self.ti.inf1010)

    def test_period_with_admins(self):
        self.ti.add(nodes='uio:admin(rektor).ifi:admin(mortend)',
                    subjects=['inf1000', 'inf1010'],
                    periods=['fall01:admin(steingj)', 'spring01:admin(steinm)'])

        # assert that the users are created
        self.assertEquals(User.objects.filter(username='steingj').count(), 1)
        self.assertEquals(User.objects.filter(username='steinm').count(), 1)

        # assert that they are admins for the periods
        self.assertTrue(self.ti.steingj in self.ti.inf1000_fall01.admins.all())
        self.assertTrue(self.ti.steinm in self.ti.inf1000_spring01.admins.all())

    def test_assignment(self):
        self.ti.add(nodes='ifi:admin(mortend)',
                    subjects=['inf1000', 'inf1010'],
                    periods=['fall01', 'spring01'],
                    assignments=['oblig1', 'oblig2'])

        # assert that the assignments are there. There should be 4 of
        # each, since there are (should!) 2 periods.
        self.assertEquals(Assignment.objects.filter(short_name='oblig1').count(), 4)
        self.assertEquals(Assignment.objects.filter(short_name='oblig2').count(), 4)

        # assert that the parentnodes are correct
        self.assertEquals(self.ti.inf1010_fall01.parentnode, self.ti.inf1010)
        self.assertEquals(self.ti.inf1010_spring01.parentnode, self.ti.inf1010)

    def test_assignment_with_admin(self):
        self.ti.add(nodes='ifi',
                    subjects=['inf1000:admin(arnem)'],
                    periods=['fall01'],
                    assignments=['oblig1:admin(jose)', 'oblig2:admin(jose)'])

        # Assert that the admins are created
        self.assertEquals(User.objects.filter(username='arnem').count(), 1)
        self.assertEquals(User.objects.filter(username='jose').count(), 1)

        # check that jose is an admin for the assignment
        self.assertTrue(self.ti.jose in self.ti.inf1000_fall01_oblig1.admins.all())
        self.assertTrue(self.ti.jose in self.ti.inf1000_fall01_oblig2.admins.all())

        # check that arnem also has admin rights in the assignments
        self.assertTrue(self.ti.inf1000_fall01_oblig1 in Assignment.where_is_admin(self.ti.arnem).all())
        self.assertTrue(self.ti.inf1000_fall01_oblig2 in Assignment.where_is_admin(self.ti.arnem).all())

    def test_assignmentgroups(self):
        self.ti.add(nodes="ifi",
                 subjects=["inf1000", "inf1100"],
                 periods=["fall01", "spring01"],
                 assignments=["oblig1", "oblig2"],
                 assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                   'g2:candidate(nataliib):examiner(jose)'])

        # assert that the assignmentgroups are there. There should be 8 of
        # each, since there are (should!) 2 assignments.
        self.assertEquals(AssignmentGroup.objects.filter(name='g1').count(), 8)
        self.assertEquals(AssignmentGroup.objects.filter(name='g2').count(), 8)

        # assert that the parentnodes are correct
        self.assertEquals(self.ti.inf1100_fall01_oblig1_g1.parentnode, self.ti.inf1100_fall01_oblig1)
        self.assertEquals(self.ti.inf1100_spring01_oblig1_g2.parentnode, self.ti.inf1100_spring01_oblig1)

        # assert that the candidates are candidates in the assignment
        self.assertTrue(self.ti.inf1100_fall01_oblig1 in Assignment.where_is_candidate(self.ti.zakia))
        self.assertTrue(self.ti.inf1100_fall01_oblig1 in Assignment.where_is_candidate(self.ti.nataliib))

        # assert that the examiners are examiners in the assignment
        self.assertTrue(self.ti.inf1100_fall01_oblig1_g1 in AssignmentGroup.where_is_examiner(self.ti.cotryti))
        self.assertTrue(self.ti.inf1100_fall01_oblig1_g2 in AssignmentGroup.where_is_examiner(self.ti.jose))

    def test_updating_paths(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['fall01', 'spring01'],
                    assignments=['oblig1'])

        self.ti.add(nodes='ifi',
                    subjects=['inf1000', 'inf1010'],
                    periods=['spring01'],
                    assignments=['oblig2'])

        # assert that spring01 has oblig2
        self.assertEquals(self.ti.inf1000_spring01.assignments.filter(short_name='oblig2').count(), 1)
        # assert that fall01 doesn't have oblig2
        self.assertEquals(self.ti.inf1000_fall01.assignments.filter(short_name='oblig2').count(), 0)
        # assert that uio doesn't have any subjects and stuff
        self.assertEquals(self.ti.uio.subjects.all().count(), 0)

        self.ti.add(nodes='ifi', subjects=['inf2220'], periods=['fall01', 'spring01'], assignments=['oblig1', 'oblig2'])

        # assert that inf2220 has 2 assignments
        self.assertEquals(self.ti.inf2220_fall01.assignments.all().count(), 2)
        # and that inf1010 is the same as before
        self.assertEquals(self.ti.inf1000_spring01.assignments.filter(short_name='oblig2').count(), 1)
        self.assertEquals(self.ti.inf1000_fall01.assignments.filter(short_name='oblig2').count(), 0)

    def test_wrong_input(self):
        self.ti.add()

        # assert that nothing was created
        self.assertEquals(self.ti.objects_created, 0)

        self.ti.add(subjects=['inf1010'])
        # assert that nothing was created
        self.assertEquals(self.ti.objects_created, 0)

    # def test_huge_test(self):
    #     self.ti.add(nodes="uio:admin(rektor).ifi:admin(mortend)",
    #                 subjects=["inf1000:admin(arnem)", "inf1010:admin(steingj,steinm)"],
    #                 periods=["fall01:admin(jose)", "spring01:admin(espeak)"],
    #                 assignments=["oblig1:admin(cotryti)", "oblig2:admin(bendiko)"],
    #                 assignmentgroups=['g1:candidate(zakia,mariherr,jensp):examiner(cotryti)',
    #                                   'g2:candidate(nataliib,runeama,trygv,stiansma):examiner(bendiko)'])

    def test_deadlines(self):
        self.ti.add(nodes="ifi",
                    subjects=["inf1000", "inf1100"],
                    periods=["fall01", "spring01"],
                    assignments=["oblig1", "oblig2"],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=[])

    def test_period_times(self):

        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2'])

        today = datetime.today().date()
        sixIshMonthsFromToday = (datetime.today() + timedelta(days=6 * 30)).date()

        # assert that first period starts today
        self.assertEquals(self.ti.inf1000_first.start_time.date(), today)

        # assert that the second semester begins in about 6 months
        # and that it ends about 1 month from then
        self.assertEquals(self.ti.inf1000_second.start_time.date(), sixIshMonthsFromToday)
        self.assertEquals(self.ti.inf1000_second.end_time.date(), sixIshMonthsFromToday + timedelta(days=30))

        # assert that first is active, while the second isnt
        self.assertTrue(self.ti.inf1000_first.is_active())
        self.assertFalse(self.ti.inf1000_second.is_active())

        # add an old period
        self.ti.add(nodes='ifi', subjects=['inf1000'], periods=['old:begins(-2):ends(1)'])

        # assert that old began 2 months ago, and that it ended 1 month ago.
        self.assertEquals(self.ti.inf1000_old.start_time.date(), today + timedelta(days=-60))
        # And that it isnt active
        self.assertEquals(self.ti.inf1000_old.end_time.date(), today + timedelta(days=-30))
        self.assertFalse(self.ti.inf1000_old.is_active())

    def test_assignments_times(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2:pub(10)', 'oblig3:pub(20)'])

        today = datetime.today().date()
        self.assertEquals(self.ti.inf1000_first_oblig1.publishing_time.date(), today)
        self.assertEquals(self.ti.inf1000_first_oblig2.publishing_time.date(), today + timedelta(days=10))
        self.assertEquals(self.ti.inf1000_first_oblig3.publishing_time.date(), today + timedelta(days=20))

    def test_add_to_path(self):

        self.ti.add_to_path('uio:admin(rektor).ifi:admin(mortend);inf1000:admin(stein,steing).fall01')
        self.assertTrue(self.ti.rektor in self.ti.uio.admins.all())
        self.assertTrue(self.ti.mortend in self.ti.ifi.admins.all())
        self.assertTrue(self.ti.stein in self.ti.inf1000.admins.all())
        self.assertTrue(self.ti.steing in self.ti.inf1000.admins.all())

    def test_deadliness(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text("heihei")', 'd2:ends(20)'])

        today = datetime.today().date()

        # assert that the deadlines are created correctly
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_d1.deadline.date(), today + timedelta(days=10))
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_d2.deadline.date(), today + timedelta(days=20))
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_d1.text, '"heihei"')

        self.assertEquals(Deadline.objects.all().count(), 2)

        # add a new deadline for g1. This should overwrite the
        # previous d1 deadline
        self.ti.add_to_path('ifi;inf1000.first.oblig1.g1.d1:text("heeellllooo")')

        self.assertEquals(self.ti.inf1000_first_oblig1_g1_d1.text, '"heeellllooo""')
        self.assertEquals(Deadline.objects.all(), 3)
        # assert that the texts are set correctly
