from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from ..models import Assignment, AssignmentGroup, Delivery, Deadline
from ..testhelper import TestHelper
from ..models.model_utils import EtagMismatchException

class TestAssignmentGroup(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["old:begins(-2):ends(1)", "looong:admin(teacher1)"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                   "g2:candidate(student2):examiner(examiner2)",
                                   "g3:candidate(student3,student2):examiner(examiner1,examiner2,examiner3)"])
        self.add_to_path('uio.ifi;inf1100.old.oldassignment.group1:examiner(examiner3)')

    def test_where_is_admin(self):
        self.assertEquals(6, AssignmentGroup.where_is_admin(self.teacher1).count())

    def test_where_is_candidate(self):
        self.assertEquals(8, AssignmentGroup.where_is_candidate(self.student2).count())
        self.assertEquals(4, AssignmentGroup.where_is_candidate(self.student1).count())

    def test_published_where_is_candidate(self):
        self.assertEquals(8, AssignmentGroup.published_where_is_candidate(self.student2).count())
        self.assertEquals(4, AssignmentGroup.published_where_is_candidate(self.student3).count())

    def test_active_where_is_candidate(self):
        self.assertEquals(4, AssignmentGroup.active_where_is_candidate(self.student2).count())
        # Set publishing time to future
        self.inf1100_looong_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_looong_assignment1.save()
        self.assertEquals(2, AssignmentGroup.active_where_is_candidate(self.student2).count())
        
    def test_old_where_is_candidate(self):
        self.assertEquals(2, AssignmentGroup.old_where_is_candidate(self.student1).count())
        self.inf1100_looong.end_time = datetime.now() - timedelta(10)
        self.inf1100_looong.save()
        self.assertEquals(4, AssignmentGroup.old_where_is_candidate(self.student1).count())
        
    def test_where_is_examiner(self):
        self.assertEquals(8, AssignmentGroup.where_is_examiner(self.examiner2).count())
        self.assertEquals(5, AssignmentGroup.where_is_examiner(self.examiner3).count())
        self.inf1100_looong_assignment1_g2.examiners.add(self.examiner3)
        self.assertEquals(6, AssignmentGroup.where_is_examiner(self.examiner3).count())

    def test_published_where_is_examiner(self):
        self.assertEquals(8, AssignmentGroup.published_where_is_examiner(self.examiner2).count())
        self.assertEquals(8, AssignmentGroup.published_where_is_examiner(self.examiner1).count())
        self.assertEquals(0, AssignmentGroup.published_where_is_examiner(self.examiner1,
                    old=False, active=False).count())
        self.assertEquals(4, AssignmentGroup.published_where_is_examiner(self.examiner1,
                    old=True, active=False).count())
        self.assertEquals(4, AssignmentGroup.published_where_is_examiner(self.examiner1,
                    old=False, active=True).count())
        
    def test_active_where_is_examiner(self):
        self.assertEquals(4, AssignmentGroup.active_where_is_examiner(self.examiner1).count())
        self.assertEquals(2, AssignmentGroup.active_where_is_examiner(self.examiner3).count())

    def test_old_where_is_examiner(self):
        self.assertEquals(4, AssignmentGroup.old_where_is_examiner(self.examiner1).count())
        self.assertEquals(3, AssignmentGroup.old_where_is_examiner(self.examiner3).count())

    def test_get_students(self):
        self.assertEquals('student1', self.inf1100_looong_assignment1_g1.get_students())
        self.assertEquals('student3, student2', self.inf1100_looong_assignment1_g3.get_students())
        
    def test_get_candidates(self):
        self.assertEquals('student3, student2', self.inf1100_looong_assignment1_g3.get_candidates())
        self.inf1100_looong_assignment1.anonymous = True
        self.inf1100_looong_assignment1.save()
        #self.assertEquals('candidate-id missing, candidate-id missing',
        #                   self.inf1100_looong_assignment1_g3.get_candidates())
        cands = self.inf1100_looong_assignment1_g3.candidates.all()
        cand0 = cands[0]
        cand0.candidate_id = "2"
        cand0.update_identifier(True)
        cand0.save()
        cand1 = cands[1]
        cand1.candidate_id = "5"
        cand1.update_identifier(True)
        cand1.save()
        ag = AssignmentGroup.objects.get(id=self.inf1100_looong_assignment1_g3.id)
        self.assertEquals('2, 5', ag.get_candidates())

    def test_get_examiners(self):
        self.assertEquals('examiner1, examiner2, examiner3', self.inf1100_looong_assignment1_g3.get_examiners())

    def test_is_admin(self):
        self.assertFalse(self.inf1100_looong_assignment1_g3.is_admin(self.student1))
        self.assertFalse(self.inf1100_looong_assignment1_g3.is_admin(self.examiner1))
        self.assertTrue(self.inf1100_looong_assignment1_g3.is_admin(self.teacher1))
        self.assertTrue(self.inf1100_looong_assignment1_g3.is_admin(self.uioadmin))
        
    def test_is_examiner(self):
        self.assertTrue(self.inf1100_looong_assignment1_g1.is_examiner(self.examiner1))
        self.assertFalse(self.inf1100_looong_assignment1_g1.is_examiner(self.examiner2))

    def test_is_candidate(self):
        self.assertTrue(self.inf1100_looong_assignment1_g1.is_candidate(self.student1))
        self.assertFalse(self.inf1100_looong_assignment1_g1.is_candidate(self.student2))

    def test_clean_deadline_after_endtime(self):
        assignment_group = self.inf1100_looong_assignment1_g1
        assignment = assignment_group.parentnode
        assignment.parentnode.start_time = datetime(2010, 1, 1)
        assignment.parentnode.end_time = datetime(2011, 1, 1)
        assignment.publishing_time = datetime(2010, 1, 2)
        deadline = assignment_group.deadlines.create(deadline=datetime(2010, 5, 5), text=None)
        deadline.clean()
        deadline = assignment_group.deadlines.create(deadline=datetime(2012, 1, 1), text=None)
        self.assertRaises(ValidationError, deadline.clean)

    def test_clean_deadline_before_publishing_time(self):
        future3 = datetime.now() + timedelta(3)
        future6 = datetime.now() + timedelta(6)
        assignment_group = self.inf1100_looong_assignment1_g1
        oblig1 = assignment_group.parentnode
        oblig1.publishing_time = datetime.now()
        oblig1.parentnode.end_time = future6
        deadline = assignment_group.deadlines.create(deadline=future3, text=None)
        deadline.clean()
        oblig1.publishing_time = future6
        deadline = assignment_group.deadlines.create(deadline=future3, text=None)
        self.assertRaises(ValidationError, deadline.clean)

    def add_delivery(self, assignmentgroup, user):
        assignmentgroup.deliveries.create(delivered_by=user,
                                          successful=True)

    def test_etag_update(self):
        etag = datetime.now()
        obj = self.inf1100_looong_assignment1_g1
        obj.is_open = False
        self.assertRaises(EtagMismatchException, obj.etag_update, etag)
        try:
            obj.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            obj.etag_update(e.etag)
        obj2 = AssignmentGroup.objects.get(id=obj.id)
        self.assertFalse(obj2.is_open)

