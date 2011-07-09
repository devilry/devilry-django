from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from ..models import Period, Subject
from ..testhelper import TestHelper
from ..models.model_utils import EtagMismatchException

class TestPeriod(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi",
                 subjects=["inf1100"],
                 periods=["old:begins(-2):ends(1)", "looong"],
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
        obj.minimum_points = 66
        self.assertRaises(EtagMismatchException, obj.etag_update, etag)
        try:
            obj.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            obj.etag_update(e.etag)
        obj2 = Period.objects.get(id=obj.id)
        self.assertEquals(obj2.minimum_points, 66)

    def test_where_is_admin(self):
        self.assertEquals(Period.where_is_admin(self.uioadmin).count(), 2)

    def test_clean(self):
        self.inf1100_looong.start_time = datetime(2010, 1, 1)
        self.inf1100_looong.end_time = datetime(2011, 1, 1)
        self.inf1100_looong.clean()
        self.inf1100_looong.start_time = datetime(2012, 1, 1)
        self.assertRaises(ValidationError, self.inf1100_looong.clean)

    def test_get_by_path(self):
        self.assertEquals(Period.get_by_path('inf1100.old').short_name, 'old')
        self.assertRaises(Period.DoesNotExist, Period.get_by_path, 'does.notexist')
        self.assertRaises(ValueError, Period.get_by_path, 'does.not.exist')

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
        self.add_to_path('uio.ifi;inf1010.spring10.oblig1.student1:examiner(examiner1)')
        q = Period.published_where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 3)
        assignment1010 = self.inf1010_spring10_oblig1_student1.parentnode
        assignment1010.publishing_time = datetime.now() + timedelta(10)
        assignment1010.save()
        self.assertEquals(q.count(), 2)
