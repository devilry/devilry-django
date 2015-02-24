from django.test import TestCase
from django.core.urlresolvers import reverse
import htmls
from devilry.apps.core.models import Delivery

from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.corebuilder import DeliveryBuilder
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssExists
from devilry.project.develop.testhelpers.soupselect import normalize_whitespace
from devilry.devilry_examiner.tests.utils import isoformat_datetime
from devilry.devilry_examiner.tests.utils import DJANGO_ISODATETIMEFORMAT


class TestSingleDeliveryView(TestCase):
    def setUp(self):
        DeliveryBuilder.set_memory_deliverystore()
        self.examiner1 = UserBuilder('examiner1').user
        self.student1 = UserBuilder('student1', full_name="Student One").user
        self.duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        self.week1builder = self.duck1010builder.add_6month_active_period()\
            .add_assignment('week1', long_name='Week 1')

    def _getas(self, username, deliveryid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_singledeliveryview', kwargs={'deliveryid': deliveryid}),
                *args, **kwargs)

    def test_404_when_not_examiner(self):
        deliverybuilder = self.week1builder\
            .add_group(students=[self.student1])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        response = self._getas('examiner1', deliverybuilder.delivery.id)
        self.assertEquals(response.status_code, 404)

    def test_404_when_inactive(self):
        deliverybuilder = self.duck1010builder.add_6month_nextyear_period()\
            .add_assignment('week1')\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        response = self._getas('examiner1', deliverybuilder.delivery.id)
        self.assertEquals(response.status_code, 404)

    def test_header(self):
        deliverybuilder = self.week1builder\
            .add_group(students=[self.student1], examiners=[self.examiner1])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        with self.settings(DATETIME_FORMAT=DJANGO_ISODATETIMEFORMAT, USE_L10N=False):
            response = self._getas('examiner1', deliverybuilder.delivery.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
            'Week 1 &mdash; Student One')
        self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(),
            'Delivery 1/1-{}'.format(isoformat_datetime(deliverybuilder.delivery.time_of_delivery)))

    def test_after_deadline(self):
        delivery = self.week1builder\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_after_deadline(hours=1).delivery
        response = self._getas('examiner1', delivery.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(
            normalize_whitespace(cssGet(html, '.after_deadline_message').text),
            'This delivery was added 1 hour after the deadline.The group has no other deliveries for this deadline.')

    def test_after_deadline_other_deliveries(self):
        deadlinebuilder = self.week1builder\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)
        delivery1 = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=1).delivery
        delivery2 = deadlinebuilder.add_delivery_x_hours_after_deadline(hours=4).delivery
        response = self._getas('examiner1', delivery2.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(
            normalize_whitespace(cssGet(html, '.after_deadline_message').text),
            'This delivery was added 4 hours after the deadline.The group has made at least one more delivery for this deadline.Browse other deliveries.')


    def test_not_last_delivery_message_not_shown_on_last(self):
        delivery = self.week1builder\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1).delivery
        response = self._getas('examiner1', delivery.id)
        html = response.content
        self.assertFalse(cssExists(html, '.not_last_delivery_message'))

    def test_not_last_delivery_message(self):
        groupbuilder = self.week1builder.add_group(examiners=[self.examiner1])
        deadlinebuilder = groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        delivery1 = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=1).delivery
        deadlinebuilder.add_delivery_x_hours_after_deadline(hours=1)
        response = self._getas('examiner1', delivery1.id)

        groupbuilder.reload_from_db()
        html = response.content
        self.assertEquals(
            cssGet(html, '.not_last_delivery_message').text.strip(),
            'This delivery is not the last delivery made by this group on this assignment.Browse other deliveries.')

    def test_show_render_no_feedback(self):
        delivery = self.week1builder\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1).delivery
        response = self._getas('examiner1', delivery.id)
        html = response.content
        self.assertIsNone(delivery.last_feedback)
        self.assertFalse(cssExists(html, '.read-feedback-box'))
        self.assertTrue(cssExists(html, '.no-feedback-box'))
        self.assertEquals(cssGet(html, '.no-feedback-box').text.strip(),
            'Write feedbackNo feedback on this delivery.')

    def test_readonly_feedback_render(self):
        feedback = self.week1builder\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_feedback(
                points=10,
                grade='10/100',
                is_passing_grade=False,
                saved_by=UserBuilder('testuser').user,
                rendered_view='This is a test.'
            ).feedback
        response = self._getas('examiner1', feedback.delivery.id)
        html = response.content
        self.assertFalse(cssExists(html, '.no-feedback-box'))
        self.assertTrue(cssExists(html, '.read-feedback-box'))
        self.assertEquals(cssGet(html, '.read-feedback-box .feedback_gradebox .feedback_grade').text.strip(),
            '10/100')
        self.assertEquals(cssGet(html, '.read-feedback-box .feedback_gradebox .feedback_is_passing_grade').text.strip(),
            'failed')
        self.assertIn('django-cradmin-container-fluid-focus-warning',
                      cssGet(html, '.read-feedback-box .feedback_gradebox')['class'])
        self.assertEquals(cssGet(html, '.read-feedback-box #devilry_examiner_feedback_rendered_view').text.strip(),
            'This is a test.')

    def test_readonly_feedback_render_fileattachments(self):
        feedbackbuilder = self.week1builder\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_passed_A_feedback(saved_by=UserBuilder('testuser').user)
        feedbackbuilder.add_fileattachment(filename='testfile.txt')

        response = self._getas('examiner1', feedbackbuilder.feedback.delivery.id)
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('.read-feedback-box ul.devilry-feedback-rendered-view-files'))
        self.assertEqual(selector.count('.read-feedback-box ul.devilry-feedback-rendered-view-files li'), 1)
        self.assertEqual(
            selector.one('.read-feedback-box ul.devilry-feedback-rendered-view-files li').alltext_normalized,
            'testfile.txt')

    def test_filemeta_links_nofiles(self):
        deliverybuilder = self.week1builder\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        response = self._getas('examiner1', deliverybuilder.delivery.id)
        html = response.content
        self.assertFalse(cssExists(html, '.delivery_files'))

    def test_filemeta_links_single(self):
        deliverybuilder = self.week1builder\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        deliverybuilder.add_filemeta(filename='testfile.txt', data='test')
        response = self._getas('examiner1', deliverybuilder.delivery.id)
        html = response.content
        self.assertTrue(cssExists(html, '.delivery_files'))
        self.assertEquals(len(cssFind(html, '.delivery_files a')), 1)
        self.assertTrue(cssExists(html, '.delivery_files .btn'))
        self.assertEquals(cssGet(html, '.delivery_files a.btn').text.strip(),
            'testfile.txt')

    def test_filemeta_links_multi(self):
        deliverybuilder = self.week1builder\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        deliverybuilder.add_filemeta( filename='b.txt', data='test')
        deliverybuilder.add_filemeta(filename='a.txt', data='test')
        response = self._getas('examiner1', deliverybuilder.delivery.id)
        html = response.content
        self.assertTrue(cssExists(html, '.delivery_files'))
        self.assertEquals(len(cssFind(html, '.delivery_files a')), 3) # One for the "Download files"-button and one for each file
        self.assertTrue(cssExists(html, '.delivery_files .btn'))
        self.assertEquals(cssGet(html, '.delivery_files .btn').text.strip(),
            'Download files')
        filenames = map(lambda e: e.text.strip(), cssFind(html, '.delivery_files ul li'))
        self.assertEquals(filenames, ['a.txt', 'b.txt'])

    def test_give_another_chance(self):
        groupbuilder = self.week1builder\
            .add_group(students=[self.student1], examiners=[self.examiner1])
        deliverybuilder = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        deliverybuilder.add_failed_feedback(saved_by=UserBuilder('testuser').user)
        response = self._getas('examiner1', deliverybuilder.delivery.id)
        html = response.content

        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.feedback, deliverybuilder.delivery.last_feedback)
        self.assertEquals(groupbuilder.group.delivery_status, 'corrected')
        self.assertFalse(groupbuilder.group.feedback.is_passing_grade)
        self.assertTrue(cssExists(html, '.devilry_give_another_chance_box'))
        box = cssGet(html, '.devilry_give_another_chance_box')
        self.assertIn('The last feedback for this group is a failing grade.', box.text.strip())
        self.assertEquals(cssGet(html, '.devilry_give_another_chance_box form input[name=group_ids]')['value'],
            str(groupbuilder.group.id))
        self.assertEquals(cssGet(html, '.devilry_give_another_chance_box form input[name=give_another_chance]')['value'],
            'true')
        self.assertEquals(cssGet(html, '.devilry_give_another_chance_box form input[name=success_url]')['value'],
            reverse('devilry_examiner_singlegroupoverview', kwargs={'groupid': groupbuilder.group.id}))
        self.assertEquals(cssGet(html, '.devilry_give_another_chance_box form input[name=cancel_url]')['value'],
            reverse('devilry_examiner_singledeliveryview', kwargs={'deliveryid': deliverybuilder.delivery.id}))

    def test_give_another_chance_only_when_last_feedback(self):
        groupbuilder = self.week1builder.add_group(
            students=[self.student1], examiners=[self.examiner1])
        deadlinebuilder = groupbuilder.add_deadline_in_x_weeks(weeks=1)
        delivery1builder = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=2)
        delivery2builder = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=1)
        testuser = UserBuilder('testuser').user
        delivery2builder.add_failed_feedback(saved_by=testuser)
        delivery1builder.add_failed_feedback(saved_by=testuser)
        response = self._getas('examiner1', delivery2builder.delivery.id)
        html = response.content
        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.feedback, delivery1builder.delivery.last_feedback)
        self.assertFalse(cssExists(html, '.devilry_give_another_chance_box'))

    def test_give_another_chance_only_when_failed(self):
        groupbuilder = self.week1builder\
            .add_group(students=[self.student1], examiners=[self.examiner1])
        deliverybuilder = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        deliverybuilder.add_passed_feedback(saved_by=UserBuilder('testuser').user)
        response = self._getas('examiner1', deliverybuilder.delivery.id)
        html = response.content
        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.feedback, deliverybuilder.delivery.last_feedback)
        self.assertEquals(groupbuilder.group.delivery_status, 'corrected')
        self.assertTrue(groupbuilder.group.feedback.is_passing_grade)
        self.assertFalse(cssExists(html, '.devilry_give_another_chance_box'))
