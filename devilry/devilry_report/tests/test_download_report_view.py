# -*- coding: utf-8 -*-


import json

import mock
from django import test
from django.conf import settings
from django.http import Http404

from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_report.models import DevilryReport
from devilry.devilry_report.views import download_report
from devilry.devilry_report import abstract_generator


class TestGenerator(abstract_generator.AbstractReportGenerator):

    @classmethod
    def get_generator_type(cls):
        return 'test-generator'

    def get_output_file_extension(self):
        return 'txt'

    def get_content_type(self):
        return 'text/plain'

    def generate(self, file_like_object):
        file_like_object.write(b'Test content')


class TestAllResultsDownload(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = download_report.DownloadReportView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def make_assignment(self, period, **assignment_kwargs):
        return baker.make('core.Assignment', parentnode=period, **assignment_kwargs)

    def make_relatedstudent(self, period, **relatedstudent_kwargs):
        return baker.make('core.RelatedStudent', period=period, **relatedstudent_kwargs)

    def make_group_for_student(self, assignment, relatedstudent):
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Candidate', assignment_group=group, relatedstudent=relatedstudent)
        return group

    def test_post_ok_sanity(self):
        with mock.patch.object(DevilryReport, 'generator', TestGenerator):
            self.mock_http302_postrequest(
                requestkwargs={
                    'data': {
                        'report_options': json.dumps({
                            'generator_type': 'semesterstudentresults',
                            'generator_options': {}
                        })
                    }})
            self.assertEqual(DevilryReport.objects.count(), 1)
            self.assertEqual(DevilryReport.objects.get().status, DevilryReport.STATUS_CHOICES.SUCCESS.value)

    def test_get_report_id_missing(self):
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls()

    def test_get_report_does_not_exist(self):
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                requestkwargs={
                    'data': {
                        'report': 1
                    }})

    def test_get_report_not_created_by_requestuser(self):
        reportuser = baker.make(settings.AUTH_USER_MODEL)
        report = baker.make('devilry_report.DevilryReport', generated_by_user=reportuser)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                requestkwargs={
                    'data': {
                        'report': report.id
                    }})

    def test_get_download_generated_report_not_finished(self):
        reportuser = baker.make(settings.AUTH_USER_MODEL)
        report = baker.make('devilry_report.DevilryReport', generated_by_user=reportuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=reportuser,
            requestkwargs={
                'data': {
                    'report': report.id
                }})
        self.assertEqual(
            mockresponse.selector.one('.devilry-report-download-message').alltext_normalized,
            'The download will start automatically as soon as the report is finished.')

    def test_get_download_generated_report(self):
        reportuser = baker.make(settings.AUTH_USER_MODEL)
        with mock.patch.object(DevilryReport, 'generator', TestGenerator):
            report = baker.make('devilry_report.DevilryReport',
                                generated_by_user=reportuser,
                                generator_type='test-generator')
            report.generate()
            mockresponse = self.mock_getrequest(
                requestuser=reportuser,
                requestkwargs={
                    'data': {
                        'report': report.id
                    }})
            self.assertEqual(mockresponse.response.content, b'Test content')
