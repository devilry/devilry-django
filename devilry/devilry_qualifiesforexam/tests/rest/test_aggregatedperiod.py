from django.test import TestCase
from django.contrib.auth.models import User

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient



class TestRestAggregatedPeriod(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)',
                                     'p2:admin(p2admin)'])
        self.client = RestClient()

    def _geturl(self, periodid):
        return '/devilry_qualifiesforexam/rest/aggregatedperiod/{0}'.format(periodid)

    def _create_relateduser(self, username, tags='', candidate_id=None,
                            labels=[]):
        user = User.objects.get(username=username)
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=user,
                                                                      tags=tags,
                                                                      candidate_id=candidate_id)
        for label in labels:
            relstudent.relatedstudentkeyvalue_set.create(application='devilry.statistics.Labels',
                                                         key=label,
                                                         student_can_read=True)
        return relstudent

    def _test_get_as(self, username):
        self.testhelper.create_user('student1')
        relatedStudentOne = self._create_relateduser('student1',
                                                     tags='a,b',
                                                     candidate_id='secret',
                                                     labels=['qualified'])
        self.testhelper.student1.devilryuserprofile.full_name = 'Student One'
        self.testhelper.student1.devilryuserprofile.save()

        self.client.login(username=username, password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)

        student1item = content[0]
        self.assertEquals(set(student1item.keys()),
                          set(['userid', 'user', 'relatedstudent', 'groups']))
        self.assertEquals(student1item['userid'], self.testhelper.student1.id)
        self.assertEquals(student1item['groups'], [])
        self.assertEquals(student1item['user'],
                          {u'email': self.testhelper.student1.email,
                           u'full_name': u'Student One',
                           u'id': self.testhelper.student1.id,
                           u'username': u'student1'})
        self.assertEquals(set(student1item['relatedstudent'].keys()),
                          set([u'candidate_id', u'labels', u'id', u'tags']))
        self.assertEquals(student1item['relatedstudent']['candidate_id'], 'secret')
        self.assertEquals(student1item['relatedstudent']['id'], relatedStudentOne.id)
        self.assertEquals(student1item['relatedstudent']['labels'][0]['label'], 'qualified')
        self.assertEquals(student1item['relatedstudent']['tags'], u'a,b')

    def test_get_as_periodadmin(self):
        self._test_get_as('p1admin')
    def test_get_as_nodeadmin(self):
        self._test_get_as('uniadmin')
    def test_get_as_superuser(self):
        self.testhelper.create_superuser('super')
        self._test_get_as('super')

    def test_nodata(self):
        self.client.login(username='p1admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, [])

    def test_as_nobody(self):
        self.testhelper.create_user('nobody')
        self.client.login(username='nobody', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id))
        self.assertEquals(response.status_code, 403)

    def test_as_otheradmin(self):
        self.client.login(username='p2admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id))
        self.assertEquals(response.status_code, 403)

    def test_load_everything(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        relatedStudentOne = self._create_relateduser('student1')

        self.client.login(username='p1admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id),
                                                 load_everything='1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)

        student1item = content[0]
        self.assertEquals(set(student1item.keys()),
                          set(['userid', 'user', 'relatedstudent', 'groups']))
        self.assertEquals(len(student1item['groups']), 1)
        self.assertEquals(student1item['groups'][0],
                          {u'assignment_id': self.testhelper.sub_p1_a1.id,
                            u'feedback': None,
                            u'id': self.testhelper.sub_p1_a1_g1.id,
                            u'is_open': True})

    def test_include_nonrelated(self):
        self.testhelper.create_user('student1')
        relatedStudentOne = self._create_relateduser('student1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student2)')

        self.client.login(username='p1admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id),
                                                 load_everything='1',
                                                 include_nonrelated='1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)

        byUsername = {}
        for item in content:
            byUsername[item['user']['username']] = item
        self.assertTrue(byUsername['student1']['relatedstudent'] != None)
        self.assertTrue(byUsername['student2']['relatedstudent'] == None)

    def test_dont_include_nonrelated(self):
        self.testhelper.create_user('student1')
        relatedStudentOne = self._create_relateduser('student1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student2)')

        self.client.login(username='p1admin', password='test')
        content, response = self.client.rest_get(self._geturl(self.testhelper.sub_p1.id),
                                                 load_everything='1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['user']['username'], 'student1')
