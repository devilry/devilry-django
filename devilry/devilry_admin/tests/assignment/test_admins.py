from django.test import TestCase

from devilry.devilry_admin.tests.common import admins_common_testmixins
from devilry.devilry_admin.views.assignment import admins
from devilry.project.develop.testhelpers.corebuilder import AssignmentBuilder


class TestAdminsListView(TestCase, admins_common_testmixins.AdminsListViewTestMixin):
    builderclass = AssignmentBuilder
    viewclass = admins.AdminsListView


class TestRemoveAdminView(TestCase, admins_common_testmixins.RemoveAdminViewTestMixin):
    builderclass = AssignmentBuilder
    viewclass = admins.RemoveAdminView


class TestAdminUserSelectView(TestCase, admins_common_testmixins.AdminUserSelectViewTestMixin):
    builderclass = AssignmentBuilder
    viewclass = admins.AdminUserSelectView


class TestAddAdminView(TestCase, admins_common_testmixins.AddAdminViewTestMixin):
    builderclass = AssignmentBuilder
    viewclass = admins.AddAdminView
    cradmin_instance_id = 'devilry_admin_assignmentadmin'
