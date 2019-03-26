import unittest

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
import htmls

from devilry.apps.core.models import StaticFeedback
from devilry.apps.core.templatetags.devilry_core_tags import devilry_user_displayname
from devilry.devilry_gradingsystem.models import FeedbackDraftFile, FeedbackDraft
from devilry.project.develop.testhelpers.corebuilder import UserBuilder


class FeedbackEditorViewTestMixin(object):
    """
    Mixin class that makes it easier to test the FeedbackEditorView
    that each gradingsystem plugin must implement.
    """
    def login(self, user):
        self.client.login(username=user.shortname, password='test')

    def get_as(self, user):
        self.login(user)
        return self.client.get(self.url)

    def post_as(self, user, *args, **kwargs):
        self.login(user)
        return self.client.post(self.url, *args, **kwargs)

    def get_valid_post_data_without_feedbackfile_or_feedbacktext(self):
        """
        Must return a valid POST data dict with the plugin specific
        data (not feedbackfile, and not feedbacktext).
        """
        raise NotImplementedError()

    def get_empty_delivery_with_testexaminer_as_examiner(self):
        """
        Must return a delivery with no feedback. The user
        returned by :meth:`.get_testexaminer` must be
        registered as examiner on the group owning the delivery.
        """
        raise NotImplementedError()

    def get_testexaminer(self):
        """
        See :meth:`.get_empty_delivery_with_testexaminer_as_examiner`.
        """
        raise NotImplementedError()

    def test_get_render_no_feedback_draft(self):
        response = self.get_as(self.get_testexaminer())
        self.assertEqual(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEqual(selector.one('#id_feedbacktext').alltext_normalized, '')
        self.assertFalse(selector.exists('#cradmin_legacy_messages'))

    @unittest.skip('Must be updated to used django cradmin')
    def test_get_render_has_feedback_draft(self):
        FeedbackDraft.objects.create(
            delivery=self.get_empty_delivery_with_testexaminer_as_examiner(),
            feedbacktext_raw='Test feedback',
            points=30,
            saved_by=self.get_testexaminer())
        response = self.get_as(self.get_testexaminer())
        selector = htmls.S(response.content)
        self.assertEqual(selector.one('#id_feedbacktext').alltext_normalized, 'Test feedback')
        self.assertIn(
            'Loaded draft saved',
            selector.one('#cradmin_legacy_messages .alert-info').alltext_normalized)
        self.assertIn(
            devilry_user_displayname(self.get_testexaminer()),
            selector.one('#cradmin_legacy_messages .alert-info').alltext_normalized)

    def test_get_render_other_examiner_has_feedback_draft_no_draft_sharing(self):
        FeedbackDraft.objects.create(
            delivery=self.get_empty_delivery_with_testexaminer_as_examiner(),
            feedbacktext_raw='Test feedback',
            points=30,
            saved_by=UserBuilder('someotheruser').user)
        response = self.get_as(self.get_testexaminer())
        selector = htmls.S(response.content)
        self.assertEqual(selector.one('#id_feedbacktext').alltext_normalized, '')

    def test_get_render_other_examiner_has_feedback_draft_draft_sharing(self):
        testdelivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        assignment = testdelivery.assignment
        assignment.feedback_workflow = 'trusted-cooperative-feedback-editing'
        assignment.save()
        FeedbackDraft.objects.create(
            delivery=testdelivery,
            feedbacktext_raw='Test feedback',
            points=30,
            saved_by=UserBuilder('someotheruser').user)
        response = self.get_as(self.get_testexaminer())
        selector = htmls.S(response.content)
        self.assertEqual(selector.one('#id_feedbacktext').alltext_normalized, 'Test feedback')

    def test_get_render_workflow_default(self):
        response = self.get_as(self.get_testexaminer())
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('button[name=submit_save_draft]'))
        self.assertFalse(selector.exists('button[name=submit_save_and_exit]'))
        self.assertTrue(selector.exists('button[name=submit_preview]'))
        self.assertTrue(selector.exists('button[name=submit_publish]'))

    def test_get_render_workflow_trusted_cooperative_feedback_editing(self):
        testdelivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        assignment = testdelivery.assignment
        assignment.feedback_workflow = 'trusted-cooperative-feedback-editing'
        assignment.save()
        response = self.get_as(self.get_testexaminer())
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('button[name=submit_save_draft]'))
        self.assertTrue(selector.exists('button[name=submit_save_and_exit]'))
        self.assertFalse(selector.exists('button[name=submit_preview]'))
        self.assertFalse(selector.exists('button[name=submit_publish]'))

    def test_post_publish_403_if_workflow_does_not_allow_publish(self):
        testdelivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        assignment = testdelivery.assignment
        assignment.feedback_workflow = 'trusted-cooperative-feedback-editing'
        assignment.save()
        testexaminer = self.get_testexaminer()
        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['submit_publish'] = 'publish'
        response = self.post_as(testexaminer, postdata)
        self.assertEqual(response.status_code, 403)

    def test_post_with_feedbackfile_no_existing_file(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        self.assertEqual(delivery.feedbacks.count(), 0)
        self.assertEqual(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = SimpleUploadedFile('testfile.txt', 'Feedback file test')
        self.post_as(testexaminer, postdata)

        self.assertEqual(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEqual(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 1)
        feedbackdraftfile = FeedbackDraftFile.objects.get(delivery=delivery)
        self.assertEqual(feedbackdraftfile.filename, 'testfile.txt')
        self.assertEqual(feedbackdraftfile.file.read(), 'Feedback file test')

    def test_post_with_feedbackfile_has_existing_file(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        feedbackdraftfile = FeedbackDraftFile(delivery=delivery, saved_by=testexaminer, filename='oldtestfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Oldfile'))

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = SimpleUploadedFile('testfile.txt', 'Feedback file test')
        self.post_as(testexaminer, postdata)

        self.assertEqual(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEqual(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 1)
        feedbackdraftfile = FeedbackDraftFile.objects.get(delivery=delivery)
        self.assertEqual(feedbackdraftfile.filename, 'testfile.txt')
        self.assertEqual(feedbackdraftfile.file.read(), 'Feedback file test')

    def test_post_remove_feedbackfile(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        feedbackdraftfile = FeedbackDraftFile(delivery=delivery, saved_by=testexaminer, filename='oldtestfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Oldfile'))

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = ''
        postdata['feedbackfile-clear'] = 'on'
        self.post_as(testexaminer, postdata)

        self.assertEqual(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEqual(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 0)

    def test_post_update_draft_without_changing_feedbackfile(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        feedbackdraftfile = FeedbackDraftFile(delivery=delivery, saved_by=testexaminer, filename='testfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Feedback file test'))

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = ''
        self.post_as(testexaminer, postdata)

        self.assertEqual(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEqual(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 1)
        feedbackdraftfile = FeedbackDraftFile.objects.get(delivery=delivery)
        self.assertEqual(feedbackdraftfile.filename, 'testfile.txt')
        self.assertEqual(feedbackdraftfile.file.read(), 'Feedback file test')

    def test_post_with_feedbackfile_is_private(self):
        testexaminer = self.get_testexaminer()
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        feedbackdraftfile = FeedbackDraftFile(
            delivery=delivery,
            saved_by=UserBuilder('otheruser').user,
            filename='otherfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Other'))

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = SimpleUploadedFile('testfile.txt', 'Feedback file test')
        self.assertEqual(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 1)
        self.post_as(testexaminer, postdata)
        self.assertEqual(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 2)
        self.assertEqual(FeedbackDraftFile.objects.filter(delivery=delivery, saved_by=testexaminer).count(), 1)

    def test_post_publish_with_feedbackfile(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        feedbackdraftfile = FeedbackDraftFile(delivery=delivery, saved_by=testexaminer, filename='testfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Feedback file test'))
        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['submit_publish'] = 'yes'

        self.assertEqual(StaticFeedback.objects.count(), 0)
        self.post_as(testexaminer, postdata)
        self.assertEqual(StaticFeedback.objects.count(), 1)
        staticfeedback = StaticFeedback.objects.get(delivery=delivery)
        self.assertEqual(staticfeedback.files.count(), 1)
        fileattachment = staticfeedback.files.first()
        self.assertEqual(fileattachment.filename, 'testfile.txt')
        self.assertEqual(fileattachment.file.read(), 'Feedback file test')
