from django.contrib import admin
from cradmin_legacy.demo.webdemo.models import Site, Page, PageTag


class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "admins_as_string")

    def admins_as_string(self, obj):
        return ", ".join([user.username for user in obj.admins.all()])

    admins_as_string.short_description = "Admins"


admin.site.register(Site, SiteAdmin)


class PageTagInline(admin.TabularInline):
    model = PageTag
    extra = 0


class PageAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "site",
        "get_tags",
        "get_subscribers",
    ]
    filter_horizontal = ["subscribers"]
    inlines = [PageTagInline]

    def get_tags(self, obj):
        return ", ".join(pagetag.tag for pagetag in obj.tags.all())

    get_tags.short_description = "Tags"

    def get_subscribers(self, obj):
        return ", ".join(str(subscriber) for subscriber in obj.subscribers.all())

    get_subscribers.short_description = "Subscribers"

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("site").prefetch_related("tags", "subscribers")
        )


admin.site.register(Page, PageAdmin)
