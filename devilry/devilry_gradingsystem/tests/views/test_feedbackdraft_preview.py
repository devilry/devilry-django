from django.core.urlresolvers import reverse
from django.test import TestCase
import htmls

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.devilry_gradingsystem.models import FeedbackDraft


class TestFeedbackDraftPreviewView(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.deliverybuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            points_to_grade_mapper='raw-points',
                            passing_grade_min_points=20,
                            max_points=100) \
            .add_group(examiners=[self.examiner1])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)

    def _login(self, user):
        self.client.login(username=user.username, password='test')

    def _get_as(self, user, draftid):
        self._login(user)
        return self.client.get(reverse('devilry_gradingsystem_feedbackdraft_preview', kwargs={
            'deliveryid': self.deliverybuilder.delivery.id,
            'draftid': draftid
        }))

    def test_get_not_examiner_404(self):
        nobody = UserBuilder('nobody').user
        response = self._get_as(nobody, 1)
        self.assertEquals(response.status_code, 404)

    def test_get_draft_not_found_404(self):
        response = self._get_as(self.examiner1, 1)
        self.assertEquals(response.status_code, 404)

    def test_render(self):
        draft = FeedbackDraft.objects.create(
            points=40,
            delivery=self.deliverybuilder.delivery,
            saved_by=self.examiner1,
            feedbacktext_html='This is a test.'
        )
        response = self._get_as(self.examiner1, draft.id)
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('.read-feedback-box'))
        self.assertEquals(
            selector.one('.read-feedback-box .feedback_gradebox .feedback_grade').alltext_normalized,
            '40/100')
        self.assertEquals(
            selector.one('.read-feedback-box .feedback_gradebox .feedback_is_passing_grade').alltext_normalized,
            'passed')
        self.assertIn(
            'django-cradmin-container-fluid-focus-success',
            selector.one('.read-feedback-box .feedback_gradebox')['class'])
        self.assertEquals(
            selector.one('.read-feedback-box .devilry-feedback-rendered-view').alltext_normalized,
            'This is a test.')
