import mock
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment.passed_previous_period import passed_previous_semester_manual
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy


class TestPassAssignmentGroupsView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_semester_manual.PassAssignmentGroupsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()
