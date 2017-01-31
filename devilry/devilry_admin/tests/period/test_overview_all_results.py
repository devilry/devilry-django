# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import test

from model_mommy import mommy
import mock

from django_cradmin import cradmin_testhelpers

from devilry.devilry_admin.views.period import overview_all_results
from devilry.devilry_dbcache import customsql
from devilry.project.common import settings


class TestOverviewAllResults(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview_all_results.RelatedStudentsAllResultsOverview

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEquals('All students results', mockresponse.selector.one('title').alltext_normalized)

    def test_table_class(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertTrue(mockresponse.selector.one('.devilry-tabulardata-list'))

    def test_table_no_students(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-tabulardata-list'))
        self.assertEquals(
            'No students on period',
            mockresponse.selector.one('.django-cradmin-listbuilderview-no-items-message').alltext_normalized)
