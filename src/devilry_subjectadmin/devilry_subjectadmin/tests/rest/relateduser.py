from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


class TestRelatedExaminerRest(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)', 'p2:admin(p2admin)'])
        self.testhelper.create_superuser("superuser")


    def get_url(self):
        """
        Get url of rest API. Overridden in TestRelatedStudentRest.
        """
        return '/devilry_subjectadmin/rest/relatedexaminer/'

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.get_url(), **data)


    def _create_user(self, index):
        username = "reluser{0}".format(index)
        user = self.testhelper.create_user(username)
        user.email = username + '@example.com'
        user.devilryuserprofile.full_name = 'User {0}'.format(index)
        user.save()
        user.devilryuserprofile.save()
        return user

    def create_relateduser(self, index, tags=''):
        """
        Create a related user of the type that we are testing. Overridden in
        TestRelatedStudentRest.
        """
        user = self._create_user(index)
        self.testhelper.sub_p1.relatedexaminer_set.create(user=user,
                                                          tags=tags)

    def _create_relatedusers(self, count):
        for index in xrange(count):
            self.create_relateduser(index)

    def test_list(self):
        self._create_relatedusers(2)
        self.create_relateduser(index=5, tags='group1,group2')
        content, response = self._listas(self.testhelper.p1admin, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3)
        first, second, last = content
        self.assertEquals(first['user']['username'], 'reluser0')
        self.assertEquals(first['user']['full_name'] , 'User 0')
        self.assertEquals(first['tags'], '')
        self.assertEquals(second['tags'], '')
        self.assertEquals(second['user']['username'], 'reluser1')
        self.assertEquals(last['user']['username'], 'reluser5')
        self.assertEquals(last['tags'], 'group1,group2')
        return content

    def test_list_none(self):
        content, response = self._listas(self.testhelper.p1admin, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)

    def test_list_superuser(self):
        self._create_relatedusers(2)
        content, response = self._listas(self.testhelper.superuser, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)

    def test_list_not_admin(self):
        self._create_relatedusers(2)
        content, response = self._listas(self.testhelper.p2admin, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 403)


class TestRelatedStudentRest(TestRelatedExaminerRest):
    def get_url(self):
        return '/devilry_subjectadmin/rest/relatedstudent/'

    def create_relateduser(self, index, tags=''):
        user = self._create_user(index)
        self.testhelper.sub_p1.relatedstudent_set.create(user=user,
                                                         tags=tags,
                                                         candidate_id='cid{0}'.format(index))

    def test_list(self):
        content = super(TestRelatedStudentRest, self).test_list()
        first, second, last = content
        self.assertEquals(first['candidate_id'], 'cid0')
