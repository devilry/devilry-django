from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from datetime import datetime, timedelta

from ..models import Node, Subject
from ..testhelpers import create_from_path

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
