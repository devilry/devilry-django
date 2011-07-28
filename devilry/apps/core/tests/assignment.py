from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from django.db.models import Q
from ..models import Period, Assignment, AssignmentGroup, Candidate
from ..testhelper import TestHelper
from ..models.model_utils import EtagMismatchException

class TestAssignment(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["old:begins(-2):ends(1)", "looong"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)", "g2:examiner(examiner2)",
                                   "g3:candidate(student2,student3):examiner(examiner1,examiner2)"])
        self.add_to_path('uio.ifi;inf1100.looong.assignment3.group1:examiner(examiner1)')
        self.add_to_path('uio.ifi;inf1100.old.oldassignment.group1:examiner(examiner3)')

    def test_unique(self):
        n = Assignment(parentnode=Period.objects.get(short_name='looong'),
                short_name='assignment1', long_name='O1',
                publishing_time=datetime.now())
        self.assertRaises(IntegrityError, n.save)

    def anon_change_anonymous(self):
        self.inf1100_looong_assignment1.anonymous = True
        self.inf1100_looong_assignment1.save()
        candidates = Candidate.objects.filter(Q(assignment_group__parentnode__id=\
                                                self.inf1100_looong_assignment1.id))
        for can in candidates:
            self.assertEquals(can.candidate_id, can.identifier)
        self.inf1100_looong_assignment1.anonymous = False
        self.inf1100_looong_assignment1.save()
        candidates = Candidate.objects.filter(Q(assignment_group__parentnode__id=\
                                                self.inf1100_looong_assignment1.id))
        for can in candidates:
            self.assertEquals(can.student.username, can.identifier)

    def test_etag_update(self):
        etag = datetime.now()
        obj = self.inf1100_looong_assignment1
        obj.anonymous = True
        self.assertRaises(EtagMismatchException, obj.etag_update, etag)
        try:
            obj.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            obj.etag_update(e.etag)
        obj2 = Assignment.objects.get(id=obj.id)
        self.assertTrue(obj2.anonymous)

    def test_where_is_admin(self):
        ifiadmin = User.objects.get(username='ifiadmin')
        self.assertEquals(Assignment.where_is_admin(ifiadmin).count(), 6)

    def test_where_is_examiner(self):
        examiner3 = User.objects.get(username='examiner3')
        q = Assignment.where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oldassignment')
        self.inf1100_looong_assignment3_group1.examiners.add(examiner3)
        self.assertEquals(q.count(), 2)

    def test_published_where_is_examiner(self):
        User.objects.get(username='examiner3')
        q = Assignment.published_where_is_examiner(self.examiner3, old=False, active=False)
        self.assertEquals(q.count(), 0)
        
        q = Assignment.published_where_is_examiner(self.examiner3)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oldassignment')

        # Add as examiner, count should increase
        self.inf1100_looong_assignment1_g1.examiners.add(self.examiner3)
        self.assertEquals(q.count(), 2)
        # Set publishing_time to future. count should decrease
        self.inf1100_looong_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_looong_assignment1.save()
        q = Assignment.published_where_is_examiner(self.examiner3)
        self.assertEquals(q.count(), 1)

    def test_active_where_is_examiner(self):
        past = datetime.now() - timedelta(10)
        examiner1 = User.objects.get(username='examiner1')
        # Get assignments where the period is active
        q = Assignment.active_where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 3)
        self.assertEquals(q[0].short_name, 'assignment1')
        self.assertEquals(q[1].short_name, 'assignment2')
        self.assertEquals(q[2].short_name, 'assignment3')
        
        #Create group2 with examiner1 as examiner
        self.add_to_path('uio.ifi;inf1010.spring10.assignment0.group2:examiner(examiner1)')
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 4)
        self.inf1010_spring10.end_time = past
        self.inf1010_spring10.save()
        self.assertEquals(q.count(), 3)
        self.inf1010_spring10_assignment0.publishing_time = past
        self.inf1010_spring10_assignment0.save()
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 3)

    def test_old_where_is_examiner(self):
        past = datetime.now() - timedelta(10)
        examiner3 = User.objects.get(username='examiner3')
        q = Assignment.old_where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oldassignment')
        
        # Set as examiner on group1
        self.add_to_path('uio.ifi;inf1100.looong.assignment1.group1:examiner(examiner3)')
        q = Assignment.old_where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        # Making the period old and verify that the count has changed
        self.inf1100_looong.end_time = past
        self.inf1100_looong.save()
        self.assertEquals(q.count(), 2)

    def test_assignmentgroups_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        self.assertEquals(self.inf1100_looong_assignment1_g1.id,
                          self.inf1100_looong_assignment1.assignment_groups_where_is_examiner(examiner1)[0].id)
        self.assertEquals(2,
                self.inf1100_looong_assignment1.assignment_groups_where_is_examiner(examiner2).count())

    def test_clean_publishing_time_before(self):
        assignment1 = self.inf1100_looong_assignment1
        assignment1.parentnode.start_time = datetime(2010, 1, 1)
        assignment1.parentnode.end_time = datetime(2011, 1, 1)
        assignment1.publishing_time = datetime(2010, 1, 2)
        assignment1.clean()
        assignment1.publishing_time = datetime(2009, 1, 1)
        self.assertRaises(ValidationError, assignment1.clean)

    def test_clean_publishing_time_after(self):
        assignment1 = self.inf1100_looong_assignment1
        assignment1.parentnode.start_time = datetime(2010, 1, 1)
        assignment1.parentnode.end_time = datetime(2011, 1, 1)
        assignment1.publishing_time = datetime(2010, 1, 2)
        assignment1.clean()
        assignment1.publishing_time = datetime(2012, 1, 1)
        self.assertRaises(ValidationError, assignment1.clean)

    def test_get_path(self):
        self.assertEquals(self.inf1100_looong_assignment1.get_path(), 'inf1100.looong.assignment1')
