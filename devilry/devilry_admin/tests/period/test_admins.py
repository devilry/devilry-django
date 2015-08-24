from django.test import TestCase

from devilry.devilry_admin.tests.common import admins_common_testmixins
from devilry.devilry_admin.views.period import admins
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder


class TestAdminsListView(TestCase, admins_common_testmixins.AdminsListViewTestMixin):
    builderclass = PeriodBuilder
    viewclass = admins.AdminsListView


class TestRemoveAdminView(TestCase, admins_common_testmixins.RemoveAdminViewTestMixin):
    builderclass = PeriodBuilder
    viewclass = admins.RemoveAdminView


class TestAdminUserSelectView(TestCase, admins_common_testmixins.AdminUserSelectViewTestMixin):
    builderclass = PeriodBuilder
    viewclass = admins.AdminUserSelectView


class TestAddAdminView(TestCase, admins_common_testmixins.AddAdminViewTestMixin):
    builderclass = PeriodBuilder
    viewclass = admins.AddAdminView
    cradmin_instance_id = 'devilry_admin_periodadmin'
