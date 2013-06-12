from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


class TestRestAssignmentListing(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        #self.testhelper.add(nodes='uni:admin(uniadmin)',
                            #subjects=['duck2000:admin(adminone,admintwo):ln(Something fancy)',
                                      #'duck3000',
                                      #'duck1000:admin(adminone)',
                                      #'duck4000:admin(adminone,admintwo,singleadmin)'])
        self.client = RestClient()

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(reverse('devilry_examiner-rest-assignmentlisting'), **data)

    def test_list(self):
        self.testhelper.create_user('examiner1')
        content, response = self._listas('examiner1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, ['Hello', 'world'])
