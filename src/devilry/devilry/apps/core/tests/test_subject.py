from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from ..models import Node, Subject
from ..testhelper import TestHelper
from ..models.model_utils import EtagMismatchException

class TestSubject(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1060:admin(teacher1)", "inf1100"],
                 periods=["autumn10:begins(-1)", "spring9:begins(-1)"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:examiner(examiner1)", "g2:examiner(examiner2)"])
        
    def test_unique(self):
        s = Subject(parentnode=Node.objects.get(short_name='ifi'),
                    short_name='inf1060', long_name='INF1060')
        self.assertRaises(IntegrityError, s.save)

    def test_unique2(self):
        s = Subject(parentnode=Node.objects.get(short_name='uio'),
                short_name='inf1060', long_name='INF1060')
        self.assertRaises(IntegrityError, s.save)

    def test_etag_update(self):
        etag = datetime.now()
        obj = self.inf1100
        obj.long_name = "Test"
        self.assertRaises(EtagMismatchException, obj.etag_update, etag)
        try:
            obj.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            obj.etag_update(e.etag)
        obj2 = Subject.objects.get(id=obj.id)
        self.assertEquals(obj2.long_name, "Test")

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(Subject.where_is_admin(teacher1).count(), 1)
        self.assertEquals(Subject.where_is_admin(uioadmin).count(), 2)

    def test_get_path(self):
        self.assertEquals(self.inf1100.get_path(), 'inf1100')

    def test_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        q = Subject.where_is_examiner(examiner1)
        self.assertEquals(q.count(), 2)
        self.assertEquals(q[0].short_name, 'inf1060')
        self.assertEquals(q[1].short_name, 'inf1100')

        self.add_to_path('uio.ifi;inf1010.spring10.oblig1.group1')
        self.inf1010_spring10_oblig1_group1.examiners.create(user=examiner1)
        self.inf1010_spring10_oblig1.save()
        q = Subject.where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 3)
        self.assertEquals(q[0].short_name, 'inf1010')
        self.assertEquals(q[1].short_name, 'inf1060')

    def test_published_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        q = Subject.published_where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 2)
        self.assertEquals(q[0].short_name, 'inf1060')
        self.assertEquals(q[1].short_name, 'inf1100')

        self.add_to_path('uio.ifi;inf1010.spring10:begins(-1).oblig1.group1')
        self.inf1010_spring10_oblig1_group1.examiners.create(user=examiner1)
        self.inf1010_spring10_oblig1_group1.save()
        q = Subject.published_where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 3)
        self.assertEquals(q[0].short_name, 'inf1010')
        self.assertEquals(q[1].short_name, 'inf1060')

        assignment1010 = self.inf1010_spring10_oblig1_group1.parentnode
        assignment1010.publishing_time = datetime.now() + timedelta(10)
        assignment1010.save()
        q = Subject.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 2)

    def test_is_empty(self):
        self.assertFalse(self.inf1060.is_empty())
        self.add(nodes="uio.ifi", subjects=['duck9000'])
        self.assertTrue(self.duck9000.is_empty())
