from django.test import TestCase

from devilry.devilry_admin.tests.common import admins_common_testmixins
from devilry.devilry_admin.views.subject import admins
from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder


class TestAdminsListView(TestCase, admins_common_testmixins.AdminsListViewTestMixin):
    builderclass = SubjectBuilder
    viewclass = admins.AdminsListView


class TestRemoveAdminView(TestCase, admins_common_testmixins.RemoveAdminViewTestMixin):
    builderclass = SubjectBuilder
    viewclass = admins.RemoveAdminView


class TestAdminUserSelectView(TestCase, admins_common_testmixins.AdminUserSelectViewTestMixin):
    builderclass = SubjectBuilder
    viewclass = admins.AdminUserSelectView


class TestAddAdminView(TestCase, admins_common_testmixins.AddAdminViewTestMixin):
    builderclass = SubjectBuilder
    viewclass = admins.AddAdminView
    cradmin_instance_id = 'devilry_admin_subjectadmin'
