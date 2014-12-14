from django.test import TestCase

from devilry.apps.core.models import Period
from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient
from devilry.devilry_subjectadmin.tests.rest.common import isoformat_relativetime


class TestRestListOrCreatePeriodRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck2000:admin(subadmin)'],
                            periods=['one:admin(adminone)',
                                     'two',
                                     'three:admin(adminone)'])
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/period/'
        self.testhelper.create_user('nobody')

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_list(self):
        content, response = self._listas('adminone')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        self.assertEquals(set(content[0].keys()),
                          set(['id', 'parentnode', 'etag', 'short_name', 'long_name',
                               'start_time', 'end_time', 'url']))

    def test_list_nonadmin(self):
        self.testhelper.create_user('otheruser')
        content, response = self._listas('otheruser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)

    def test_list_in_subject(self):
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck9000'],
                            periods=['p1', 'p2'])
        content, response = self._listas('uniadmin',
                                         parentnode=self.testhelper.duck9000.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        shortnames = set([p['short_name'] for p in content])
        self.assertEquals(shortnames, set(['p1', 'p2']))

    def _createas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self.url, data)

    def test_create(self):
        content, response = self._createas('subadmin',
                                           {'short_name': 'test',
                                            'long_name': 'Test',
                                            'admins': [],
                                            'start_time': isoformat_relativetime(days=-2),
                                            'end_time': isoformat_relativetime(days=2),
                                            'parentnode': self.testhelper.duck2000.id})
        self.assertEquals(response.status_code, 201)
        self.assertEquals(content['long_name'], 'Test')
        self.assertEquals(content['short_name'], 'test')
        self.assertEquals(content['parentnode'], self.testhelper.duck2000.id)
        created = Period.objects.get(id=content['id'])
        self.assertEquals(created.short_name, 'test')
        self.assertEquals(created.long_name, 'Test')
        self.assertEquals(created.parentnode.id, self.testhelper.duck2000.id)
        admins = created.admins.all()
        self.assertEquals(len(admins), 0)

    def test_create_nobody(self):
        content, response = self._createas('nobody',
                                           {'short_name': 'test',
                                            'long_name': 'Test',
                                            'admins': [],
                                            'start_time': isoformat_relativetime(days=-2),
                                            'end_time': isoformat_relativetime(days=2),
                                            'parentnode': self.testhelper.duck2000.id})
        self.assertEquals(response.status_code, 403)
        self.assertEquals(content['detail'], 'Permission denied')

    def test_create_admins(self):
        self.testhelper.create_user('testadmin')
        content, response = self._createas('uniadmin',
                                           {'short_name': 'test',
                                            'long_name': 'Test',
                                            'admins': [{'id': self.testhelper.testadmin.id}],
                                            'start_time': isoformat_relativetime(days=-2),
                                            'end_time': isoformat_relativetime(days=2),
                                            'parentnode': self.testhelper.duck2000.id})
        self.assertEquals(response.status_code, 201)
        created = Period.objects.get(id=content['id'])
        admins = created.admins.all()
        self.assertEquals(len(admins), 1)
        self.assertEquals(admins[0].username, 'testadmin')


class TestRestInstancePeriodRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck2000:admin(duck2000admin)'],
                            periods=['periodone:admin(oneadmin)',
                                     'periodtwo',
                                     'periodthree:admin(adminone)'])
        self.client = RestClient()

    def _geturl(self, periodid):
        return '/devilry_subjectadmin/rest/period/{0}'.format(periodid)

    def test_delete_denied(self):
        self.client.login(username='nobody', password='test')
        content, response = self.client.rest_delete(self._geturl(self.testhelper.duck2000_periodone.id))
        self.assertEquals(response.status_code, 403)

    def test_delete(self):
        self.client.login(username='uniadmin', password='test')
        content, response = self.client.rest_delete(self._geturl(self.testhelper.duck2000_periodone.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000_periodone.id)
        self.assertEquals(Period.objects.filter(id=self.testhelper.duck2000_periodone.id).count(), 0)


    def test_get(self):
        period = self.testhelper.duck2000_periodone
        for username in ('student1', 'student2', 'student3', 'student4'):
            user = self.testhelper.create_user(username)
            period.relatedstudent_set.create(user=user)
        for username in ('examiner1', 'examiner2'):
            user = self.testhelper.create_user(username)
            period.relatedexaminer_set.create(user=user)

        self.client.login(username='duck2000admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000_periodone.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000_periodone.id)
        self.assertEquals(content['short_name'], self.testhelper.duck2000_periodone.short_name)
        self.assertEquals(content['long_name'], self.testhelper.duck2000_periodone.long_name)
        self.assertEquals(content['parentnode'], self.testhelper.duck2000_periodone.parentnode_id)
        self.assertEquals(content['can_delete'], self.testhelper.duck2000_periodone.can_delete(self.testhelper.uniadmin))
        self.assertEquals(content['number_of_relatedexaminers'], 2)
        self.assertEquals(content['number_of_relatedstudents'], 4)
        self.assertEquals(set(content.keys()),
                          set(['short_name', 'long_name', 'admins', 'etag',
                               'can_delete', 'parentnode', 'id', 'inherited_admins',
                               'start_time', 'end_time', 'breadcrumb',
                               'number_of_relatedexaminers', 'number_of_relatedstudents']))

    def test_get_admins(self):
        self.client.login(username='duck2000admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000_periodone.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['admins']), 1)
        self.assertEquals(content['admins'][0]['email'], 'oneadmin@example.com')
        self.assertEquals(set(content['admins'][0].keys()),
                          set(['email', 'username', 'id', 'full_name']))

    def test_get_inherited_admins(self):
        self.client.login(username='duck2000admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000_periodone.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['inherited_admins']), 2)
        self.assertEquals(set(content['inherited_admins'][0].keys()),
                          set(['basenode', 'user']))
        self.assertEquals(set(content['inherited_admins'][0]['basenode'].keys()),
                          set(['type', 'path', 'id', 'is_admin']))
        self.assertEquals(set(content['inherited_admins'][0]['user'].keys()),
                          set(['email', 'username', 'id', 'full_name']))
        inherited_adminusernames = [user['user']['username'] for user in content['inherited_admins']]
        self.assertIn('uniadmin', inherited_adminusernames)
        self.assertIn('duck2000admin', inherited_adminusernames)

    def test_get_breadcrumb_periodadmin(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)'])
        self.client.login(username='p1admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.sub_p1.id, u'text': u'sub.p1', u'type': u'Period'}])

    def test_get_breadcrumb_subjectadmin(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub:admin(subadm)'],
                            periods=['p1'])
        self.client.login(username='subadm', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.sub.id, u'text': u'sub', u'type': u'Subject'},
                           {u'id': th.sub_p1.id, u'text': u'p1', u'type': u'Period'}])

    def test_get_breadcrumb_nodeadmin(self):
        self.testhelper.add(nodes='uni:admin(uniadmin).inf',
                            subjects=['sub'],
                            periods=['p1'])
        self.client.login(username='uniadmin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.uni.id, u'text': u'uni', u'type': u'Node'},
                           {u'id': th.uni_inf.id, u'text': u'inf', u'type': u'Node'},
                           {u'id': th.sub.id, u'text': u'sub', u'type': u'Subject'},
                           {u'id': th.sub_p1.id, u'text': u'p1', u'type': u'Period'}])

    def test_get_breadcrumb_superuser(self):
        self.testhelper.add(nodes='uni.inf',
                            subjects=['sub'],
                            periods=['p1'])
        self.testhelper.create_superuser('super')
        self.client.login(username='super', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.uni.id, u'text': u'uni', u'type': u'Node'},
                           {u'id': th.uni_inf.id, u'text': u'inf', u'type': u'Node'},
                           {u'id': th.sub.id, u'text': u'sub', u'type': u'Subject'},
                           {u'id': th.sub_p1.id, u'text': u'p1', u'type': u'Period'}])

    def test_get_can_not_delete(self):
        self.client.login(username='oneadmin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000_periodone.id))
        self.assertFalse(content['can_delete'])

    def test_put(self):
        self.client.login(username='oneadmin', password='test')
        data = {'short_name': 'duck2000',
                'long_name': 'Updated',
                'admins': [],
                'start_time': isoformat_relativetime(days=-2),
                'end_time': isoformat_relativetime(days=2),
                'parentnode': 1}
        content, response = self.client.rest_put(self._geturl(self.testhelper.duck2000_periodone.id),
                                                 data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000_periodone.id)
        self.assertEquals(content['short_name'], self.testhelper.duck2000.short_name)
        self.assertEquals(content['long_name'], 'Updated')
        self.assertEquals(content['parentnode'], 1)
        self.assertEquals(set(content.keys()),
                          set(['short_name', 'long_name', 'admins', 'etag',
                               'can_delete', 'parentnode', 'id', 'inherited_admins',
                               'start_time', 'end_time', 'breadcrumb',
                               'number_of_relatedstudents', 'number_of_relatedexaminers']))
        updated = Period.objects.get(id=self.testhelper.duck2000_periodone.id)
        self.assertEquals(updated.long_name, 'Updated')

    def test_put_admins(self):
        self.client.login(username='oneadmin', password='test')
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
                'start_time': isoformat_relativetime(days=-2),
                'end_time': isoformat_relativetime(days=2),
                'parentnode': 1}
        content, response = self.client.rest_put(self._geturl(self.testhelper.duck2000_periodone.id),
                                                 data=data)
        self.assertEquals(response.status_code, 200)
        admins = content['admins']
        self.assertEquals(len(content['admins']), 3)
        admins.sort(cmp=lambda a,b: cmp(a['username'], b['username']))
        self.assertEquals(admins[0]['username'], 'user1')
        self.assertEquals(admins[2]['username'], 'user3')
        updated = Period.objects.get(id=self.testhelper.duck2000_periodone.id)
        self.assertEquals(updated.admins.all().count(), 3)
