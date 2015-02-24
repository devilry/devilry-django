from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase
import htmls
from devilry.apps.core.models import StaticFeedback

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.devilry_gradingsystem.models import FeedbackDraft, FeedbackDraftFile


class TestFeedbackDraftPreviewView(TestCase):
    def setUp(self):
        self.testexaminer = UserBuilder('testexaminer').user
        self.deliverybuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            points_to_grade_mapper='raw-points',
                            passing_grade_min_points=20,
                            max_points=100) \
            .add_group(examiners=[self.testexaminer])\
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

    def _post_as(self, user, draftid, data=None):
        self._login(user)
        url = reverse('devilry_gradingsystem_feedbackdraft_preview', kwargs={
            'deliveryid': self.deliverybuilder.delivery.id,
            'draftid': draftid
        })
        return self.client.post(url, data=data)

    def test_get_not_examiner_404(self):
        nobody = UserBuilder('nobody').user
        response = self._get_as(nobody, 1)
        self.assertEquals(response.status_code, 404)

    def test_get_draft_not_found_404(self):
        response = self._get_as(self.testexaminer, 1)
        self.assertEquals(response.status_code, 404)

    def test_render(self):
        draft = FeedbackDraft.objects.create(
            points=40,
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            feedbacktext_html='This is a test.'
        )
        response = self._get_as(self.testexaminer, draft.id)
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
        self.assertFalse(selector.exists('ul.devilry-feedback-rendered-view-files'))

    def test_render_with_draftfile(self):
        draft = FeedbackDraft.objects.create(
            points=40,
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            feedbacktext_html='This is a test.'
        )
        draftfile = FeedbackDraftFile(
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            filename='test.txt')
        draftfile.file.save('test.txt', ContentFile('Test'))

        response = self._get_as(self.testexaminer, draft.id)
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('ul.devilry-feedback-rendered-view-files'))
        self.assertEqual(selector.count('ul.devilry-feedback-rendered-view-files li'), 1)
        self.assertEqual(
            selector.one('ul.devilry-feedback-rendered-view-files li').alltext_normalized,
            'test.txt')

    def test_post(self):
        draft = FeedbackDraft.objects.create(
            points=40,
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            feedbacktext_html='<p>This is a test.</p>'
        )

        self.assertEquals(StaticFeedback.objects.count(), 0)
        response = self._post_as(self.testexaminer, draft.id, {
            'submit_publish': 'yes'
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(StaticFeedback.objects.count(), 1)
        staticfeedback = StaticFeedback.objects.first()
        self.assertEquals(staticfeedback.delivery, self.deliverybuilder.delivery)
        self.assertEquals(staticfeedback.points, 40)
        self.assertEquals(staticfeedback.saved_by, self.testexaminer)
        self.assertEquals(staticfeedback.rendered_view, '<p>This is a test.</p>')

    def test_post_with_draftfile(self):
        draft = FeedbackDraft.objects.create(
            points=40,
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            feedbacktext_html=''
        )
        draftfile = FeedbackDraftFile(
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            filename='test.txt')
        draftfile.file.save('test.txt', ContentFile('Test'))

        self.assertEquals(StaticFeedback.objects.count(), 0)
        response = self._post_as(self.testexaminer, draft.id, {
            'submit_publish': 'yes'
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(StaticFeedback.objects.count(), 1)
        staticfeedback = StaticFeedback.objects.first()
        self.assertEqual(staticfeedback.files.count(), 1)
        fileattachment = staticfeedback.files.first()
        self.assertEqual(fileattachment.filename, 'test.txt')
        self.assertEqual(fileattachment.file.read(), 'Test')
