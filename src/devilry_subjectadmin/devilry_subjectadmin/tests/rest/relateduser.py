from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient
from devilry.apps.core.models import RelatedExaminer
from devilry.apps.core.models import RelatedStudent


class TestRelatedUserRestMixin(object):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)', 'p2:admin(p2admin)'])
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

    def create_relateduser(self, index, tags=''):
        """
        Create a related user of the type that we are testing.
        """
        raise NotImplementedError()

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

    def _createas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self.get_url(), data)

    def get_valid_createdata(self):
        """
        Overridden in TestRelatedStudentRest.
        """
        return {'period': self.testhelper.sub_p1.id,
                'user': self.testhelper.testuser.id, # TODO: Support username
                'tags': 'tag1,tag2'}

    def _create_test_helper(self, username):
        self.assertEquals(self.modelcls.objects.all().count(), 0)
        content, response = self._createas(username, self.get_valid_createdata())
        self.assertEquals(response.status_code, 201)
        self.assertEquals(content['user'].keys(),
                          [u'username', u'email', u'full_name', u'id'])
        self.assertEquals(content['user']['username'], 'testuser')
        self.assertEquals(content['user']['id'], self.testhelper.testuser.id)
        self.assertEquals(content['tags'], 'tag1,tag2')
        self.assertEquals(content['period'], self.testhelper.sub_p1.id)
        self.assertEquals(self.modelcls.objects.all().count(), 1)
        created = self.modelcls.objects.all()[0]
        self.assertEquals(created.user.username, 'testuser')
        return content, created

    def test_create(self):
        return self._create_test_helper('p1admin')

    def test_create_not_admin(self):
        content, response = self._createas('p2admin', self.get_valid_createdata())
        self.assertEquals(response.status_code, 403)

    def test_create_superuser(self):
        content, response = self._create_test_helper('superuser')



class TestRelatedExaminerRest(TestRelatedUserRestMixin, TestCase):
    modelcls = RelatedExaminer

    def get_url(self):
        return '/devilry_subjectadmin/rest/relatedexaminer/'

    def create_relateduser(self, index, tags=''):
        user = self._create_user(index)
        self.testhelper.sub_p1.relatedexaminer_set.create(user=user,
                                                          tags=tags)


class TestRelatedStudentRest(TestRelatedUserRestMixin, TestCase):
    modelcls = RelatedStudent

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

    def get_valid_createdata(self):
        data = super(TestRelatedStudentRest, self).get_valid_createdata()
        data['candidate_id'] = 'cand0'
        return data

    def test_create(self):
        content, created = super(TestRelatedStudentRest, self).test_create()
        self.assertEquals(content['candidate_id'], 'cand0')
        self.assertEquals(created.candidate_id, 'cand0')
