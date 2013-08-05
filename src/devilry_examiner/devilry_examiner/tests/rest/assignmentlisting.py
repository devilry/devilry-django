from django.test import TestCase
from django.core.urlresolvers import reverse
import time
from urllib import urlencode

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


    #def _put(self, getdata, data):
        #url = reverse('devilry_examiner-rest-assignmentlisting')
        #url = '{}?{}'.format(url, urlencode(getdata))
        #print url
        #return self.client.rest_put(url, data)

    #def test_secret_key_auth(self):
        #from devilry_rest.auth import calculate_signature
        #import json

        #getdata = {
                #'somearg': 'A',
                #'_auth_public_key': 'abc123',
                #'_auth_timestamp': int(time.mktime(time.gmtime()))
        #}
        #bodydata = {'somedata': 'hello'}

        #signature = calculate_signature(
                #secret_key='test123',
                #getdata=getdata,
                #request_body=json.dumps(bodydata))
        #getdata.update({
            #'_auth_signature': signature,
            #})
        #content, response = self._put(getdata, bodydata)
        #self.assertEquals(response.status_code, 401)
