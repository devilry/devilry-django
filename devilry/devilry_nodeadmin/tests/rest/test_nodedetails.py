from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient



class TestRestNodeDetails(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin).inf:admin(infadmin)')
        self.testhelper.add(nodes='uni.fys')
        self.testhelper.create_superuser('super')
        self.client = RestClient()

    def _geturl(self, node_id):
        return reverse('devilry_nodeadmin-rest_node_details', kwargs={'id': node_id})

    def test_as_nobody(self):
        self.testhelper.create_user('nobody')
        self.client.login(username='nobody', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.uni_inf.id))
        self.assertEquals(response.status_code, 403)

    def test_as_wrongadmin(self):
        self.client.login(username='infadmin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.uni_fys.id))
        self.assertEquals(response.status_code, 403)

    def _test_get_as(self, username):
        self.client.login(username=username, password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.uni_inf.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(set(content.keys()),
                set([u'subject_count', u'short_name', u'id',
                    u'long_name', u'assignment_count', u'etag',
                    u'period_count', u'path', u'childnodes', u'subjects']))
        self.assertEquals(content['short_name'], 'inf')
        self.assertEquals(content['id'], self.testhelper.uni_inf.id)

    def test_get_as_nodeadmin(self):
        self._test_get_as('infadmin')

    def test_get_as_superuser(self):
        self._test_get_as('super')


    def test_get_path_only_admin_on_child(self):
        self.client.login(username='infadmin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.uni_inf.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['path'], [
            {u'id': self.testhelper.uni_inf.id, u'short_name': u'uni.inf'}
        ])

    def _test_get_path_toplevel_admin(self, username):
        self.client.login(username=username, password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.uni_inf.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['path'], [
            {u'id': self.testhelper.uni.id, u'short_name': u'uni'},
            {u'id': self.testhelper.uni_inf.id, u'short_name': u'inf'}
        ])

    def test_get_path_toplevel_admin(self):
        self._test_get_path_toplevel_admin('uniadmin')

    def test_get_path_toplevel_superuser(self):
        self._test_get_path_toplevel_admin('super')
