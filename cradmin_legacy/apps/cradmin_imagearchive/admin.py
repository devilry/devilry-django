from django.contrib import admin
from django.template import defaultfilters

from cradmin_legacy.apps.cradmin_imagearchive.models import ArchiveImage


class ArchiveImageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "description",
        "role",
        "image_width",
        "image_height",
        "get_size",
        "get_url",
    ]
    list_display_links = [
        "id",
        "name",
    ]

    search_fields = [
        "id",
        "name",
        "description",
    ]

    readonly_fields = [
        "image_width",
        "image_height",
        "file_extension",
    ]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        else:
            return ArchiveImage.objects.none()

    def get_size(self, obj):
        if obj.file_size:
            return defaultfilters.filesizeformat(obj.file_size)
        else:
            return None

    get_size.short_description = "Size"
    get_size.admin_order_field = "file_size"

    def get_url(self, obj):
        return '<a href="{url}" target="_blank">{label}</a>'.format(label="Show image", url=obj.image.url)

    get_url.short_description = "Open"
    get_url.allow_tags = True


admin.site.register(ArchiveImage, ArchiveImageAdmin)
