from django.test import TestCase

from devilry.devilry_admin.tests.common import admins_common_testmixins
from devilry.devilry_admin.views.node import admins
from devilry.project.develop.testhelpers.corebuilder import NodeBuilder


class TestAdminsListView(TestCase, admins_common_testmixins.AdminsListViewTestMixin):
    builderclass = NodeBuilder
    viewclass = admins.AdminsListView


class TestRemoveAdminView(TestCase, admins_common_testmixins.RemoveAdminViewTestMixin):
    builderclass = NodeBuilder
    viewclass = admins.RemoveAdminView


class TestAdminUserSelectView(TestCase, admins_common_testmixins.AdminUserSelectViewTestMixin):
    builderclass = NodeBuilder
    viewclass = admins.AdminUserSelectView


class TestAddAdminView(TestCase, admins_common_testmixins.AddAdminViewTestMixin):
    builderclass = NodeBuilder
    viewclass = admins.AddAdminView
    cradmin_instance_id = 'devilry_admin_nodeadmin'
