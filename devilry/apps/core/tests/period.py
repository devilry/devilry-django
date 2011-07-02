from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from ..models import Period, Subject
from ..testhelpers import create_from_path

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
