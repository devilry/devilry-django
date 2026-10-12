from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata


class GenericTokenWithMetadataAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "content_object",
        "app",
        "created_datetime",
        "expiration_datetime",
        "expiration_naturaltime",
    )
    search_fields = (
        "app",
        "user__email",
        "token",
    )
    list_filter = (
        "app",
        "created_datetime",
        "expiration_datetime",
    )
    readonly_fields = (
        "token",
        "content_type",
        "single_use",
        "metadata_json",
        "object_id",
        "app",
        "created_datetime",
    )
    ordering = ["-created_datetime"]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(GenericTokenWithMetadataAdmin, self).get_queryset(request)
        else:
            return GenericTokenWithMetadata.objects.none()

    def expiration_naturaltime(self, obj):
        return naturaltime(obj.expiration_datetime)

    expiration_naturaltime.short_description = "Expires"
    expiration_naturaltime.admin_order_field = "expiration_datetime"


admin.site.register(GenericTokenWithMetadata, GenericTokenWithMetadataAdmin)
