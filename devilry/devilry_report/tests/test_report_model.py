# -*- coding: utf-8 -*-


import io

import mock
from django import test

from model_bakery import baker

from devilry.devilry_report import abstract_generator
from devilry.devilry_report.models import DevilryReport


class Generator(abstract_generator.AbstractReportGenerator):
    @classmethod
    def get_generator_type(cls):
        return 'test-generator'

    def get_output_file_extension(self):
        return 'txt'

    def get_content_type(self):
        return 'text/plain'

    def generate(self, file_like_object):
        file_like_object.write(b'Test content')


class FailingGenerator(abstract_generator.AbstractReportGenerator):
    @classmethod
    def get_generator_type(cls):
        return 'failing-test-generator'

    def get_output_file_extension(self):
        return 'txt'

    def get_content_type(self):
        return 'text/plain'

    def generate(self, file_like_object):
        raise ValueError('Some error!')


class TestDevilryReport(test.TestCase):
    def test_generate_status_error(self):
        with mock.patch.object(DevilryReport, 'generator', FailingGenerator):
            devilry_report = baker.make('devilry_report.DevilryReport',
                                        generator_type=FailingGenerator.get_generator_type())
            devilry_report.generate()
            devilry_report.refresh_from_db()
            self.assertEqual(devilry_report.status, DevilryReport.STATUS_CHOICES.ERROR.value)

    def test_generate_status_data_error(self):
        with mock.patch.object(DevilryReport, 'generator', FailingGenerator):
            devilry_report = baker.make('devilry_report.DevilryReport',
                                        generator_type=FailingGenerator.get_generator_type())
            devilry_report.generate()
            devilry_report.refresh_from_db()
            self.assertEqual(devilry_report.status_data['error_message'], 'Some error!')

    def test_generate_error_fields_not_set(self):
        with mock.patch.object(DevilryReport, 'generator', FailingGenerator):
            devilry_report = baker.make('devilry_report.DevilryReport',
                                        generator_type=FailingGenerator.get_generator_type())
            devilry_report.generate()
            devilry_report.refresh_from_db()
            self.assertEqual(devilry_report.status, DevilryReport.STATUS_CHOICES.ERROR.value)
            self.assertIsNone(devilry_report.finished_datetime)
            self.assertEqual(devilry_report.content_type, '')
            self.assertEqual(devilry_report.output_filename, '')

    def test_generator_success(self):
        with mock.patch.object(DevilryReport, 'generator', Generator):
            devilry_report = baker.make('devilry_report.DevilryReport',
                                        generator_type=Generator.get_generator_type())
            devilry_report.generate()
            devilry_report.refresh_from_db()
            self.assertEqual(devilry_report.status, DevilryReport.STATUS_CHOICES.SUCCESS.value)
            self.assertIsNotNone(devilry_report.finished_datetime)
            self.assertEqual(devilry_report.content_type, 'text/plain')
            self.assertEqual(
                devilry_report.output_filename,
                'report-{}.txt'.format(devilry_report.finished_datetime.strftime('%d%m%Y-%H%M%S')))

    def test_generator_success_content(self):
        with mock.patch.object(DevilryReport, 'generator', Generator):
            devilry_report = baker.make('devilry_report.DevilryReport',
                                        generator_type=Generator.get_generator_type())
            devilry_report.generate()
            devilry_report.refresh_from_db()
            buffer = io.BytesIO()
            buffer.write(devilry_report.result)
            self.assertEqual(buffer.getvalue(), b'Test content')
