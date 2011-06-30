from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Subject, Period, Assignment
from ..testhelpers import create_from_path

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
