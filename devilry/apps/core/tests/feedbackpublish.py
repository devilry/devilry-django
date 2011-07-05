from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Delivery, Deadline

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
