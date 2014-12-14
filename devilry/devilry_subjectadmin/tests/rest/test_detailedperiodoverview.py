from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient



class TestRestDetailedPeriodOverview(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
            subjects=['sub'],
            periods=['p1:admin(periodadmin):begins(-3):ends(6)'])
        self.client = RestClient()
        self.testhelper.create_superuser('superuser')

    def _get_url(self, periodid):
        return reverse('devilry-subjectadmin-rest-detailedperiodoverview', kwargs={'id': periodid})

    def _getas(self, username, periodid):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self._get_url(periodid))

    def _test_get_as(self, username):
        content, response = self._getas(username, self.testhelper.sub_p1.id)
        self.assertEqual(response.status_code, 200)
        # NOTE: This is tested in more detail in the API that generates the data (devilry.utils.groups_groupedby_relatedstudent_and_assignment)
        self.assertEqual(set(content.keys()),
            set([u'students_with_feedback_that_is_candidate_but_not_in_related',
                 u'students_with_no_feedback_that_is_candidate_but_not_in_related',
                 u'relatedstudents', u'assignments']))

    def test_getlist_as_periodadmin(self):
        self._test_get_as('periodadmin')
    def test_getlist_as_nodeadmin(self):
        self._test_get_as('uniadmin')
    def test_getlist_as_superuser(self):
        self._test_get_as('superuser')

    def test_get_as_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getas('nobody', self.testhelper.sub_p1.id)
        self.assertEqual(response.status_code, 403)

    def test_get_invalid_id(self):
        content, response = self._getas('periodadmin', 10000)
        self.assertEqual(response.status_code, 403)
