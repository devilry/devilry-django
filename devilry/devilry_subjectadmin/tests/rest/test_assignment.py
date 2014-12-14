from django.test import TestCase

from devilry.apps.core.models import Assignment
from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient
from devilry.devilry_subjectadmin.tests.rest.common import isoformat_relativetime

class TestRestListOrCreateAssignmentRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck2000'],
                            periods=['someperiod:begins(-2):ends(6):admin(periodadm)'],
                            assignments=['first:admin(firstadmin)',
                                         'second:admin(secondadmin,firstadmin)',
                                         'third'])
        self.testhelper.add_to_path('uni;duck9000.otherperiod:begins(-3):ends(6).someassignment:admin(firstadmin)')
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/assignment/'
        self.testhelper.create_user('nobody')

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_list(self):
        content, response = self._listas('firstadmin')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3)
        self.assertEquals(set(content[0].keys()),
                          set(['id', 'parentnode', 'short_name', 'long_name',
                               'publishing_time', 'delivery_types',
                               'is_published', 'publishing_time_offset_from_now',
                               'scale_points_percent', 'first_deadline',
                               'anonymous', 'deadline_handling']))

    def test_list_nonadmin(self):
        self.testhelper.create_user('otheruser')
        content, response = self._listas('otheruser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)

    def test_list_in_subject(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['per'],
                            assignments=['a', 'b'])
        content, response = self._listas('uniadmin',
                                         parentnode=self.testhelper.sub_per.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        shortnames = set([a['short_name'] for a in content])
        self.assertEquals(shortnames, set(['a', 'b']))

    def _createas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self.url, data)

    def test_create(self):
        content, response = self._createas('periodadm',
                                           {'short_name': 'test',
                                            'long_name': 'Test',
                                            'admins': [],
                                            'anonymous': True,
                                            'publishing_time': isoformat_relativetime(days=2),
                                            'first_deadline': isoformat_relativetime(days=3),
                                            'scale_points_percent': 100,
                                            'deadline_handling': 0,
                                            'delivery_types': 0,
                                            'parentnode': self.testhelper.duck2000_someperiod.id})
        self.assertEquals(response.status_code, 201)
        self.assertEquals(content['delivery_types'], 0)
        self.assertEquals(content['scale_points_percent'], 100)
        self.assertTrue(content['publishing_time'] != None)
        self.assertTrue(content['first_deadline'] != None)
        self.assertEquals(content['long_name'], 'Test')
        self.assertEquals(content['short_name'], 'test')
        self.assertEquals(content['anonymous'], True)
        self.assertEquals(content['parentnode'], self.testhelper.duck2000_someperiod.id)
        created = Assignment.objects.get(id=content['id'])
        self.assertEquals(created.short_name, 'test')
        self.assertEquals(created.long_name, 'Test')
        self.assertEquals(created.delivery_types, 0)
        self.assertEquals(created.anonymous, True)
        self.assertEquals(created.scale_points_percent, 100)
        self.assertEquals(created.deadline_handling, 0)
        self.assertEquals(created.parentnode.id, self.testhelper.duck2000_someperiod.id)
        admins = created.admins.all()
        self.assertEquals(len(admins), 0)

    def test_create_nobody(self):
        content, response = self._createas('nobody',
                                           {'short_name': 'test',
                                            'long_name': 'Test',
                                            'admins': [],
                                            'publishing_time': isoformat_relativetime(days=-2),
                                            'scale_points_percent': 100,
                                            'deadline_handling': 0,
                                            'delivery_types': 0,
                                            'parentnode': self.testhelper.duck2000_someperiod.id})
        self.assertEquals(response.status_code, 403)
        self.assertEquals(content['detail'], 'Permission denied')

    def test_create_admins(self):
        self.testhelper.create_user('testadmin')
        content, response = self._createas('uniadmin',
                                           {'short_name': 'test',
                                            'long_name': 'Test',
                                            'admins': [{'id': self.testhelper.testadmin.id}],
                                            'publishing_time': isoformat_relativetime(days=-2),
                                            'scale_points_percent': 100,
                                            'deadline_handling': 0,
                                            'delivery_types': 0,
                                            'parentnode': self.testhelper.duck2000.id})
        self.assertEquals(response.status_code, 201)
        created = Assignment.objects.get(id=content['id'])
        admins = created.admins.all()
        self.assertEquals(len(admins), 1)
        self.assertEquals(admins[0].username, 'testadmin')



class TestRestInstanceAssignmentRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck2000:admin(duck2000admin)'],
                            periods=['someperiod:begins(-2):ends(6)'],
                            assignments=['first:admin(firstadmin)',
                                         'second:admin(secondadmin,firstadmin)',
                                         'third'])
        self.client = RestClient()

    def _geturl(self, assignmentid):
        return '/devilry_subjectadmin/rest/assignment/{0}'.format(assignmentid)

    def test_delete_denied(self):
        self.client.login(username='nobody', password='test')
        content, response = self.client.rest_delete(self._geturl(self.testhelper.duck2000_someperiod_first.id))
        self.assertEquals(response.status_code, 403)

    def test_delete(self):
        self.client.login(username='uniadmin', password='test')
        content, response = self.client.rest_delete(self._geturl(self.testhelper.duck2000_someperiod_first.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000_someperiod_first.id)
        self.assertEquals(Assignment.objects.filter(id=self.testhelper.duck2000_someperiod_first.id).count(), 0)

    def test_get(self):
        self.testhelper.add_to_path('uni;duck2000.someperiod.first.g1:candidate(student1):examiner(examiner1).d1')
        self.testhelper.add_to_path('uni;duck2000.someperiod.first.g2:candidate(student2,student3,student4,student5):examiner(examiner1).d1')
        self.testhelper.add_delivery('duck2000.someperiod.first.g1', {'bad.py': ['print ', 'bah']})
        self.testhelper.add_delivery('duck2000.someperiod.first.g1', {'good.py': ['print ', 'good']})
        self.testhelper.add_delivery('duck2000.someperiod.first.g2', {'good.py': ['print ', 'good']})

        self.client.login(username='duck2000admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000_someperiod_first.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000_someperiod_first.id)
        self.assertEquals(content['short_name'], self.testhelper.duck2000_someperiod_first.short_name)
        self.assertEquals(content['long_name'], self.testhelper.duck2000_someperiod_first.long_name)
        self.assertEquals(content['deadline_handling'], self.testhelper.duck2000_someperiod_first.deadline_handling)
        self.assertEquals(content['parentnode'], self.testhelper.duck2000_someperiod_first.parentnode_id)
        self.assertEquals(content['can_delete'], self.testhelper.duck2000_someperiod_first.can_delete(self.testhelper.duck2000admin))
        self.assertEquals(content['can_delete'], False)
        self.assertEquals(content['number_of_groups'], 2)
        self.assertEquals(content['number_of_deliveries'], 3)
        self.assertEquals(content['number_of_candidates'], 5)
        self.assertEquals(content['has_valid_grading_setup'], True)
        self.assertEquals(content['gradingsystemplugin_title'], 'Passed/failed')
        self.assertEquals(set(content.keys()),
                          set(['short_name', 'long_name', 'admins',
                               'can_delete', 'parentnode', 'id', 'inherited_admins',
                               'publishing_time', 'delivery_types',
                               'is_published', 'publishing_time_offset_from_now',
                               'scale_points_percent', 'deadline_handling',
                               'first_deadline', 'breadcrumb', 'anonymous',
                               'number_of_deliveries', 'number_of_groups',
                               'number_of_candidates',
                               'number_of_groups_where_is_examiner',
                               'has_valid_grading_setup', 'gradingsystemplugin_title',
                               'max_points', 'points_to_grade_mapper', 'grading_system_plugin_id', 'passing_grade_min_points'
                               ]))

    def test_get_admins(self):
        self.client.login(username='duck2000admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000_someperiod_first.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['admins']), 1)
        self.assertEquals(content['admins'][0]['email'], 'firstadmin@example.com')
        self.assertEquals(set(content['admins'][0].keys()),
                          set(['email', 'username', 'id', 'full_name']))

    def test_get_inherited_admins(self):
        self.client.login(username='duck2000admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000_someperiod_first.id))
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

    def test_get_breadcrumb_assignmentadmin(self):
        self.testhelper.add(nodes='uni.inf',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)'])
        self.client.login(username='a1admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1_a1.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.sub_p1_a1.id, u'text': u'sub.p1.a1', u'type': u'Assignment'}])

    def test_get_breadcrumb_periodadmin(self):
        self.testhelper.add(nodes='uni.inf',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)'],
                            assignments=['a1'])
        self.client.login(username='p1admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1_a1.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.sub_p1.id, u'text': u'sub.p1', u'type': u'Period'},
                           {u'id': th.sub_p1_a1.id, u'text': u'a1', u'type': u'Assignment'}])

    def test_get_breadcrumb_subjectadmin(self):
        self.testhelper.add(nodes='uni.inf',
                            subjects=['sub:admin(subadm)'],
                            periods=['p1'],
                            assignments=['a1'])
        self.client.login(username='subadm', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1_a1.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.sub.id, u'text': u'sub', u'type': u'Subject'},
                           {u'id': th.sub_p1.id, u'text': u'p1', u'type': u'Period'},
                           {u'id': th.sub_p1_a1.id, u'text': u'a1', u'type': u'Assignment'}])

    def test_get_breadcrumb_nodeadmin(self):
        self.testhelper.add(nodes='uni:admin(uniadm).inf',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1'])
        self.client.login(username='uniadm', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1_a1.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.uni.id, u'text': u'uni', u'type': u'Node'},
                           {u'id': th.uni_inf.id, u'text': u'inf', u'type': u'Node'},
                           {u'id': th.sub.id, u'text': u'sub', u'type': u'Subject'},
                           {u'id': th.sub_p1.id, u'text': u'p1', u'type': u'Period'},
                           {u'id': th.sub_p1_a1.id, u'text': u'a1', u'type': u'Assignment'}])

    def test_get_breadcrumb_superuser(self):
        self.testhelper.add(nodes='uni.inf',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1'])
        self.testhelper.create_superuser('super')
        self.client.login(username='super', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1_a1.id))
        self.assertEquals(response.status_code, 200)
        th = self.testhelper
        self.assertEquals(content['breadcrumb'],
                          [{u'id': th.uni.id, u'text': u'uni', u'type': u'Node'},
                           {u'id': th.uni_inf.id, u'text': u'inf', u'type': u'Node'},
                           {u'id': th.sub.id, u'text': u'sub', u'type': u'Subject'},
                           {u'id': th.sub_p1.id, u'text': u'p1', u'type': u'Period'},
                           {u'id': th.sub_p1_a1.id, u'text': u'a1', u'type': u'Assignment'}])

    def test_get_can_not_delete(self):
        self.client.login(username='firstadmin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.duck2000_someperiod_first.id))
        self.assertEquals(response.status_code, 200)
        self.assertFalse(content['can_delete'])

    def test_put(self):
        self.client.login(username='firstadmin', password='test')
        data = {'short_name': 'duck2000',
                'long_name': 'Updated',
                'admins': [],
                'publishing_time': isoformat_relativetime(days=-2),
                'scale_points_percent': 80,
                'deadline_handling': 0,
                'delivery_types': 0,
                'parentnode': 1}
        content, response = self.client.rest_put(self._geturl(self.testhelper.duck2000_someperiod_first.id),
                                                 data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], self.testhelper.duck2000_someperiod_first.id)
        self.assertEquals(content['short_name'], self.testhelper.duck2000.short_name)
        self.assertEquals(content['long_name'], 'Updated')
        self.assertEquals(content['parentnode'], 1)
        self.assertEquals(content['scale_points_percent'], 80)
        self.assertEquals(content['deadline_handling'], 0)
        self.assertEquals(content['delivery_types'], 0)
        self.assertEquals(set(content.keys()),
                          set(['short_name', 'long_name', 'admins',
                               'can_delete', 'parentnode', 'id', 'inherited_admins',
                               'publishing_time', 'delivery_types',
                               'is_published', 'publishing_time_offset_from_now',
                               'scale_points_percent', 'deadline_handling',
                               'first_deadline', 'breadcrumb', 'anonymous',
                               'number_of_deliveries', 'number_of_groups',
                               'number_of_candidates',
                               'number_of_groups_where_is_examiner',
                               'has_valid_grading_setup', 'gradingsystemplugin_title',
                               'max_points', 'points_to_grade_mapper', 'grading_system_plugin_id', 'passing_grade_min_points'
                               ]))
        updated = Assignment.objects.get(id=self.testhelper.duck2000_someperiod_first.id)
        self.assertEquals(updated.long_name, 'Updated')

    def test_put_admins(self):
        self.client.login(username='firstadmin', password='test')
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
                'publishing_time': isoformat_relativetime(days=-2),
                'scale_points_percent': 80,
                'deadline_handling': 0,
                'delivery_types': 0,
                'parentnode': 1}
        content, response = self.client.rest_put(self._geturl(self.testhelper.duck2000_someperiod_first.id),
                                                 data=data)
        self.assertEquals(response.status_code, 200)
        admins = content['admins']
        self.assertEquals(len(content['admins']), 3)
        admins.sort(cmp=lambda a,b: cmp(a['username'], b['username']))
        self.assertEquals(admins[0]['username'], 'user1')
        self.assertEquals(admins[2]['username'], 'user3')
        updated = Assignment.objects.get(id=self.testhelper.duck2000_someperiod_first.id)
        self.assertEquals(updated.admins.all().count(), 3)
