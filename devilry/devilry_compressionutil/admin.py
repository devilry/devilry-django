from django.contrib import admin

from devilry.devilry_compressionutil.models import CompressedArchiveMeta


@admin.register(CompressedArchiveMeta)
class CompressedArchiveMeta(admin.ModelAdmin):
    list_per_page = 20

    list_display =[
        'id',
        'content_object_id',
        'content_type',
        'content_object',
        'created_by',
        'created_datetime',
        'archive_name',
        'archive_path',
        'archive_size',
        'deleted_datetime'
    ]

    readonly_fields = [
        'content_object_id',
        'content_type',
        'content_object',
        'created_by',
        'created_by_role',
        'created_datetime',
        'archive_name',
        'archive_path',
        'archive_size',
        'deleted_datetime'
    ]

    list_filter = [
        'id',
        'content_object_id',
        'content_type'
    ]

    search_fields = [
        'content_object_id',
        'content_type__app_label',
        'content_type__model'
    ]
