import typing

from django.contrib import admin

from cradmin_legacy.apps.cradmin_temporaryfileuploadstore.models import TemporaryFile, TemporaryFileCollection
from cradmin_legacy.utils.settingsutils import cradmin_legacy_djangoadmin_user_search_fields

if typing.TYPE_CHECKING:
    from django.http.request import HttpRequest


class TemporaryFileInline(admin.StackedInline):
    fields = ["filename", "file"]
    readonly_fields = ["filename", "file"]
    model = TemporaryFile
    extra = 0


class TemporaryFileCollectionAdmin(admin.ModelAdmin):
    inlines = [TemporaryFileInline]
    list_display = (
        "id",
        "user",
        "created_datetime",
        "minutes_to_live",
    )
    readonly_fields = ["singlemode", "user", "accept", "created_datetime", "unique_filenames", "max_filename_length"]
    search_fields = [
        "=id",
    ]
    date_hierarchy = "created_datetime"

    def get_search_fields(self, request: "HttpRequest") -> list[str]:
        user_search_fields = cradmin_legacy_djangoadmin_user_search_fields(lookup="user__")
        return super().get_search_fields(request) + user_search_fields

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        else:
            return TemporaryFile.objects.none()


admin.site.register(TemporaryFileCollection, TemporaryFileCollectionAdmin)
