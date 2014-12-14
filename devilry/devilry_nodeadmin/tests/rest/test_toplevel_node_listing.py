from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient



class TestRestToplevelNodeListing(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin).inf:admin(infadmin)')
        self.testhelper.add(nodes='uni.fys:admin(fysadmin)')
        self.testhelper.add(nodes='uni.fys2:admin(fysadmin)')
        self.client = RestClient()

    def _geturl(self):
        return reverse('devilry_nodeadmin-rest_toplevel_nodes')

    def test_get_as_nodeadmin(self):
        self.client.login(username='infadmin', password='test')
        content, response = self.client.rest_get(self._geturl())
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['short_name'], 'inf')

    def test_multiget_as_nodeadmin(self):
        self.client.login(username='fysadmin', password='test')
        content, response = self.client.rest_get(self._geturl())
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        self.assertEquals([n['short_name'] for n in content], ['fys', 'fys2'])

    def test_get_as_superuser(self):
        self.testhelper.create_superuser('super')
        self.client.login(username='super', password='test')
        content, response = self.client.rest_get(self._geturl())
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['short_name'], 'uni')

    def test_nodata(self):
        self.testhelper.create_user('nobody')
        self.client.login(username='nobody', password='test')
        content, response = self.client.rest_get(self._geturl())
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, [])
