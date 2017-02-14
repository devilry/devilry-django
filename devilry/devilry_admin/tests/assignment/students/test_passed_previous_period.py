import mock
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import AssignmentGroup, Candidate, Assignment
from devilry.devilry_admin.views.assignment.students import passed_previous_period
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestPassedPreviousAnonymization(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_period.SelectPeriodView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_anonymizationmode_fully_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_404_anonymizationmode_fully_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_404_anonymizationmode_fully_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_anonymizationmode_semi_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_semi_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_404_anonymizationmode_semi_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_anonymizationmode_off_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_off_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_anonymizationmode_off_period(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))
