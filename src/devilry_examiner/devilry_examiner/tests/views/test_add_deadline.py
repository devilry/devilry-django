from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.models import Deadline
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.datebuilder import DateTimeBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists
from devilry_examiner.tests.utils import isoformat_datetime



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

    def test_get_200_when_examiner(self):
        group1 = self.assignment1builder\
            .add_group(examiners=[self.examiner1]).group
        response = self._getas(self.examiner1, {
            'group_ids': [group1.id]
        })
        self.assertEquals(response.status_code, 200)

    def test_get_404_when_not_examiner(self):
        group1 = self.assignment1builder\
            .add_group().group # Not adding any examiners.
        response = self._getas(self.examiner1, {
            'group_ids': [group1.id]
        })
        self.assertEquals(response.status_code, 404)


    #######################################
    # Initial rendering
    #######################################

    def test_header(self):
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
            'submit_primary': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline.deadline, deadline_datetime)
        self.assertEquals(group1builder.group.last_deadline.text, 'Hello world')


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
            'submit_primary': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)

        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline.deadline, deadline_datetime)
        self.assertEquals(group1builder.group.last_deadline.text, 'Hello world')

        group2builder.reload_from_db()
        self.assertEquals(group2builder.group.last_deadline.deadline, deadline_datetime)
        self.assertEquals(group2builder.group.last_deadline.text, 'Hello world')

    def test_post_no_text(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        deadline_datetime = Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=10))
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'deadline': isoformat_datetime(deadline_datetime),
            'submit_primary': 'i18nlabel',
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
            'submit_primary': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 200)
        group1builder.reload_from_db()
        self.assertEquals(group1builder.group.last_deadline, None)
        self.assertIn('You must specify a deadline text, or select that you do not want to specify any text.',
            response.content)
