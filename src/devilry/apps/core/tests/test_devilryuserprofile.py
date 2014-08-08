from django.test import TestCase
from ..testhelper import TestHelper
from ..models.devilryuserprofile import user_is_admin
from ..models.devilryuserprofile import user_is_admin_or_superadmin
from ..models.devilryuserprofile import user_is_nodeadmin
from ..models.devilryuserprofile import user_is_subjectadmin
from ..models.devilryuserprofile import user_is_periodadmin
from ..models.devilryuserprofile import user_is_assignmentadmin
from ..models.devilryuserprofile import user_is_examiner
from ..models.devilryuserprofile import user_is_student



class TestUserHasRole(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes="uni:admin(uniadmin)",
                            subjects=["sub:admin(subadmin)"],
                            periods=["p1:admin(p1admin):begins(-2):ends(6)"],
                            assignments=["a1:admin(a1admin)"])
        self.testhelper.create_superuser('grandma')
        self.testhelper.create_user('notadmin')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:examiner(examiner1):candidate(student1)')

    def test_user_is_nodeadmin(self):
        self.assertTrue(user_is_nodeadmin(self.testhelper.uniadmin))
        self.assertFalse(user_is_nodeadmin(self.testhelper.subadmin))
        self.assertFalse(user_is_nodeadmin(self.testhelper.p1admin))
        self.assertFalse(user_is_nodeadmin(self.testhelper.a1admin))
        self.assertFalse(user_is_nodeadmin(self.testhelper.notadmin))
        self.assertFalse(user_is_nodeadmin(self.testhelper.grandma))
        self.assertFalse(user_is_nodeadmin(self.testhelper.student1))
        self.assertFalse(user_is_nodeadmin(self.testhelper.examiner1))

    def test_user_is_subjectadmin(self):
        self.assertFalse(user_is_subjectadmin(self.testhelper.uniadmin))
        self.assertTrue(user_is_subjectadmin(self.testhelper.subadmin))
        self.assertFalse(user_is_subjectadmin(self.testhelper.p1admin))
        self.assertFalse(user_is_subjectadmin(self.testhelper.a1admin))
        self.assertFalse(user_is_subjectadmin(self.testhelper.notadmin))
        self.assertFalse(user_is_subjectadmin(self.testhelper.grandma))
        self.assertFalse(user_is_subjectadmin(self.testhelper.student1))
        self.assertFalse(user_is_subjectadmin(self.testhelper.examiner1))

    def test_user_is_periodadmin(self):
        self.assertFalse(user_is_periodadmin(self.testhelper.uniadmin))
        self.assertFalse(user_is_periodadmin(self.testhelper.subadmin))
        self.assertTrue(user_is_periodadmin(self.testhelper.p1admin))
        self.assertFalse(user_is_periodadmin(self.testhelper.a1admin))
        self.assertFalse(user_is_periodadmin(self.testhelper.notadmin))
        self.assertFalse(user_is_periodadmin(self.testhelper.grandma))
        self.assertFalse(user_is_periodadmin(self.testhelper.student1))
        self.assertFalse(user_is_periodadmin(self.testhelper.examiner1))

    def test_user_is_assignmentadmin(self):
        self.assertFalse(user_is_assignmentadmin(self.testhelper.uniadmin))
        self.assertFalse(user_is_assignmentadmin(self.testhelper.subadmin))
        self.assertFalse(user_is_assignmentadmin(self.testhelper.p1admin))
        self.assertTrue(user_is_assignmentadmin(self.testhelper.a1admin))
        self.assertFalse(user_is_assignmentadmin(self.testhelper.notadmin))
        self.assertFalse(user_is_assignmentadmin(self.testhelper.grandma))
        self.assertFalse(user_is_assignmentadmin(self.testhelper.student1))
        self.assertFalse(user_is_assignmentadmin(self.testhelper.examiner1))

    def test_user_is_admin(self):
        self.assertTrue(user_is_admin(self.testhelper.uniadmin))
        self.assertTrue(user_is_admin(self.testhelper.subadmin))
        self.assertTrue(user_is_admin(self.testhelper.p1admin))
        self.assertTrue(user_is_admin(self.testhelper.a1admin))
        self.assertFalse(user_is_admin(self.testhelper.notadmin))
        self.assertFalse(user_is_admin(self.testhelper.grandma))
        self.assertFalse(user_is_admin(self.testhelper.student1))
        self.assertFalse(user_is_admin(self.testhelper.examiner1))

    def test_user_is_admin_or_superadmin(self):
        self.assertTrue(user_is_admin_or_superadmin(self.testhelper.uniadmin))
        self.assertTrue(user_is_admin_or_superadmin(self.testhelper.subadmin))
        self.assertTrue(user_is_admin_or_superadmin(self.testhelper.p1admin))
        self.assertTrue(user_is_admin_or_superadmin(self.testhelper.a1admin))
        self.assertFalse(user_is_admin_or_superadmin(self.testhelper.notadmin))
        self.assertTrue(user_is_admin_or_superadmin(self.testhelper.grandma))
        self.assertFalse(user_is_admin_or_superadmin(self.testhelper.student1))
        self.assertFalse(user_is_admin_or_superadmin(self.testhelper.examiner1))

    def test_user_is_student(self):
        self.assertFalse(user_is_student(self.testhelper.uniadmin))
        self.assertFalse(user_is_student(self.testhelper.subadmin))
        self.assertFalse(user_is_student(self.testhelper.p1admin))
        self.assertFalse(user_is_student(self.testhelper.a1admin))
        self.assertFalse(user_is_student(self.testhelper.notadmin))
        self.assertFalse(user_is_student(self.testhelper.grandma))
        self.assertTrue(user_is_student(self.testhelper.student1))
        self.assertFalse(user_is_student(self.testhelper.examiner1))

    def test_user_is_examiner(self):
        self.assertFalse(user_is_examiner(self.testhelper.uniadmin))
        self.assertFalse(user_is_examiner(self.testhelper.subadmin))
        self.assertFalse(user_is_examiner(self.testhelper.p1admin))
        self.assertFalse(user_is_examiner(self.testhelper.a1admin))
        self.assertFalse(user_is_examiner(self.testhelper.notadmin))
        self.assertFalse(user_is_examiner(self.testhelper.grandma))
        self.assertFalse(user_is_examiner(self.testhelper.student1))
        self.assertTrue(user_is_examiner(self.testhelper.examiner1))
