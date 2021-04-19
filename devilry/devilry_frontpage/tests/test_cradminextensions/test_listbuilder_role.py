import htmls
import mock
from django import test
from django.conf import settings
from model_bakery import baker

from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_frontpage.cradminextensions.listbuilder import listbuilder_role


class TestStudentRoleItemValue(test.TestCase):
    def test_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.StudentRoleItemValue(value=testuser).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue'))

    def test_correct_devilryrole(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.StudentRoleItemValue(value=testuser).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.StudentRoleItemValue(value=testuser).render())
        self.assertEqual(
            'Student',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.StudentRoleItemValue(value=testuser).render())
        self.assertEqual(
            'Upload deliveries or see your delivery and feedback history.',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestExaminerRoleItemValue(test.TestCase):
    def test_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.ExaminerRoleItemValue(value=testuser).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue'))

    def test_correct_devilryrole(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.ExaminerRoleItemValue(value=testuser).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.ExaminerRoleItemValue(value=testuser).render())
        self.assertEqual(
            'Examiner',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.ExaminerRoleItemValue(value=testuser).render())
        self.assertEqual(
            'Give students feedback on their deliveries as examiner.',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestAnyAdminRoleItemValue(test.TestCase):
    def test_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.AnyAdminRoleItemValue(value=testuser).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue'))

    def test_correct_devilryrole(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.AnyAdminRoleItemValue(value=testuser).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.AnyAdminRoleItemValue(value=testuser).render())
        self.assertEqual(
            'Administrator',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.AnyAdminRoleItemValue(value=testuser).render())
        self.assertEqual(
            'Manage departments, courses, semesters and assignments.',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestStudentRoleItemFrame(test.TestCase):
    def test_sanity(self):
        selector = htmls.S(listbuilder_role.StudentRoleItemFrame(inneritem=mock.MagicMock()).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemframe'))

    def test_correct_devilryrole(self):
        selector = htmls.S(listbuilder_role.StudentRoleItemFrame(inneritem=mock.MagicMock()).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemframe-student'))

    def test_url(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.StudentRoleItemFrame(
            inneritem=mock.MagicMock(value=testuser)).render())
        self.assertEqual(
            '/devilry_student/',
            selector.one('.cradmin-legacy-listbuilder-itemframe-link')['href'])


class TestExaminerRoleItemFrame(test.TestCase):
    def test_sanity(self):
        selector = htmls.S(listbuilder_role.ExaminerRoleItemFrame(inneritem=mock.MagicMock()).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemframe'))

    def test_correct_devilryrole(self):
        selector = htmls.S(listbuilder_role.ExaminerRoleItemFrame(inneritem=mock.MagicMock()).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemframe-examiner'))

    def test_url(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.ExaminerRoleItemFrame(
            inneritem=mock.MagicMock(value=testuser)).render())
        self.assertEqual(
            '/devilry_examiner/',
            selector.one('.cradmin-legacy-listbuilder-itemframe-link')['href'])


class TestAnyAdminRoleItemFrame(test.TestCase):
    def test_sanity(self):
        selector = htmls.S(listbuilder_role.AnyAdminRoleItemFrame(inneritem=mock.MagicMock()).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemframe'))

    def test_correct_devilryrole(self):
        selector = htmls.S(listbuilder_role.AnyAdminRoleItemFrame(inneritem=mock.MagicMock()).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemframe-anyadmin'))

    def test_url(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        selector = htmls.S(listbuilder_role.AnyAdminRoleItemFrame(
            inneritem=mock.MagicMock(value=testuser)).render())
        self.assertEqual(
            '/devilry_admin/',
            selector.one('.cradmin-legacy-listbuilder-itemframe-link')['href'])


class TestRoleSelectList(test.TestCase):
    def test_user_is_student(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        selector = htmls.S(listbuilder_role.RoleSelectList(user=testuser).render())
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))

    def test_user_is_examiner(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        selector = htmls.S(listbuilder_role.RoleSelectList(user=testuser).render())
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))

    def test_user_is_superuser(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        selector = htmls.S(listbuilder_role.RoleSelectList(user=testuser).render())
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))

    def test_user_is_departmentadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make(
                       'devilry_account.SubjectPermissionGroup',
                       permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN).permissiongroup)
        selector = htmls.S(listbuilder_role.RoleSelectList(user=testuser).render())
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))

    def test_user_is_subjectadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make(
                       'devilry_account.SubjectPermissionGroup',
                       permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN).permissiongroup)
        selector = htmls.S(listbuilder_role.RoleSelectList(user=testuser).render())
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))

    def test_user_is_periodadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make('devilry_account.PeriodPermissionGroup').permissiongroup)
        selector = htmls.S(listbuilder_role.RoleSelectList(user=testuser).render())
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertTrue(
            selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))
