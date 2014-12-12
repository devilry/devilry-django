from django.core.urlresolvers import reverse
from django.test import TestCase

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists
from devilry_gradingsystemplugin_points.devilry_plugin import PointsPluginApi


class TestFeedbackEditorView(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        self.assignment1builder.assignment.setup_grading(
            grading_system_plugin_id=PointsPluginApi.id,
            points_to_grade_mapper='raw-points',
            passing_grade_min_points=20,
            max_points=100)
        self.assignment1builder.assignment.save()
        self.deliverybuilder = self.assignment1builder.add_group(examiners=[self.examiner1])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        pluginapi = PointsPluginApi(self.assignment1builder.assignment)
        self.url = pluginapi.get_edit_feedback_url(self.deliverybuilder.delivery.id)

    def _login(self, user):
        self.client.login(username=user.username, password='test')

    def _get_as(self, user):
        self._login(user)
        return self.client.get(self.url)

    def _post_as(self, user, *args, **kwargs):
        self._login(user)
        return self.client.post(self.url, *args, **kwargs)

    def test_get_not_examiner_404(self):
        nobody = UserBuilder('nobody').user
        response = self._get_as(nobody)
        self.assertEquals(response.status_code, 404)

    def test_render(self):
        response = self._get_as(self.examiner1)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertTrue(cssExists(html, '#id_points'))

    def test_post_draft_valid_value_creates_draft_but_not_staticfeedback(self):
        delivery = self.deliverybuilder.delivery
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        response = self._post_as(self.examiner1, {
            'points': '20'
        })
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)

    def test_post_publish_creates_draft_and_staticfeedback(self):
        delivery = self.deliverybuilder.delivery
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        response = self._post_as(self.examiner1, {
            'points': '20',
            'submit_publish': 'publish'
        })
        self.assertEquals(delivery.feedbacks.count(), 1)
        html = response.content
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)

    def test_post_draft_over_max_points(self):
        delivery = self.deliverybuilder.delivery
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        response = self._post_as(self.examiner1, {
            'points': '200'
        })
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        self.assertIn('Ensure this value is less than or equal to 100', response.content)

    def test_post_draft_redirect_back_to_self(self):
        response = self._post_as(self.examiner1, {'points': '20'})
        self.assertTrue(response['Location'].endswith(self.url))

    def test_post_publish_redirect_to_successurl(self):
        response = self._post_as(self.examiner1, {'points': '20', 'submit_publish': 'publish'})
        successurl = reverse('devilry_examiner_singledeliveryview',
            kwargs={'deliveryid': self.deliverybuilder.delivery.id})
        self.assertTrue(response['Location'].endswith(successurl))