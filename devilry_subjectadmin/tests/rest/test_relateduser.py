from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient
from devilry.apps.core.models import RelatedExaminer
from devilry.apps.core.models import RelatedStudent


class TestListOrCreateRelatedUserMixin(object):
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
        content, response = self._listas('p1admin')
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
        content, response = self._listas('p1admin')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)

    def test_list_superuser(self):
        self._create_relatedusers(2)
        content, response = self._listas('superuser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)

    def test_list_not_admin(self):
        self._create_relatedusers(2)
        content, response = self._listas('p2admin')
        self.assertEquals(response.status_code, 403)

    def _listqueryas(self, username, query):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.get_url(), **{'query': query})

    def test_list_query(self):
        self._create_relatedusers(2)
        self.create_relateduser(self.testhelper.sub_p1, index=5, tags='group1,group2')
        self.create_relateduser(self.testhelper.sub_p2, index=20, tags='') # Not on p1, so we shold not get this in the listing!
        self.testhelper.reluser0.devilryuserprofile.full_name = 'Superhero'
        self.testhelper.reluser0.devilryuserprofile.save()
        self.testhelper.reluser1.devilryuserprofile.full_name = 'Super Not hero'
        self.testhelper.reluser1.email = 'supernothero@example.com'
        self.testhelper.reluser1.devilryuserprofile.save()
        self.testhelper.reluser1.save()

        content, response = self._listqueryas('p1admin', query='5')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)

        content, response = self._listqueryas('p1admin', query='HeRo')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)

        content, response = self._listqueryas('p1admin', query='group2')
        self.assertEquals(len(content), 1)

        content, response = self._listqueryas('p1admin', query='nothero@exAM')
        self.assertEquals(len(content), 1)

    def _createas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self.get_url(), data)

    def get_valid_createdata(self):
        """
        Overridden in TestListOrCreateRelatedStudentRest.
        """
        return {'period': self.testhelper.sub_p1.id,
                'user': self.testhelper.testuser.id, # TODO: Support username
                'tags': 'tag1,tag2'}

    def _create_test_helper(self, username):
        self.assertEquals(self.modelcls.objects.all().count(), 0)
        content, response = self._createas(username, self.get_valid_createdata())
        self.assertEquals(response.status_code, 201)
        self.assertEquals(set(content['user'].keys()),
                          set(['username', 'email', 'full_name', 'id', 'displayname']))
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



class TestListOrCreateRelatedExaminerRest(TestListOrCreateRelatedUserMixin, TestCase):
    modelcls = RelatedExaminer

    def get_url(self):
        return '/devilry_subjectadmin/rest/relatedexaminer/{0}/'.format(self.testhelper.sub_p1.id)

    def create_relateduser(self, period, index, tags=''):
        user = self._create_user(index)
        period.relatedexaminer_set.create(user=user,
                                                 tags=tags)


class TestListOrCreateRelatedStudentRest(TestListOrCreateRelatedUserMixin, TestCase):
    modelcls = RelatedStudent

    def get_url(self):
        return '/devilry_subjectadmin/rest/relatedstudent/{0}/'.format(self.testhelper.sub_p1.id)

    def create_relateduser(self, period, index, tags=''):
        user = self._create_user(index)
        period.relatedstudent_set.create(user=user,
                                         tags=tags,
                                         candidate_id='cid{0}'.format(index))

    def test_list(self):
        content = super(TestListOrCreateRelatedStudentRest, self).test_list()
        first, second, last = content
        self.assertEquals(first['candidate_id'], 'cid0')

    def get_valid_createdata(self):
        data = super(TestListOrCreateRelatedStudentRest, self).get_valid_createdata()
        data['candidate_id'] = 'cand0'
        return data

    def test_create(self):
        content, created = super(TestListOrCreateRelatedStudentRest, self).test_create()
        self.assertEquals(content['candidate_id'], 'cand0')
        self.assertEquals(created.candidate_id, 'cand0')



