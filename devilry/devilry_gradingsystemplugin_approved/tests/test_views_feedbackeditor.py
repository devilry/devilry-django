from django.core.urlresolvers import reverse
from django.test import TestCase
from devilry.devilry_gradingsystem.tests.helpers import FeedbackEditorViewTestMixin

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssExists
from devilry.devilry_gradingsystemplugin_approved.devilry_plugin import ApprovedPluginApi


class TestFeedbackEditorView(TestCase, FeedbackEditorViewTestMixin):
    def get_valid_post_data_without_feedbackfile_or_feedbacktext(self):
        return {'points': 'on'}

    def get_empty_delivery_with_testexaminer_as_examiner(self):
        return self.deliverybuilder.delivery

    def get_testexaminer(self):
        return self.examiner1

    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        self.assignment1builder.assignment.setup_grading(
            grading_system_plugin_id=ApprovedPluginApi.id,
            points_to_grade_mapper='passed-failed',
            passing_grade_min_points=1,
            max_points=1)
        self.assignment1builder.assignment.save()
        self.deliverybuilder = self.assignment1builder.add_group(examiners=[self.examiner1])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        pluginapi = ApprovedPluginApi(self.assignment1builder.assignment)
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
            'points': 'on'
        })
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)

    def test_post_publish_creates_draft_and_staticfeedback(self):
        delivery = self.deliverybuilder.delivery
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        response = self._post_as(self.examiner1, {
            'points': 'on',
            'submit_publish': 'publish'
        })
        self.assertEquals(delivery.feedbacks.count(), 1)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)

    def test_post_draft_redirect_back_to_self(self):
        response = self._post_as(self.examiner1, {'points': 'on'})
        self.assertTrue(response['Location'].endswith(self.url))

    def test_post_publish_redirect_to_successurl(self):
        response = self._post_as(self.examiner1, {'points': 'on', 'submit_publish': 'publish'})
        successurl = reverse('devilry_examiner_singledeliveryview',
                             kwargs={'deliveryid': self.deliverybuilder.delivery.id})
        self.assertTrue(response['Location'].endswith(successurl))


class TestFeedbackBulkEditorView(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        self.assignment1builder.assignment.setup_grading(
            grading_system_plugin_id=ApprovedPluginApi.id,
            points_to_grade_mapper='passed-failed',
            passing_grade_min_points=1,
            max_points=1)
        self.assignment1builder.assignment.save()
        pluginapi = ApprovedPluginApi(self.assignment1builder.assignment)
        self.url = pluginapi.get_bulkedit_feedback_url(self.assignment1builder.assignment.id)

    def _login(self, user):
        self.client.login(username=user.username, password='test')

    def _get_as(self, user, *args, **kwargs):
        self._login(user)
        return self.client.get(self.url, *args, **kwargs)

    def _post_as(self, user, *args, **kwargs):
        self._login(user)
        return self.client.post(self.url, *args, **kwargs)

    def test_get_not_examiner_404(self):
        groupbuilder = self.assignment1builder.add_group()
        nobody = UserBuilder('nobody').user
        response = self._post_as(nobody, {
            'group_ids': groupbuilder.group.id
        })
        self.assertEquals(response.status_code, 404)

    def test_no_group_ids_shows_errormessage(self):
        self.assignment1builder.add_group(examiners=[self.examiner1])
        response = self._post_as(self.examiner1)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertIn('You have to select at least one group to perform a bulk action.', html)

    def test_no_delivery_shows_errormessage(self):
        groupbuilder = self.assignment1builder.add_group(examiners=[self.examiner1])
        response = self._post_as(self.examiner1, {
            'group_ids': groupbuilder.group.id
        })
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertIn('One or more of the selected groups has no deliveries.', html)

    def test_render(self):
        groupbuilder = self.assignment1builder.add_group(examiners=[self.examiner1])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        response = self._post_as(self.examiner1, {
            'group_ids': groupbuilder.group.id
        })
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertTrue(cssExists(html, '#id_points'))

    def test_post_publish_creates_draft_and_staticfeedback(self):
        groupbuilder = self.assignment1builder.add_group(examiners=[self.examiner1])
        deliverybuilder = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)

        self.assertEquals(deliverybuilder.delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        self.assertEquals(deliverybuilder.delivery.feedbacks.count(), 0)

        response = self._post_as(self.examiner1, {
            'group_ids': groupbuilder.group.id,
            'points': 'on',
            'submit_publish': 'i18nlabel'
        })
        html = response.content
        self.assertEquals(response.status_code, 302)
        deliverybuilder.reload_from_db()
        self.assertEquals(deliverybuilder.delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEquals(deliverybuilder.delivery.feedbacks.count(), 1)
        self.assertEquals(deliverybuilder.delivery.last_feedback.is_passing_grade, True)
        self.assertEquals(deliverybuilder.delivery.last_feedback.points, 1)

    def test_post_preview_creates_draft_and_NOT_staticfeedback(self):
        groupbuilder = self.assignment1builder.add_group(examiners=[self.examiner1])
        deliverybuilder = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)

        self.assertEquals(deliverybuilder.delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)
        self.assertEquals(deliverybuilder.delivery.feedbacks.count(), 0)

        response = self._post_as(self.examiner1, {
            'group_ids': groupbuilder.group.id,
            'points': 'on',
            'submit_preview': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        deliverybuilder.reload_from_db()
        self.assertEquals(deliverybuilder.delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEquals(deliverybuilder.delivery.feedbacks.count(), 0)
