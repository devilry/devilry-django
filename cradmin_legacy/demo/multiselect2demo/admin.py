from django.contrib import admin
from cradmin_legacy.demo.multiselect2demo.models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("site")


admin.site.register(Product, ProductAdmin)
