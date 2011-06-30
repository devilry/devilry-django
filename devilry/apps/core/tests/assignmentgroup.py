from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from ..models import Assignment, AssignmentGroup, Delivery, Deadline

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
