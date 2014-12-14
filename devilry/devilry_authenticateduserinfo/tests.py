from django.test import TestCase

from devilry.devilry_rest.testclient import RestClient
from devilry.apps.core.testhelper import TestHelper



class TestUserInfo(TestCase):
    def setUp(self):
        self.client = RestClient()

        self.url = '/devilry_authenticateduserinfo/userinfo'
        self.testhelper = TestHelper()
        self.testhelper.add(nodes="uni:admin(nodeadm)",
                            subjects=["sub:admin(subjectadm)"],
                            periods=["p1:admin(periodadm):begins(-2):ends(6)"],
                            assignments=["a1:admin(assignmentadm)"])
        self.testhelper.create_superuser('grandma')
        self.testhelper.create_user('nobody')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:examiner(examiner1):candidate(student1)')

    def _getas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url)

    def _get_and_sanitytest_as(self, username, is_superuser=False,
                               is_nodeadmin=False, is_subjectadmin=False,
                               is_periodadmin=False, is_assignmentadmin=False,
                               is_student=False, is_examiner=False):
        content, response = self._getas(username)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(set(content.keys()),
                          set(['id', 'username', 'languagecode', 'email',
                               'full_name', 'is_superuser', 'is_nodeadmin',
                               'is_subjectadmin', 'is_periodadmin',
                               'is_assignmentadmin', 'is_examiner', 'is_student']))
        self.assertEquals(content['is_superuser'], is_superuser)
        self.assertEquals(content['is_nodeadmin'], is_nodeadmin)
        self.assertEquals(content['is_subjectadmin'], is_subjectadmin)
        self.assertEquals(content['is_periodadmin'], is_periodadmin)
        self.assertEquals(content['is_assignmentadmin'], is_assignmentadmin)
        self.assertEquals(content['is_student'], is_student)
        self.assertEquals(content['is_examiner'], is_examiner)
        return content

    def test_as_superuser(self):
        content = self._get_and_sanitytest_as('grandma', is_superuser=True)

    def test_as_nodeadmin(self):
        content = self._get_and_sanitytest_as('nodeadm', is_nodeadmin=True)

    def test_as_subjectadmin(self):
        content = self._get_and_sanitytest_as('subjectadm', is_subjectadmin=True)

    def test_as_periodadmin(self):
        content = self._get_and_sanitytest_as('periodadm', is_periodadmin=True)

    def test_as_assignmentadmin(self):
        content = self._get_and_sanitytest_as('assignmentadm', is_assignmentadmin=True)

    def test_as_student(self):
        content = self._get_and_sanitytest_as('student1', is_student=True)

    def test_as_examiner(self):
        content = self._get_and_sanitytest_as('examiner1', is_examiner=True)

    def test_as_nobody(self):
        nobody = self.testhelper.nobody
        nobody.devilryuserprofile.full_name = 'A true nobody'
        nobody.devilryuserprofile.languagecode = 'en_US'
        nobody.devilryuserprofile.save()

        content = self._get_and_sanitytest_as('nobody')
        self.assertEquals(content['email'], 'nobody@example.com')
        self.assertEquals(content['full_name'], 'A true nobody')
        self.assertEquals(content['languagecode'], 'en_US')
        self.assertEquals(content['username'], 'nobody')
        self.assertEquals(content['id'], self.testhelper.nobody.id)
