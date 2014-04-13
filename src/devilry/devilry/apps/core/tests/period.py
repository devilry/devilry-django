from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from devilry_developer.testhelpers.corebuilder import NodeBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
# from devilry_developer.testhelpers.datebuilder import DateTimeBuilder
from devilry.apps.core.models import Subject
from devilry.apps.core.models import Period
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models.model_utils import EtagMismatchException



class TestPeriod(TestCase):
    def test_create_many_multiple_subjects(self):
        nodebuilder = NodeBuilder('ducku')
        subject1 = nodebuilder.add_subject('subject1').subject
        subject2 = nodebuilder.add_subject('subject2').subject
        unusedsubject = nodebuilder.add_subject('unusedsubject').subject
        Period.objects.create_many([subject1, subject2],
            start_time=datetime(2014, 1, 1,),
            end_time=datetime(2014, 2, 1),
            short_name='testperiod')
        self.assertEquals(subject1.periods.count(), 1)
        self.assertEquals(subject2.periods.count(), 1)
        self.assertEquals(unusedsubject.periods.count(), 0)
        self.assertEquals(subject1.periods.all()[0].short_name, 'testperiod')
        self.assertEquals(subject2.periods.all()[0].short_name, 'testperiod')

    def test_create_many_details(self):
        nodebuilder = NodeBuilder('ducku')
        subject1 = nodebuilder.add_subject('subject1').subject
        Period.objects.create_many([subject1],
            start_time=datetime(2014, 1, 1),
            end_time=datetime(2014, 2, 1),
            short_name='testperiod')
        self.assertEquals(subject1.periods.count(), 1)
        testperiod = subject1.periods.all()[0]
        self.assertEquals(testperiod.short_name, 'testperiod')
        self.assertEquals(testperiod.start_time, datetime(2014, 1, 1))
        self.assertEquals(testperiod.end_time, datetime(2014, 2, 1))


    def test_relatedstudents_by_tag(self):
        period = PeriodBuilder.quickadd_ducku_duck1010_active().period
        relatedstudent1 = period.relatedstudent_set.create(
            user=UserBuilder('studentuser1').user,
            tags='group1,special')
        relatedstudent2 = period.relatedstudent_set.create(
            user=UserBuilder('studentuser2').user,
            tags='group1')
        relatedstudent3 = period.relatedstudent_set.create(
            user=UserBuilder('studentuser3').user,
            tags='group2,special')
        bytag = period.relatedstudents_by_tag()
        self.assertEquals(bytag, {
            'group1': [relatedstudent1, relatedstudent2],
            'group2': [relatedstudent3],
            'special': [relatedstudent1, relatedstudent3]
        })

    def test_relatedexaminers_by_tag(self):
        period = PeriodBuilder.quickadd_ducku_duck1010_active().period
        relatedexaminer1 = period.relatedexaminer_set.create(
            user=UserBuilder('examineruser1').user,
            tags='group1,special')
        relatedexaminer2 = period.relatedexaminer_set.create(
            user=UserBuilder('examineruser2').user,
            tags='group1')
        relatedexaminer3 = period.relatedexaminer_set.create(
            user=UserBuilder('examineruser3').user,
            tags='group2,special')
        bytag = period.relatedexaminers_by_tag()
        self.assertEquals(bytag, {
            'group1': [relatedexaminer1, relatedexaminer2],
            'group2': [relatedexaminer3],
            'special': [relatedexaminer1, relatedexaminer3]
        })


class TestPeriodOld(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi",
                 subjects=["inf1100"],
                 periods=["old:begins(-2):ends(1)", "looong:begins(-1):ends(10)"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:examiner(examiner1)", "g2:examiner(examiner2)"])

    def test_unique(self):
        n = Period(parentnode=Subject.objects.get(short_name='inf1100'),
                short_name='old', long_name='Old',
                start_time=datetime.now(),
                end_time=datetime.now())
        self.assertRaises(IntegrityError, n.save)

    def test_etag_update(self):
        etag = datetime.now()
        obj = self.inf1100_looong
        obj.long_name = 'Updated'
        self.assertRaises(EtagMismatchException, obj.etag_update, etag)
        try:
            obj.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            obj.etag_update(e.etag)
        obj2 = Period.objects.get(id=obj.id)
        self.assertEquals(obj2.long_name, 'Updated')

    def test_where_is_admin(self):
        self.assertEquals(Period.where_is_admin(self.uioadmin).count(), 2)

    def test_clean(self):
        self.inf1100_looong.start_time = datetime(2010, 1, 1)
        self.inf1100_looong.end_time = datetime(2011, 1, 1)
        self.inf1100_looong.clean()
        self.inf1100_looong.start_time = datetime(2012, 1, 1)
        self.assertRaises(ValidationError, self.inf1100_looong.clean)

    def test_where_is_examiner(self):
        q = Period.where_is_examiner(self.examiner1).order_by('short_name')
        self.assertEquals(q.count(), 2)
        self.assertEquals(q[0].short_name, 'looong')
        self.assertEquals(q[1].short_name, 'old')
        # Add on different period
        self.add_to_path('uio.ifi;inf1010.spring10.oblig1.student1:examiner(examiner1)')
        self.assertEquals(q.count(), 3)
        self.assertEquals(q[0].short_name, 'looong')
        self.assertEquals(q[1].short_name, 'old')
        self.assertEquals(q[2].short_name, 'spring10')

    def test_published_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        self.add_to_path('uio.ifi;inf1010.spring10:begins(-1):ends(2).oblig1.student1:examiner(examiner1)')
        q = Period.published_where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 3)
        assignment1010 = self.inf1010_spring10_oblig1_student1.parentnode
        assignment1010.publishing_time = datetime.now() + timedelta(10)
        assignment1010.save()
        self.assertEquals(q.count(), 2)

    def test_is_empty(self):
        self.assertFalse(self.inf1100_old.is_empty())
        self.add(nodes="uio.ifi", subjects=['duck9000'], periods=['emptyperiod'])
        self.assertTrue(self.duck9000_emptyperiod.is_empty())


    def test_q_is_active(self):
        activeperiods = Period.objects.filter(Period.q_is_active())
        self.assertEquals(activeperiods.count(), 1)
        self.assertEqual(activeperiods[0], self.inf1100_looong)
        self.inf1100_old.end_time = datetime.now() + timedelta(days=10)
        self.inf1100_old.save()
        self.assertEquals(Period.objects.filter(Period.q_is_active()).count(), 2)
