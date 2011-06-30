from django.test import TestCase
from django.contrib.auth.models import User

from ..models import StaticFeedback

# TODO: StaticFeedback tests
class TestFeedback(TestCase):

    # fixtures = ['core/deprecated_users.json', 'core/core.json']
    # using the 'new' test-data, since the 'old' data doesn't have
    # feedbacks inserted
    fixtures = ['simplified/data.json']

    def setUp(self):
        self.candidate0 = User.objects.get(username='student0')
        self.candidate1 = User.objects.get(username='student1')

    def test_published_where_is_candidate(self):
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.candidate0).count(), 8)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.candidate1).count(), 7)
        
    def test_published_where_is_examiner(self):
        examiner0 = User.objects.get(username='examiner0')
        examiner0_feedbacks = StaticFeedback.published_where_is_examiner(examiner0)
        self.assertEquals(len(examiner0_feedbacks), 15)