class TestInstanceRelatedUserMixin(object):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)', 'p2:admin(p2admin)'])
        self.testhelper.create_superuser("superuser")
        self.testreluser = self.create_reluser_on_p1('testuser', tags='group1,group2')

    def create_reluser_on_p1(self, username, tags):
        raise NotImplementedError()
    def get_url(self, periodid, reluserid):
        raise NotImplementedError()
    def get_valid_putdata(self):
        return {'period': self.testhelper.sub_p1.id,
                'tags': 'group10,group20',
                'user': self.testhelper.testuser.id}

    def _getas(self, username, periodid, id, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.get_url(periodid, id), **data)

    def test_get_404(self):
        content, response = self._getas('p1admin', self.testhelper.sub_p1.id, 40000000)
        self.assertEquals(response.status_code, 404)

    def test_get_unauthorized(self):
        content, response = self._getas('p2admin', self.testhelper.sub_p1.id, self.testreluser.id)
        self.assertEquals(response.status_code, 403)

    def test_get_superuser(self):
        content, response = self._getas('superuser', self.testhelper.sub_p1.id, self.testreluser.id)
        self.assertEquals(response.status_code, 200)

    def _putas(self, username, periodid, id, data):
        self.client.login(username=username, password='test')
        return self.client.rest_put(self.get_url(periodid, id), data)

    def test_put_unauthorized(self):
        content, response = self._putas('p2admin', self.testhelper.sub_p1.id,
                                        self.testreluser.id, self.get_valid_putdata())
        self.assertEquals(response.status_code, 403)

    def test_put_superuser(self):
        content, response = self._putas('superuser', self.testhelper.sub_p1.id,
                                        self.testreluser.id, self.get_valid_putdata())
        self.assertEquals(response.status_code, 200)

    def test_put(self):
        content, response = self._putas('p1admin', self.testhelper.sub_p1.id,
                                        self.testreluser.id, self.get_valid_putdata())
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['period'], self.testhelper.sub_p1.id)
        self.assertEquals(content['tags'], 'group10,group20')
        self.assertEquals(set(content['user'].keys()),
                          set(['email', 'full_name', 'id', 'username', 'displayname']))
        self.assertEquals(content['user']['id'], self.testreluser.user.id)
        self.assertEquals(content['user']['username'], 'testuser')
        return content

    def _deleteas(self, username, periodid, id):
        self.client.login(username=username, password='test')
        return self.client.rest_delete(self.get_url(periodid, id))

    def test_delete(self):
        reluserid = self.testreluser.id
        self.assertEquals(self.modelcls.objects.filter(id=reluserid).count(), 1)
        content, response = self._deleteas('p1admin',
                                           self.testhelper.sub_p1.id,
                                           reluserid)
        self.assertEquals(response.status_code, 204)
        self.assertEquals(self.modelcls.objects.filter(id=reluserid).count(), 0)

    def test_delete_superuser(self):
        content, response = self._deleteas('superuser',
                                           self.testhelper.sub_p1.id,
                                           self.testreluser.id)
        self.assertEquals(response.status_code, 204)

    def test_delete_unauthorized(self):
        content, response = self._deleteas('p2admin',
                                           self.testhelper.sub_p1.id,
                                           self.testreluser.id)
        self.assertEquals(response.status_code, 403)



class TestInstanceRelatedStudent(TestInstanceRelatedUserMixin, TestCase):
    modelcls = RelatedStudent

    def get_url(self, periodid, reluserid):
        return '/devilry_subjectadmin/rest/relatedstudent/{0}/{1}'.format(periodid, reluserid)

    def create_reluser_on_p1(self, username, tags):
        user = self.testhelper.create_user(username)
        return self.testhelper.sub_p1.relatedstudent_set.create(user=user,
                                                                tags=tags)

    def test_get(self):
        content, response = self._getas('p1admin', self.testhelper.sub_p1.id, self.testreluser.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content,
                          {u'id': 1,
                           u'tags': u'group1,group2',
                           u'period': 1,
                           u'candidate_id': None,
                           u'user': {u'username': u'testuser',
                                     u'email': u'testuser@example.com',
                                     u'full_name': None,
                                     u'displayname': 'testuser',
                                     u'id': 4}})

    def test_put(self):
        content = super(TestInstanceRelatedStudent, self).test_put()
        self.assertEquals(set(content.keys()),
                          set(['candidate_id', 'id', 'period', 'tags', 'user']))



class TestInstanceRelatedExaminer(TestInstanceRelatedUserMixin, TestCase):
    modelcls = RelatedExaminer

    def get_url(self, periodid, reluserid):
        return '/devilry_subjectadmin/rest/relatedexaminer/{0}/{1}'.format(periodid, reluserid)

    def create_reluser_on_p1(self, username, tags):
        user = self.testhelper.create_user(username)
        return self.testhelper.sub_p1.relatedexaminer_set.create(user=user,
                                                                tags=tags)

    def test_get(self):
        content, response = self._getas('p1admin', self.testhelper.sub_p1.id, self.testreluser.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content,
                          {u'id': 1,
                           u'tags': u'group1,group2',
                           u'period': 1,
                           u'user': {u'username': u'testuser',
                                     u'email': u'testuser@example.com',
                                     u'full_name': None,
                                     u'displayname': 'testuser',
                                     u'id': 4}})

    def test_put(self):
        content = super(TestInstanceRelatedExaminer, self).test_put()
        self.assertEquals(set(content.keys()),
                          set(['id', 'period', 'tags', 'user']))
