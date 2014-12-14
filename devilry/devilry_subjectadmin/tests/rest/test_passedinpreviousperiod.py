from django.test import TransactionTestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient
from devilry.apps.core.models import deliverytypes


class TestRestPassedInPreviousPeriod(TransactionTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['old:begins(-14):ends(6)', # 14 months ago
                                     'cur:begins(-2)'], # 2 months ago
                            assignments=['a1:admin(adm):pub(0)']) # 0 days after period begins
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/passedinpreviousperiod/{0}'.format(self.testhelper.sub_cur_a1.id)

    def _getas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def _test_get_simple_as(self, username):
        self.testhelper.add_to_path('uni;sub.cur.a1.g1:candidate(student1)')
        content, response = self._getas(username)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        item = content[0]
        self.assertEquals(item['group']['id'], self.testhelper.sub_cur_a1_g1.id)
        self.assertEquals(item['oldgroup'], None)
        self.assertEquals(item['whyignored'], 'not_in_previous')

    def test_get_simple_as_assignmentadmin(self):
        self._test_get_simple_as('adm')

    def test_get_simple_as_superuser(self):
        self.testhelper.create_superuser('super')
        self._test_get_simple_as('super')

    def test_get_as_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getas('nobody')
        self.assertEquals(response.status_code, 403)

    def test_with_oldfeedback(self):
        # Add a group for the student on the old period
        self.testhelper.add_to_path('uni;sub.old.a1.g1:candidate(student1):examiner(examiner1).d1:ends(1)')
        self.testhelper.create_feedbacks(
            (self.testhelper.sub_old_a1_g1, {'grade': 'approved', 'points': 1, 'is_passing_grade': True})
        )

        # Add the student to the current period
        self.testhelper.add_to_path('uni;sub.cur.a1.g1:candidate(student1)')

        content, response = self._getas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        item = content[0]
        self.assertEquals(item['group']['id'], self.testhelper.sub_cur_a1_g1.id)
        self.assertEquals(item['whyignored'], None)
        self.assertNotEquals(item['oldgroup'], None)
        oldgroup = item['oldgroup']
        self.assertEqual(oldgroup['id'], self.testhelper.sub_old_a1_g1.id)
        self.assertEqual(oldgroup['assignment']['id'], self.testhelper.sub_old_a1.id)
        self.assertEqual(oldgroup['period']['id'], self.testhelper.sub_old.id)
        self.assertEqual(oldgroup['grade'], 'approved')

    def _putas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_put(self.url, data)

    def _test_putas(self, username):
        self.testhelper.add_to_path('uni;sub.cur.a1.g1:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.cur.a1.g2:candidate(student2).d1')
        self.testhelper.add_to_path('uni;sub.cur.a1.g3:candidate(student3).d1')

        self.testhelper.add_to_path('uni;sub.old.a1.g3:candidate(student3):examiner(examiner1).d1')
        oldg3_delivery = self.testhelper.add_delivery(self.testhelper.sub_old_a1_g3)
        self.testhelper.add_feedback(oldg3_delivery,
                                     verdict=dict(grade='C', points=40,
                                                  is_passing_grade=True))

        g1 = self.testhelper.sub_cur_a1_g1
        g2 = self.testhelper.sub_cur_a1_g2
        g3 = self.testhelper.sub_cur_a1_g3
        content, response = self._putas(username,
                                        [{'id': g1.id,
                                          'newfeedback_points': 10},
                                         {'id': g3.id,
                                          'newfeedback_points': 20}])
        self.assertEquals(response.status_code, 200)

        g1 = self.testhelper.reload_from_db(g1)
        self.assertEquals(g1.feedback.grade, 'Passed')
        self.assertEquals(g1.feedback.delivery.delivery_type, deliverytypes.ALIAS)

        g2 = self.testhelper.reload_from_db(g2)
        self.assertEquals(g2.feedback, None)

        g3 = self.testhelper.reload_from_db(g3)
        self.assertEquals(g3.feedback.grade, 'Passed')
        self.assertEquals(g3.feedback.delivery.delivery_type, deliverytypes.ALIAS)
        self.assertEquals(g3.feedback.delivery.alias_delivery, oldg3_delivery)

    def test_put_as_assignmentadmin(self):
        self._test_putas('adm')

    def test_put_as_superuser(self):
        self.testhelper.create_superuser('super')
        self._test_putas('super')

    def test_put_as_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._putas('nobody', [])
        self.assertEquals(response.status_code, 403)

    def test_put_shortformat_validationerror(self):
        self.testhelper.add_to_path('uni;sub.cur.a1.g1:candidate(student1).d1')
        g1 = self.testhelper.sub_cur_a1_g1
        content, response = self._putas('adm',
            [{'id': g1.id,
              'newfeedback_points': 'invalidstuff'}])
        self.assertEquals(response.status_code, 400)
