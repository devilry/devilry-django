from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient
from devilry.apps.core.models import RelatedExaminer
from devilry.apps.core.models import RelatedStudent


class TestListRelatedUserOnAssignmentMixin(object):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)',
                                         'a2:admin(a2admin)'])
        self.testhelper.add_to_path('uni;sub.p2')
        self.testhelper.create_superuser("superuser")
        self.testhelper.create_user('testuser')

    def get_url(self):
        """
        Get url of rest API.
        """
        raise NotImplementedError()

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

    def create_relateduser(self, period, index, tags=''):
        """
        Create a related user of the type that we are testing.
        """
        raise NotImplementedError()

    def _create_relatedusers(self, count):
        for index in xrange(count):
            self.create_relateduser(self.testhelper.sub_p1, index)

    def test_list(self):
        self._create_relatedusers(2)
        self.create_relateduser(self.testhelper.sub_p1, index=5, tags='group1,group2')
        self.create_relateduser(self.testhelper.sub_p2, index=20, tags='') # Not on p1, so we shold not get this in the listing!
        content, response = self._listas(self.testhelper.a1admin, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3) # Since this is 3, we did not get the user registered on p2.
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
        content, response = self._listas(self.testhelper.a1admin, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)

    def test_list_superuser(self):
        self._create_relatedusers(2)
        content, response = self._listas(self.testhelper.superuser, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)

    def test_list_not_admin(self):
        self._create_relatedusers(2)
        content, response = self._listas(self.testhelper.a2admin, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 403)



class TestListRelatedExaminerOnAssignmentRest(TestListRelatedUserOnAssignmentMixin, TestCase):
    modelcls = RelatedExaminer

    def get_url(self):
        return '/devilry_subjectadmin/rest/relatedexaminer_assignment_ro/{0}/'.format(self.testhelper.sub_p1_a1.id)

    def create_relateduser(self, period, index, tags=''):
        user = self._create_user(index)
        period.relatedexaminer_set.create(user=user, tags=tags)


class TestListRelatedStudentOnAssignmentRest(TestListRelatedUserOnAssignmentMixin, TestCase):
    modelcls = RelatedStudent

    def get_url(self):
        return '/devilry_subjectadmin/rest/relatedstudent_assignment_ro/{0}/'.format(self.testhelper.sub_p1_a1.id)

    def create_relateduser(self, period, index, tags=''):
        user = self._create_user(index)
        period.relatedstudent_set.create(user=user,
                                         tags=tags,
                                         candidate_id='cid{0}'.format(index))

    def test_list(self):
        content = super(TestListRelatedStudentOnAssignmentRest, self).test_list()
        first, second, last = content
        self.assertEquals(first['candidate_id'], 'cid0')
