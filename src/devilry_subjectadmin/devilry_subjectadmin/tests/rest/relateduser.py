from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


#class TestRelatedStudentDao(TestCase):
    #def setUp(self):
        #self.testhelper = TestHelper()
        #self.testhelper.add(nodes='uni',
                            #subjects=['sub'],
                            #periods=['p1:admin(p1admin)', 'p2'])
        #self.testhelper.create_superuser("superuser")

    #def test_list_none(self):
        #students = RelatedStudentDao().list(self.testhelper.p1admin, self.testhelper.sub_p1.id)
        #self.assertEquals(len(students), 0)

    #def test_list(self):
        #for num in xrange(2):
            #username = "student{0}".format(num)
            #student = self.testhelper.create_user(username)
            #student.email = username + '@example.com'
            #student.devilryuserprofile.full_name = 'User {0}'.format(num)
            #student.save()
            #student.devilryuserprofile.save()
            #self.testhelper.sub_p1.relatedstudent_set.create(user=student,
                                                             #tags='group1,group2',
                                                             #candidate_id=str(num))
        #students = RelatedStudentDao().list(self.testhelper.p1admin, self.testhelper.sub_p1.id)
        #self.assertEquals(len(students), 2)
        #first, second = students
        #self.assertEquals(first['user__username'], 'student0')
        #self.assertEquals(first['user__devilryuserprofile__full_name'] , 'User 0')
        #self.assertEquals(first['candidate_id'], '0')
        #self.assertEquals(first['tags'], 'group1,group2')
        #self.assertEquals(second['user__username'], 'student1')

    #def test_list_superadmin(self):
        ## Just make it does not fail, since this is the only difference from any other admin
        #RelatedStudentDao().list(self.testhelper.superuser, self.testhelper.sub_p2.id)

    #def test_list_nonadmin(self):
        #with self.assertRaises(PermissionDeniedError):
            ## p1admin is not admin on p2
            #students = RelatedStudentDao().list(self.testhelper.p1admin,
                                                #self.testhelper.sub_p2.id)


class TestRelatedExaminerRest(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)', 'p2'])
        self.testhelper.create_superuser("superuser")
        self.url = '/devilry_subjectadmin/rest/relatedexaminer/'

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def create_users(self, count):
        for num in xrange(count):
            username = "examiner{0}".format(num)
            examiner = self.testhelper.create_user(username)
            examiner.email = username + '@example.com'
            examiner.devilryuserprofile.full_name = 'User {0}'.format(num)
            examiner.save()
            examiner.devilryuserprofile.save()
            self.testhelper.sub_p1.relatedexaminer_set.create(user=examiner,
                                                             tags='group1,group2')

    def test_list(self):
        self.create_users(2)
        content, response = self._listas(self.testhelper.p1admin, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        first, second = content
        self.assertEquals(first['user']['username'], 'examiner0')
        self.assertEquals(first['user']['full_name'] , 'User 0')
        self.assertEquals(first['tags'], 'group1,group2')
        self.assertEquals(second['user']['username'], 'examiner1')

    def test_list_none(self):
        content, response = self._listas(self.testhelper.p1admin, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)

    def test_list_superadmin(self):
        content, response = self._listas(self.testhelper.superuser, period=self.testhelper.sub_p1.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)
