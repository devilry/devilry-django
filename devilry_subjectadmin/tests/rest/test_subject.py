from django.test import TestCase

from devilry.apps.core.models import Subject
from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient


class TestRestListOrCreateSubjectRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck2000:admin(adminone,admintwo):ln(Something fancy)',
                                      'duck3000',
                                      'duck1000:admin(adminone)',
                                      'duck4000:admin(adminone,admintwo,singleadmin)'])
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/subject/'
        self.testhelper.create_user('nobody')

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_list(self):
        content, response = self._listas('adminone')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3)
        self.assertEquals(content[0]['short_name'], 'duck1000')
        self.assertEquals(content[1]['short_name'], 'duck2000')
        self.assertEquals(content[1]['long_name'], 'Something fancy')
        self.assertEquals(content[2]['short_name'], 'duck4000')
        self.assertEquals(set(content[0].keys()),
                          set(['id', 'parentnode', 'etag', 'short_name', 'long_name']))

    def test_list_singleadmin(self):
        content, response = self._listas('singleadmin')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['short_name'], 'duck4000')

    def test_list_nonadmin(self):
        self.testhelper.create_user('otheruser')
        content, response = self._listas('otheruser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)

    def test_list_in_node(self):
        self.testhelper.add(nodes='othernode:admin(otheradmin)',
                            subjects=['s1', 's2'])
        content, response = self._listas('otheradmin',
                                         parentnode=self.testhelper.othernode.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        shortnames = set([p['short_name'] for p in content])
        self.assertEquals(shortnames, set(['s1', 's2']))

    def _createas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self.url, data)

    def test_create(self):
        content, response = self._createas('uniadmin',
                                           {'short_name': 'test',
                                            'long_name': 'Test',
                                            'admins': [],
                                            'parentnode': self.testhelper.uni.id})
        self.assertEquals(response.status_code, 201)
        self.assertEquals(content['long_name'], 'Test')
        self.assertEquals(content['short_name'], 'test')
        self.assertEquals(content['parentnode'], self.testhelper.uni.id)
        created = Subject.objects.get(id=content['id'])
        self.assertEquals(created.short_name, 'test')
        self.assertEquals(created.long_name, 'Test')
        self.assertEquals(created.parentnode.id, self.testhelper.uni.id)
        admins = created.admins.all()
        self.assertEquals(len(admins), 0)

    def test_create_nobody(self):
        content, response = self._createas('nobody',
                                           {'short_name': 'test',
                                            'long_name': 'Test',
                                            'admins': [],
                                            'parentnode': self.testhelper.uni.id})
        self.assertEquals(response.status_code, 403)
        self.assertEquals(content['detail'], 'Permission denied')

    def test_create_admins(self):
        self.testhelper.create_user('testadmin')
        content, response = self._createas('uniadmin',
                                           {'short_name': 'test',
                                            'long_name': 'Test',
                                            'admins': [{'id': self.testhelper.testadmin.id}],
                                            'parentnode': self.testhelper.uni.id})
        self.assertEquals(response.status_code, 201)
        created = Subject.objects.get(id=content['id'])
        admins = created.admins.all()
        self.assertEquals(len(admins), 1)
        self.assertEquals(admins[0].username, 'testadmin')


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

    def test_delete_notempty(self):
        self.testhelper.add_to_path('uni;duck2000.p1')
        self.client.login(username='uniadmin', password='test')
        content, response = self.client.rest_delete(self._geturl(self.testhelper.duck2000.id))
        self.assertEquals(response.status_code, 403)
        self.assertIn('Only superadmins can delete non-empty items', content['detail'])

    def test_get(self):
        self.client.login(username='uniadmin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000.id)
        self.assertEquals(content['short_name'], self.testhelper.duck2000.short_name)
        self.assertEquals(content['long_name'], self.testhelper.duck2000.long_name)
        self.assertEquals(content['parentnode'], self.testhelper.duck2000.parentnode_id)
        self.assertEquals(content['can_delete'], self.testhelper.duck2000.can_delete(self.testhelper.uniadmin))
        self.assertEquals(set(content.keys()),
                          set(['short_name', 'long_name', 'admins', 'etag',
                               'can_delete', 'parentnode', 'id', 'inherited_admins',
                               'breadcrumb']))

    def test_get_admins(self):
        self.client.login(username='uniadmin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['admins']), 1)
        self.assertEquals(content['admins'][0]['email'], 'duck2000admin@example.com')
        self.assertEquals(set(content['admins'][0].keys()),
                          set(['email', 'username', 'id', 'full_name']))

    def test_get_inherited_admins(self):
        self.client.login(username='uniadmin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['inherited_admins']), 1)
        self.assertEquals(set(content['inherited_admins'][0].keys()),
                          set(['basenode', 'user']))
        self.assertEquals(set(content['inherited_admins'][0]['basenode'].keys()),
                          set(['type', 'path', 'id', 'is_admin']))
        self.assertEquals(set(content['inherited_admins'][0]['user'].keys()),
                          set(['email', 'username', 'id', 'full_name']))
        inherited_adminusernames = [user['user']['username'] for user in content['inherited_admins']]
        self.assertEquals(inherited_adminusernames, ['uniadmin'])

    def test_get_breadcrumb_subjectadmin(self):
        self.testhelper.add(nodes='uni.inf',
                            subjects=['sub:admin(subadm)'])
        self.client.login(username='subadm', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.sub.id, u'text': u'sub', u'type': u'Subject'}])

    def test_get_breadcrumb_nodeadmin(self):
        self.testhelper.add(nodes='uni:admin(uniadm).inf',
                            subjects=['sub'])
        self.client.login(username='uniadm', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.uni.id, u'text': u'uni', u'type': u'Node'},
                           {u'id': th.uni_inf.id, u'text': u'inf', u'type': u'Node'},
                           {u'id': th.sub.id, u'text': u'sub', u'type': u'Subject'}])

    def test_get_breadcrumb_superuser(self):
        self.testhelper.add(nodes='uni.inf',
                            subjects=['sub'])
        self.testhelper.create_superuser('super')
        self.client.login(username='super', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.uni.id, u'text': u'uni', u'type': u'Node'},
                           {u'id': th.uni_inf.id, u'text': u'inf', u'type': u'Node'},
                           {u'id': th.sub.id, u'text': u'sub', u'type': u'Subject'}])

    def test_get_can_not_delete(self):
        self.client.login(username='duck2000admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000.id))
        self.assertFalse(content['can_delete'])

    def test_put(self):
        self.client.login(username='duck2000admin', password='test')
        data = {'short_name': 'duck2000',
                'long_name': 'Updated',
                'admins': [],
                'parentnode': 1}
        content, response = self.client.rest_put(self._geturl(self.testhelper.duck2000.id),
                                                 data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000.id)
        self.assertEquals(content['short_name'], self.testhelper.duck2000.short_name)
        self.assertEquals(content['long_name'], 'Updated')
        self.assertEquals(content['parentnode'], 1)
        self.assertEquals(set(content.keys()),
                          set(['short_name', 'long_name', 'admins', 'etag',
                               'can_delete', 'parentnode', 'id', 'inherited_admins',
                               'breadcrumb']))

    def test_put_admins(self):
        self.client.login(username='duck2000admin', password='test')
        self.testhelper.create_user('user1')
        self.testhelper.create_user('user2')
        self.testhelper.create_user('user3')
        data = {'short_name': 'duck2000',
                'long_name': 'Updated',
                'admins': [{'username': 'user1',
                             'email': 'ignored',
                             'full_name': 'ignored!'},
                           {'username': 'user2'},
                           {'id': self.testhelper.user3.id}],
                'parentnode': 1}
        content, response = self.client.rest_put(self._geturl(self.testhelper.duck2000.id),
                                                 data=data)
        self.assertEquals(response.status_code, 200)
        admins = content['admins']
        self.assertEquals(len(content['admins']), 3)
        admins.sort(cmp=lambda a,b: cmp(a['username'], b['username']))
        self.assertEquals(admins[0]['username'], 'user1')
        self.assertEquals(admins[2]['username'], 'user3')

    def test_put_generated_fields(self):
        self.client.login(username='duck2000admin', password='test')
        data = {'short_name': 'duck2000',
                'long_name': 'Updated',
                'admins': [],
                'parentnode': 1,
                'breadcrumb': [],
                'can_delete': False,
                'inherited_admins': []}
        content, response = self.client.rest_put(self._geturl(self.testhelper.duck2000.id),
                                                 data=data)
        self.assertEquals(response.status_code, 200)
