from django.contrib import admin

import json
from django.utils.html import format_html

from devilry.devilry_report.models import DevilryReport


class DevilryReportAdmin(admin.ModelAdmin):
    raw_id_fields = [
        'generated_by_user'
    ]

    list_display = [
        'id',
        'generated_by_user',
        'status',
        'created_datetime',
        'started_datetime',
        'finished_datetime',
        'generator_type'
    ]

    list_filter = [
        'status',
        'started_datetime',
        'finished_datetime',
        'generator_type'
    ]

    search_fields = [
        'generated_by_user__id',
        'generated_by_user__fullname'
    ]

    exclude = [
        'status_data',
        'generator_options'
    ]

    readonly_fields = [
        'generated_by_user',
        'status',
        'get_status_data_pretty',
        'created_datetime',
        'started_datetime',
        'finished_datetime',
        'generator_type',
        'get_generator_options_pretty',
        'output_filename',
        'content_type'
    ]

    def get_status_data_pretty(self, obj):
        return format_html('<pre>{}</pre>', json.dumps(obj.status_data, indent=2, sort_keys=True))
    get_status_data_pretty.short_description = 'Status data'

    def get_generator_options_pretty(self, obj):
        return format_html('<pre>{}</pre>', json.dumps(obj.generator_options, indent=2, sort_keys=True))
    get_generator_options_pretty.short_description = 'Generator options'


admin.site.register(DevilryReport, DevilryReportAdmin)
