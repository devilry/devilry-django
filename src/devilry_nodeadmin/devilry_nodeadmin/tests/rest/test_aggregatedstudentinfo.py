from django.test import TestCase
from django.core.urlresolvers import reverse
import time
from urllib import urlencode

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


class TestRestAggregatedStudentInfo(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        #self.testhelper.add(nodes='uni:admin(uniadmin)',
                            #subjects=['duck2000:admin(adminone,admintwo):ln(Something fancy)',
                                      #'duck3000',
                                      #'duck1000:admin(adminone)',
                                      #'duck4000:admin(adminone,admintwo,singleadmin)'])
        self.client = RestClient()


    def _get(self, **data):
        return self.client.rest_get(reverse('devilry_examiner-rest-assignmentlisting'), **data)

    def _getas(self, username, **data):
        self.client.login(username=username, password='test')
        return self._get(**data)

    def test_get(self):
        self.testhelper.create_user('examiner1')
        content, response = self._getas('examiner1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, ['Hello', 'world'])

    def test_get_noauth(self):
        content, response = self._get()
        self.assertEquals(response.status_code, 401)
