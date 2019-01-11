from django.contrib import admin

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


admin.site.register(DevilryReport, DevilryReportAdmin)
