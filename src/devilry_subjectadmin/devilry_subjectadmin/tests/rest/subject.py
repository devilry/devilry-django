from django.test import TestCase

from devilry.apps.core.models import Subject
from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


class TestRestListSubjectRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['duck2000:admin(adminone,admintwo):ln(Something fancy)',
                                      'duck3000',
                                      'duck1000:admin(adminone)',
                                      'duck4000:admin(adminone,admintwo,singleadmin)'])
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/subject/'
        self.testhelper.create_user('nobody')

    def _listas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url)

    def test_list(self):
        content, response = self._listas('adminone')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3)
        self.assertEquals(content[0]['short_name'], 'duck1000')
        self.assertEquals(content[1]['short_name'], 'duck2000')
        self.assertEquals(content[1]['long_name'], 'Something fancy')
        self.assertEquals(content[2]['short_name'], 'duck4000')
        self.assertEquals(set(content[0].keys()),
                          set(['id', 'parentnode_id', 'etag', 'short_name', 'long_name']))

    def test_singleadmin(self):
        content, response = self._listas('singleadmin')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['short_name'], 'duck4000')

    def test_nonadmin(self):
        self.testhelper.create_user('otheruser')
        content, response = self._listas('otheruser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)


class TestRestInstanceSubjectRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck2000:admin(duck2000admin):ln(Something fancy)'])
        self.client = RestClient()

    def _geturl(self, subjectid):
        return '/devilry_subjectadmin/rest/subject/{0}'.format(subjectid)

    def test_delete_denied(self):
        self.client.login(username='nobody', password='test')
        content, response = self.client.rest_delete(self._geturl(self.testhelper.duck2000.id))
        self.assertEquals(response.status_code, 403)

    def test_delete(self):
        self.client.login(username='uniadmin', password='test')
        content, response = self.client.rest_delete(self._geturl(self.testhelper.duck2000.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000.id)
        self.assertEquals(Subject.objects.filter(id=self.testhelper.duck2000.id).count(), 0)

    def test_get(self):
        self.client.login(username='uniadmin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000.id)
        self.assertEquals(content['short_name'], self.testhelper.duck2000.short_name)
        self.assertEquals(content['long_name'], self.testhelper.duck2000.long_name)
        self.assertEquals(content['parentnode_id'], self.testhelper.duck2000.parentnode_id)
        self.assertEquals(content['can_delete'], self.testhelper.duck2000.can_delete(self.testhelper.uniadmin))
        self.assertEquals(set(content.keys()),
                          set(['short_name', 'long_name', 'admins', 'etag', 'can_delete', 'parentnode_id', 'id']))

        self.assertEquals(len(content['admins']), 1)
        self.assertTrue('duck2000admin' in content['admins'])
        self.assertEquals(content['admins']['duck2000admin']['email'], 'duck2000admin@example.com')
        self.assertEquals(set(content['admins']['duck2000admin'].keys()),
                          set(['email', 'username', 'id', 'full_name']))

    def test_get_can_not_delete(self):
        self.client.login(username='duck2000admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000.id))
        self.assertFalse(content['can_delete'])
