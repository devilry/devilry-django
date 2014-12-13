from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.models import Deadline
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssExists
from devilry.devilry_examiner.tests.utils import isoformat_datetime


class TestAddDeadlineView(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', long_name='Assignment One')
        self.url = reverse('devilry_examiner_add_deadline', kwargs={
            'assignmentid': self.assignment1builder.assignment.id})

    def _getas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.get(self.url, *args, **kwargs)

    def _postas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.post(self.url, *args, **kwargs)


    ##############################
    # Security checks
    ##############################

    def test_post_200_when_examiner(self):
        group1 = self.assignment1builder\
            .add_group(examiners=[self.examiner1]).group
        response = self._postas(self.examiner1, {
            'group_ids': [group1.id]
        })
        self.assertEquals(response.status_code, 200)

    def test_post_404_when_not_examiner(self):
        group1 = self.assignment1builder\
            .add_group().group # Not adding any examiners.
        response = self._postas(self.examiner1, {
            'group_ids': [group1.id]
        })
        self.assertEquals(response.status_code, 404)

    def test_get_405(self):
        response = self._getas(self.examiner1)
        self.assertEquals(response.status_code, 405)


    #######################################
    # Initial rendering
    #######################################

    def test_render(self):
        group1 = self.assignment1builder\
            .add_group(examiners=[self.examiner1]).group
        response = self._postas(self.examiner1, {
            'group_ids': [group1.id]
        })
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
            'Add deadline')
        self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(),
            "Assignment One &mdash; duck1010, active")
        self.assertTrue(cssExists(html, 'input[name=success_url]'))
        self.assertTrue(cssExists(html, 'input[name=cancel_url]'))
        self.assertTrue(cssExists(html, 'input[name=group_ids]'))
        self.assertTrue(cssExists(html, 'input[name=why_created]'))
        self.assertTrue(cssExists(html, 'textarea[name=text]'))
        self.assertTrue(cssExists(html, 'input[name=no_text]'))
        self.assertTrue(cssExists(html, '[name=add_deadline_form]'))
        self.assertTrue(cssExists(html, '[name=submit_cancel]'))


    def test_give_another_chance_sets_initial_text(self):
        group1 = self.assignment1builder\
            .add_group(examiners=[self.examiner1]).group
        response = self._postas(self.examiner1, {
            'group_ids': [group1.id],
            'give_another_chance': 'on'
        })
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '#id_text').text.strip(),
            "I have given you a new chance to pass this assignment. Read your last feedback for information about why you did not pass, and why you have been given another chance.")
        self.assertEquals(cssGet(html, '#id_why_created')['value'],
            'examiner-gave-another-chance')
        self.assertEquals(cssGet(html, '#id_why_created')['type'], 'hidden')


    ##########################################
    # Form handling
    ##########################################

    def test_post_single(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'deadline': isoformat_datetime(deadline_datetime),
            'text': 'Hello world',
            'add_deadline_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline.deadline, deadline_datetime)
        self.assertEquals(group1builder.group.last_deadline.text, 'Hello world')
        self.assertEquals(group1builder.group.last_deadline.why_created, '')
        self.assertEquals(group1builder.group.last_deadline.added_by, self.examiner1)

    def test_post_multiple(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        group2builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id, group2builder.group.id],
            'deadline': isoformat_datetime(deadline_datetime),
            'text': 'Hello world',
            'add_deadline_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)

        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline.deadline, deadline_datetime)
        self.assertEquals(group1builder.group.last_deadline.text, 'Hello world')

        group2builder.reload_from_db()
        self.assertEquals(group2builder.group.last_deadline.deadline, deadline_datetime)
        self.assertEquals(group2builder.group.last_deadline.text, 'Hello world')


    def test_post_why_created(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'deadline': isoformat_datetime(deadline_datetime),
            'text': 'Hello world',
            'why_created': 'examiner-gave-another-chance',
            'add_deadline_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline.why_created, 'examiner-gave-another-chance')

    def test_post_no_text(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'deadline': isoformat_datetime(deadline_datetime),
            'add_deadline_form': 'i18nlabel',
            'no_text': 'on'
        })
        self.assertEquals(response.status_code, 302)
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline.deadline, deadline_datetime)
        self.assertEquals(group1builder.group.last_deadline.text, '')

    def test_post_no_text_checkbox_required(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'deadline': isoformat_datetime(deadline_datetime),
            'add_deadline_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 200)
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline, None)
        self.assertIn('You must specify an &quot;About this deadline&quot; message, or select that you do not want to specify a message.',
            response.content)

    def test_post_no_text_checked_and_text_provided(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'deadline': isoformat_datetime(deadline_datetime),
            'add_deadline_form': 'i18nlabel',
            'no_text': 'on',
            'text': 'Test'
        })
        self.assertEquals(response.status_code, 200)
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline, None)
        self.assertIn('If you do not want to provide an &quot;About this deadline&quot; message, you have to clear the text field.',
            response.content)


    #
    #
    # Cancel and success urls
    #
    #
    def test_custom_success_url(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'deadline': isoformat_datetime(deadline_datetime),
            'text': 'Hello world',
            'success_url': '/my/test',
            'add_deadline_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('/my/test'))

    def test_custom_cancel_url(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'cancel_url': '/my/test',
            'submit_cancel': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('/my/test'))


    def test_default_success_url(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'deadline': isoformat_datetime(deadline_datetime),
            'text': 'Hello world',
            'add_deadline_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(
            reverse('devilry_examiner_allgroupsoverview', kwargs={'assignmentid': self.assignment1builder.assignment.id})))

    def test_default_cancel_url(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'submit_cancel': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(
            reverse('devilry_examiner_allgroupsoverview', kwargs={'assignmentid': self.assignment1builder.assignment.id})))
