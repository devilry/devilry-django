from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists


class TestAddDeadlineView(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', long_name='Assignment One')

    def _getas(self, username, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_add_deadline', kwargs={
            'assignmentid': self.assignment1builder.assignment.id}), *args, **kwargs)

    def test_404_when_not_examiner(self):
        response = self._getas('examiner1')
        self.assertEquals(response.status_code, 404)

    def test_header(self):
        group1 = deliverybuilder = self.assignment1builder\
            .add_group(examiners=[self.examiner1]).group
        response = self._getas('examiner1', {
            'group_ids': [group1.id]
        })
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
            'Add deadline')
        # self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(),
            # "duck1010 active Assignment One")
