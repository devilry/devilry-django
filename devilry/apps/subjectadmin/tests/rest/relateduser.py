from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.subjectadmin.rest.errors import PermissionDeniedError
from devilry.apps.subjectadmin.rest.relateduser import RelatedStudentDao


class TestRelatedStudentDao(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)', 'p2'])
        self.testhelper.create_superuser("superuser")

    def test_list_none(self):
        students = RelatedStudentDao().list(self.testhelper.p1admin, self.testhelper.sub_p1.id)
        self.assertEquals(len(students), 0)

    def test_list(self):
        for num in xrange(2):
            username = "student{0}".format(num)
            student = self.testhelper.create_user(username)
            student.email = username + '@example.com'
            student.devilryuserprofile.full_name = 'User {0}'.format(num)
            student.save()
            student.devilryuserprofile.save()
            self.testhelper.sub_p1.relatedstudent_set.create(user=student,
                                                             tags='group1,group2',
                                                             candidate_id=str(num))
        students = RelatedStudentDao().list(self.testhelper.p1admin, self.testhelper.sub_p1.id)
        self.assertEquals(len(students), 2)
        first, second = students
        self.assertEquals(first['user__username'], 'student0')
        self.assertEquals(first['user__devilryuserprofile__full_name'] , 'User 0')
        self.assertEquals(first['candidate_id'], '0')
        self.assertEquals(first['tags'], 'group1,group2')
        self.assertEquals(second['user__username'], 'student1')

    def test_list_superadmin(self):
        # Just make it does not fail, since this is the only difference from any other admin
        RelatedStudentDao().list(self.testhelper.superuser, self.testhelper.sub_p2.id)

    def test_list_nonadmin(self):
        with self.assertRaises(PermissionDeniedError):
            # p1admin is not admin on p2
            students = RelatedStudentDao().list(self.testhelper.p1admin,
                                                self.testhelper.sub_p2.id)