#    def test_status_one_deadline(self):
#        teacher1 = User.objects.get(username='teacher1')
#        student1 = User.objects.get(username='student1')
#        ag = AssignmentGroup(parentnode=Assignment.objects.get(id=1))
#
#        ag.save()
#        self.assertEquals(ag.status, AssignmentGroup.NO_DELIVERIES)
#        self.assertEquals(ag.get_localized_status(), "No deliveries")
#        self.assertEquals(ag.get_localized_student_status(), "No deliveries")
#
#        # 'cheat' by setting default deadline time to epoch
#        head_deadline = ag.deadlines.all()[0]
#        head_deadline.deadline = datetime(1970, 1, 1, 1, 0)
#        head_deadline.save()
#
#        # Adding delivery on head deadline
#        self.add_delivery(ag, student1)
#        self.assertEquals(ag.status, AssignmentGroup.HAS_DELIVERIES)
#        self.assertEquals(ag.get_localized_status(), "Has deliveries")
#        self.assertEquals(ag.get_localized_student_status(), "Has deliveries")
#
#        time_now = datetime.now()
#        deadline_5min = (time_now - timedelta(minutes=5))
#        ag.deadlines.create(deadline=deadline_5min, text=None)
#        # Adding delivery 5 minutes too late
#        self.add_delivery(ag, student1)
#
#        delivery1 = ag.deliveries.all()[1]
#        delivery2 = ag.deliveries.all()[0]
#
#        self.assertEquals(ag.deliveries.all().count(), 2)
#        # First delivery is not after deadline even though the deadline was set
#        # to 1970. That is because it's the head deadline.
#        self.assertFalse(delivery1.after_deadline)
#        # Second delivery delivered too late
#        self.assertTrue(delivery2.after_deadline)
#        # Status not corrected
#        self.assertEquals(delivery2.get_status_number(), Delivery.NOT_CORRECTED)
#
#        delivery2.feedbacks.create(rendered_view="", grade="ok", points=1,
#                                   is_passing_grade=True, saved_by=teacher1)
#        delivery2.save()
#        self.assertEquals(delivery2.get_status_number(), Delivery.CORRECTED_AND_PUBLISHED)
#
#        # Update cache on assignment group
#        ag = delivery2.assignment_group
#        self.assertEquals(ag.status, AssignmentGroup.CORRECTED_AND_PUBLISHED)
#        self.assertEquals(ag.get_localized_status(), "Corrected and published")
#        self.assertEquals(ag.get_localized_student_status(), "Has deliveries")
#
#        # Test publishing feedback
#        delivery2.feedback.published = True
#        delivery2.feedback.save()
#        ag = delivery2.assignment_group
#        
#        self.assertEquals(delivery2.get_status_number(), Delivery.CORRECTED_AND_PUBLISHED)
#        self.assertEquals(ag.status, AssignmentGroup.CORRECTED_AND_PUBLISHED)
#        self.assertEquals(ag.get_localized_status(), "Corrected and published")
#        self.assertEquals(ag.get_localized_student_status(), "Corrected")
#        
#    def test_status_multiple_deadlines(self):
#        teacher1 = User.objects.get(username='teacher1')
#        student1 = User.objects.get(username='student1')
#        ag = AssignmentGroup(parentnode=Assignment.objects.get(id=1))
#        ag.save()
#
#        self.assertEquals(ag.status, AssignmentGroup.NO_DELIVERIES)
#        self.assertEquals(ag.get_localized_status(), "No deliveries")
#        self.assertEquals(ag.get_localized_student_status(), "No deliveries")
#
#        # 'cheat' by setting default deadline time to epoch
#        head_deadline = ag.deadlines.all()[0]
#        head_deadline.deadline = datetime(1970, 1, 1, 1, 0)
#        head_deadline.save()
#        
#        time_now = datetime.now()
#        time_min10 = (time_now - timedelta(minutes=10))
#        ag.deadlines.create(deadline=time_min10, text=None)
#        time_min5 = (time_now - timedelta(minutes=5))
#        ag.deadlines.create(deadline=time_min5, text=None)
#        time_plus5 = (time_now + timedelta(minutes=5))
#        ag.deadlines.create(deadline=time_plus5, text=None)
#        time_plus10 = (time_now + timedelta(minutes=10))
#        ag.deadlines.create(deadline=time_plus10, text=None)
#
#        # Adding delivery on deadline 
#        self.add_delivery(ag, student1)
#        self.add_delivery(ag, student1)
#        delivery1 = ag.deliveries.all()[1]
#        delivery2 = ag.deliveries.all()[0]
#
#        deadline_min10 = Deadline.objects.get(deadline=time_min10)
#        deadline_min5 = Deadline.objects.get(deadline=time_min5)
#        deadline_plus5 = Deadline.objects.get(deadline=time_plus5)
#        deadline_plus10 = Deadline.objects.get(deadline=time_plus10)
#        
#        # Was assigned the correct deadline
#        self.assertEquals(delivery1.deadline.id, deadline_plus5.id)
#        self.assertEquals(delivery2.deadline.id, deadline_plus5.id)
#        
#        self.assertEquals(deadline_min10.status, AssignmentGroup.NO_DELIVERIES)
#        self.assertEquals(deadline_min5.status, AssignmentGroup.NO_DELIVERIES)
#        self.assertEquals(deadline_plus5.status, AssignmentGroup.HAS_DELIVERIES)
#        self.assertEquals(deadline_plus10.status, AssignmentGroup.NO_DELIVERIES)
#
#        deadline_plus5.deliveries_available_before_deadline = True
#        deadline_plus5.save()
#        ag = delivery1.assignment_group
#
#        self.add_delivery(ag, student1)
#        deadline_plus5 = Deadline.objects.get(deadline=time_plus5)
#        self.assertEquals(deadline_plus5.status, AssignmentGroup.HAS_DELIVERIES)
