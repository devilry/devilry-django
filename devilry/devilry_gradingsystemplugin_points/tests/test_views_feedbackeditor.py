from django.core.urlresolvers import reverse

from django.test import TestCase
import htmls

from devilry.devilry_gradingsystem.tests.helpers import FeedbackEditorViewTestMixin
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder

from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.devilry_gradingsystemplugin_points.devilry_plugin import PointsPluginApi


class TestFeedbackEditorView(TestCase, FeedbackEditorViewTestMixin):
    def get_valid_post_data_without_feedbackfile_or_feedbacktext(self):
        return {'points': '1'}

    def get_empty_delivery_with_testexaminer_as_examiner(self):
        return self.deliverybuilder.delivery

    def get_testexaminer(self):
        return self.examiner1

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

    def test_get_not_examiner_404(self):
        nobody = UserBuilder('nobody').user
        response = self.get_as(nobody)
        self.assertEquals(response.status_code, 404)

    def test_render(self):
        response = self.get_as(self.examiner1)
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#id_points'))
        self.assertTrue(selector.exists('input#id_feedbackfile'))

    def test_post_draft_valid_value_creates_draft_but_not_staticfeedback(self):
        delivery = self.deliverybuilder.delivery
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        response = self.post_as(self.examiner1, {
            'points': '20'
        })
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)

    def test_post_publish_creates_draft_and_staticfeedback(self):
        delivery = self.deliverybuilder.delivery
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        response = self.post_as(self.examiner1, {
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
        response = self.post_as(self.examiner1, {
            'points': '200'
        })
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        self.assertIn('Ensure this value is less than or equal to 100', response.content)

    def test_post_draft_redirect_back_to_self(self):
        response = self.post_as(self.examiner1, {'points': '20'})
        self.assertTrue(response['Location'].endswith(self.url))

    def test_post_publish_redirect_to_successurl(self):
        response = self.post_as(self.examiner1, {'points': '20', 'submit_publish': 'publish'})
        successurl = reverse('devilry_examiner_singledeliveryview',
                             kwargs={'deliveryid': self.deliverybuilder.delivery.id})
        self.assertTrue(response['Location'].endswith(successurl))
