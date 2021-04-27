# -*- coding: utf-8 -*-


import logging
import traceback
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ievv_opensource.utils import choices_with_meta

from devilry.devilry_report import generator_registry


logger = logging.getLogger(__name__)


class DevilryReport(models.Model):
    """
    A model representing a report of various data, e.g complete user report.

    The model is designed for being updated asynchronously with a continuously
    updated status while generating a report. Of course, the a report can also be generated synchronously,
    but usually the report generators will perform time-consuming tasks.

    Report data is stored as binary data, and is always generated for a specific user.
    """

    #: The user(`AUTH_USER_MODEL`) that generated the report.
    generated_by_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    #: The datetime the report was generated. Defaults to timezone.now
    created_datetime = models.DateTimeField(
        null=False, blank=False,
        default=timezone.now
    )

    #: When the report generation was started.
    started_datetime = models.DateTimeField(
        null=True, blank=True,
        default=None
    )

    #: When the report generation was finished.
    finished_datetime = models.DateTimeField(
        null=True, blank=True,
        default=None
    )

    #: The generator type.
    #:
    #: This is specified in a subclass
    #: of :class:`devilry.devilry_report.abstract_generator.AbstractReportGenerator`.
    generator_type = models.CharField(
        null=False, blank=False, max_length=255
    )

    #: JSON-field for generator options that are specific to the ``generator_type``.
    #:
    #: If the generator
    generator_options = models.JSONField(null=False, blank=True, default=dict)

    #: Supported status types.
    STATUS_CHOICES = choices_with_meta.ChoicesWithMeta(
        choices_with_meta.Choice(value='unprocessed'),
        choices_with_meta.Choice(value='generating'),
        choices_with_meta.Choice(value='success'),
        choices_with_meta.Choice(value='error'),
    )

    #: The current status of the report.
    #:
    #: - `unprocessed`: The report generation has not started yet.
    #: - `generating`: Report data is being generated.
    #: - `success`: The report was successfully generated.
    #: - `error`: Something happened during report generation. Data will be available in the ``status_data``-field.
    status = models.CharField(
        null=False, blank=False,
        max_length=255,
        choices=STATUS_CHOICES.iter_as_django_choices_short(),
        default=STATUS_CHOICES.UNPROCESSED.value
    )

    #: The status data of the report generation. Usually only contains data when the some error occurred
    #: during report generation.
    status_data = models.JSONField(
        null=False, blank=True,
        default=dict
    )

    #: Name of the generated file with results.
    output_filename = models.CharField(
        null=True, blank=True,
        max_length=255,
        default=''
    )

    #: Content-type used when creating a download-request.
    content_type = models.CharField(
        null=True, blank=True,
        max_length=255,
        default=''
    )

    #: The complete report stored as binary data.
    result = models.BinaryField()

    def __str__(self):
        return '#{}-{}-{}'.format(
            self.id, self.generator_type, self.status)

    def clean_generator_options(self):
        if len(self.generator_options) == 0:
            return
        generator = self.generator(devilry_report=self)
        generator.validate()

    def clean(self):
        self.clean_generator_options()

    @property
    def generator(self):
        """
        Fetch generator from the generator registry based on the
        ``generator_type`` field.
        Returns:
            AbstractReportGenerator: Subclass.
        """
        return generator_registry.Registry.get_instance().get(generator_type=self.generator_type)

    def generate(self):
        """
        Typically called within RQ task
          - Sets started_datetime to NOW
          - Sets status="generating"
          - Calls self.generator.generate() - on completion:
            - If no exception - set status="success"
            - If exception - save traceback in status_data and set status="error"
            - Set finished_datetime
        """
        self.started_datetime = timezone.now()
        self.status = self.STATUS_CHOICES.GENERATING.value
        self.full_clean()
        self.save()

        generator = self.generator(devilry_report=self)
        file_like_obj = BytesIO()
        try:
            generator.generate(file_like_object=file_like_obj)
        except Exception as exception:
            self.status = self.STATUS_CHOICES.ERROR.value
            self.status_data = {
                'error_message': str(exception),
                'exception_traceback': traceback.format_exc()
            }
            logger.exception('Failed to generate DevilryReport#{}'.format(self.id))
        else:
            self.result = file_like_obj.getvalue()
            self.finished_datetime = timezone.now()
            self.content_type = generator.get_content_type()
            self.output_filename = '{}-{}.{}'.format(
                generator.get_output_filename_prefix(),
                self.finished_datetime.strftime('%d%m%Y-%H%M%S'),
                generator.get_output_file_extension()
            )
            self.status = self.STATUS_CHOICES.SUCCESS.value
        self.full_clean()
        self.save()
