import json

from django.contrib import admin
from django.utils.html import format_html

from devilry.devilry_qualifiesforexam.models import (
    DraftQualifiesForFinalExam,
    DraftStatus,
    QualifiesForFinalExam,
    Status,
)


class QualifiesForFinalExamInline(admin.TabularInline):
    model = QualifiesForFinalExam
    raw_id_fields = ["relatedstudent"]
    fields = ["relatedstudent", "qualifies"]
    readonly_fields = ["relatedstudent", "qualifies"]
    extra = 0


class StatusAdmin(admin.ModelAdmin):
    raw_id_fields = ["period"]
    inlines = [QualifiesForFinalExamInline]
    list_display = (
        "id",
        "period",
        "get_status_text",
        "createtime",
        "message",
    )
    search_fields = [
        "id",
        "period__short_name",
        "period__long_name",
        "period__parentnode__short_name",
        "period__parentnode__long_name",
        "message",
    ]
    readonly_fields = ["period", "createtime", "message", "user", "plugin", "exported_timestamp", "status"]

    def get_queryset(self, request):
        return super(StatusAdmin, self).get_queryset(request).select_related("period", "period__parentnode")


admin.site.register(Status, StatusAdmin)


class QualifiesForFinalExamAdmin(admin.ModelAdmin):
    raw_id_fields = ["relatedstudent"]
    list_display = ("id", "qualifies")
    search_fields = ["id"]


admin.site.register(QualifiesForFinalExam, QualifiesForFinalExamAdmin)


class DraftQualifiesForFinalExamInline(admin.TabularInline):
    model = DraftQualifiesForFinalExam
    raw_id_fields = ["relatedstudent"]
    readonly_fields = ["relatedstudent", "qualifies"]
    extra = 0


class DraftStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ["period", "created_by"]
    inlines = [DraftQualifiesForFinalExamInline]
    list_display = (
        "id",
        "period",
        "created_datetime",
        "processing_started_datetime",
        "processing_completed_datetime",
        "processing_status",
    )
    search_fields = [
        "id",
        "period__short_name",
        "period__long_name",
        "period__parentnode__short_name",
        "period__parentnode__long_name",
    ]
    readonly_fields = [
        "created_datetime",
        "created_by",
        "period",
        "plugin",
        "plugin_data",
        "processing_started_datetime",
        "processing_completed_datetime",
        "processing_status",
        "processing_status_data",
        "get_processing_status_pretty"
    ]

    @admin.display(description="Summary json")
    def get_processing_status_pretty(self, obj):
        return format_html("<pre>{}</pre>", json.dumps(obj.processing_status_data, indent=2, sort_keys=True))

    def get_queryset(self, request):
        return super(DraftStatusAdmin, self).get_queryset(request).select_related("period", "period__parentnode")


admin.site.register(DraftStatus, DraftStatusAdmin)


class DraftQualifiesForFinalExamAdmin(admin.ModelAdmin):
    raw_id_fields = ["relatedstudent"]
    list_display = ("id", "relatedstudent__user__shortname", "qualifies")
    search_fields = ["id"]


admin.site.register(DraftQualifiesForFinalExam, DraftQualifiesForFinalExamAdmin)
